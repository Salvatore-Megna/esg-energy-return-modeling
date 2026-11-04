"""ESG Energy (2013–2024): audited reimplementation of the historic two-layer study.

This module makes NO claim that the historical Random Forest scores survive a purged
12-month-ahead evaluation. Original notebook and data are linked in README.
All numeric outputs in outputs/ require authentic inputs, not synthetic records.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, r2_score

USA_HIGH = ("NEE", "XEL", "DUK")
USA_LOW = ("XOM", "CVX", "OXY")
EU_HIGH = ("ENEL.MI", "IBE.MC", "EOAN.DE")
EU_LOW = ("TTE.PA", "BP.L", "ENI.MI")
TICKERS = USA_HIGH + USA_LOW + EU_HIGH + EU_LOW
PERIODS = ("pre_trump", "trump", "biden")
FEATURES = ("E_lag1", "S_lag1", "G_lag1", "ESG_lag1")
MAP_ESG_TO_TICKER = {
    "NEE-US": "NEE", "XEL-US": "XEL", "DUK-US": "DUK",
    "XOM-US": "XOM", "CVX-US": "CVX", "OXY-US": "OXY",
    "ENEL-IT": "ENEL.MI", "IBE-ES": "IBE.MC", "EOAN-DE": "EOAN.DE",
    "TTE-FR": "TTE.PA", "BP-GB": "BP.L", "ENI-IT": "ENI.MI",
}


def month_end(values: pd.Series) -> pd.Series:
    return pd.to_datetime(values).dt.to_period("M").dt.to_timestamp("M")


def month_num(values: pd.Series) -> pd.Series:
    return values.dt.year * 12 + values.dt.month


def read_prices(path: Path) -> pd.DataFrame:
    # Original: price, not independently verified as dividend-adjusted total return.
    p = pd.read_csv(path)
    required = {"date", "ticker", "price"}
    if not required.issubset(p):
        raise ValueError(f"Prices: missing {required.difference(p)}")
    p = p[p["ticker"].isin(TICKERS)].copy()
    p["date"] = month_end(p["date"])
    p["price"] = pd.to_numeric(p["price"], errors="raise")
    if not np.isfinite(p["price"]).all() or (p["price"] <= 0).any():
        raise ValueError("Prices must be positive and finite")
    # Keep last record in ORIGINAL file order within a ticker-month.
    p = p.drop_duplicates(["ticker", "date"], keep="last")
    p = p.sort_values(["ticker", "date"]).reset_index(drop=True)
    p["previous_date"] = p.groupby("ticker")["date"].shift(1)
    p["r_stock"] = p.groupby("ticker")["price"].pct_change(fill_method=None)
    adjacent = (month_num(p["date"]) - month_num(p["previous_date"]) == 1)
    # Do not silently treat a return across a missing calendar month as monthly.
    return p.loc[adjacent, ["ticker", "date", "r_stock"]].copy()


def read_benchmarks(path: Path) -> pd.DataFrame:
    b = pd.read_csv(path)
    if not {"date", "bm_USA", "bm_EU"}.issubset(b):
        raise ValueError("Benchmark CSV must have date,bm_USA,bm_EU")
    b["date"] = month_end(b["date"])
    if b["date"].duplicated().any():
        raise ValueError("Duplicate benchmark months")
    b[["bm_USA", "bm_EU"]] = b[["bm_USA", "bm_EU"]].apply(pd.to_numeric, errors="raise")
    return b


def read_esg(path: Path) -> pd.DataFrame:
    # IMPORTANT: follows FIRST SHEET of the historical GitHub notebook, not
    # the later, incompatible wide multi-sheet notebook.
    e = pd.read_excel(path, sheet_name=0)
    original_cols = ("Date", "Ticker", "ESG-E SCORE", "ESG-S SCORE",
                     "ESG-G SCORE", "ESG TOT SCORE")
    if not set(original_cols).issubset(e):
        raise ValueError(f"Historical ESG Excel schema not confirmed: {list(e.columns)}")
    dates = pd.to_datetime(e["Date"], format="%m/%y", errors="coerce")
    if dates.isna().any():
        raise ValueError("Date must follow original m/yy schema: investigate source")
    e["date"] = month_end(dates)
    e["ticker"] = e["Ticker"].map(MAP_ESG_TO_TICKER)
    e = e[e["ticker"].notna()].copy()
    if e.duplicated(["ticker", "date"]).any():
        raise ValueError("Duplicate ESG rows for same ticker-month")
    e = e.sort_values(["ticker", "date"])
    new_cols = ("E_lag1", "S_lag1", "G_lag1", "ESG_lag1")
    for old, new in zip(original_cols[2:], new_cols):
        e[old] = pd.to_numeric(e[old], errors="coerce")
        e[new] = e.groupby("ticker")[old].shift(1)
    before_date = e.groupby("ticker")["date"].shift(1)
    adjacent = (month_num(e["date"]) - month_num(before_date) == 1)
    return e.loc[adjacent, ["ticker", "date", *new_cols]].dropna().copy()


def period_of(dates: pd.Series) -> pd.Series:
    return pd.Series(np.select(
        [dates.between("2013-01-01", "2016-12-31"),
         dates.between("2017-01-01", "2020-12-31"),
         dates.between("2021-01-01", "2024-12-31")],
        PERIODS, default="outside"), index=dates.index)


def prepare_panel(prices: pd.DataFrame, benchmarks: pd.DataFrame, esg: pd.DataFrame) -> pd.DataFrame:
    x = prices.merge(benchmarks, on="date", validate="many_to_one")
    x = x.merge(esg, on=["ticker", "date"], validate="one_to_one")
    x["area"] = np.where(x.ticker.isin(USA_HIGH + USA_LOW), "USA", "EU")
    x["esg_class"] = np.where(x.ticker.isin(USA_HIGH + EU_HIGH), "High", "Low")
    x["r_sector"] = np.where(x.area.eq("USA"), x.bm_USA, x.bm_EU)
    x["r_rel"] = x.r_stock - x.r_sector
    x["periodo"] = period_of(x.date)
    x = x.loc[x.periodo.ne("outside")].copy()
    if x.duplicated(["ticker", "date"]).any():
        raise ValueError("Duplicate company-month after joins")
    if x[list(FEATURES) + ["r_rel"]].isna().any().any():
        raise ValueError("Missing model features or relative returns")
    return x.sort_values(["ticker", "date"]).reset_index(drop=True)


def forward_12m_by_period(panel: pd.DataFrame) -> pd.DataFrame:
    """Sum 12 subsequent SIMPLE excess returns, as in the original notebook.

    Targets cannot cross a period boundary and must have 12 consecutive months.
    """
    x = panel.sort_values(["ticker", "periodo", "date"]).copy()
    grouped = x.groupby(["ticker", "periodo"], sort=False)
    x["target_end"] = grouped["date"].shift(-12)
    x["r_rel_12m_fwd"] = sum(grouped["r_rel"].shift(-k) for k in range(1, 13))
    contiguous = month_num(x["target_end"]) - month_num(x["date"]) == 12
    # Ensure ALL intermediate target points exist; 12-month endpoint alone
    # is insufficient in irregular panels. Use an explicit calendar-month check.
    for k in range(1, 13):
        future_date = grouped["date"].shift(-k)
        contiguous &= (month_num(future_date) - month_num(x["date"]) == k)
    return x.loc[contiguous & x["r_rel_12m_fwd"].notna()].copy()


def purged_holdout(frame: pd.DataFrame, horizon: int = 12, fraction: float = 0.20):
    """Chronological split on UNIQUE MONTHS, with labels ending strictly before test.

    This is a single holdout per area/period, NOT k-fold TimeSeriesSplit.
    """
    dates = np.array(sorted(pd.to_datetime(frame["date"].unique())))
    if len(dates) < 15:
        raise ValueError(f"Too few calendar months for a forward-{horizon} evaluation")
    n_test = max(5, int(np.ceil(len(dates) * fraction)))
    if n_test >= len(dates):
        raise ValueError("Invalid temporal split")
    test_start = pd.Timestamp(dates[-n_test])
    test = frame.loc[frame["date"] >= test_start].copy()
    train = frame.loc[(frame["date"] < test_start) &
                      (frame["target_end"] < test_start)].copy()
    if train.empty or test.empty:
        raise ValueError("Purging leaves an empty train/test set")
    if train["target_end"].max() >= test["date"].min():
        raise AssertionError("Future information enters model training")
    if set(train["date"]).intersection(test["date"]):
        raise AssertionError("Same-month train/test contamination")
    return train, test


def train_evaluate(panel12: pd.DataFrame, n_trees: int = 400):
    result_rows, importance_rows = [], []
    for period in PERIODS:
        for area in ("EU", "USA"):
            subset = panel12.loc[(panel12.periodo == period) & (panel12.area == area)].copy()
            if subset.empty:
                raise ValueError(f"No forward-12m data for {period}/{area}")
            train, test = purged_holdout(subset)
            X_train, X_test = train[list(FEATURES)], test[list(FEATURES)]
            y_train, y_test = train.r_rel_12m_fwd, test.r_rel_12m_fwd
            rf = RandomForestRegressor(n_estimators=n_trees, random_state=42, n_jobs=1)
            rf.fit(X_train, y_train)
            yhat = rf.predict(X_test)
            # Baseline constant = train mean, without accessing holdout labels.
            constant = np.full(len(y_test), y_train.mean())
            record = {
                "periodo": period, "area": area,
                "R2_test": r2_score(y_test, yhat),
                "MAE_test": mean_absolute_error(y_test, yhat),
                "R2_baseline": r2_score(y_test, constant),
                "MAE_baseline": mean_absolute_error(y_test, constant),
                "train_months": train.date.nunique(), "test_months": test.date.nunique(),
                "n_train": len(train), "n_test": len(test),
                "train_last_label_month": train.target_end.max().strftime("%Y-%m"),
                "test_first_month": test.date.min().strftime("%Y-%m"),
            }
            result_rows.append(record)
            # Exploratory held-out permutation importance, not causal attribution.
            pi = permutation_importance(rf, X_test, y_test, scoring="neg_mean_absolute_error",
                                        n_repeats=10, random_state=42, n_jobs=1)
            for col, avg, sd in zip(FEATURES, pi.importances_mean, pi.importances_std):
                importance_rows.append({"periodo": period, "area": area, "feature": col,
                                        "mean_delta_MAE": float(avg), "sd_delta_MAE": float(sd)})
    return pd.DataFrame(result_rows), pd.DataFrame(importance_rows)


def annual_sharpe(values: np.ndarray) -> float:
    x = np.asarray(values, dtype=float)
    if len(x) < 12:
        return float("nan")
    sd = x.std(ddof=1)
    return float(x.mean() / sd * np.sqrt(12)) if sd > 0 else float("nan")


def circular_block_indices(n: int, block_length: int, rng: np.random.Generator) -> np.ndarray:
    """Sample contiguous months with replacement, preserving H/L alignment."""
    out = []
    while len(out) < n:
        start = int(rng.integers(0, n))
        out.extend((start + k) % n for k in range(block_length))
    return np.array(out[:n], dtype=int)


def paired_sharpe_analysis(panel: pd.DataFrame, n_boot: int = 5000,
                           block_length: int = 6, seed: int = 42):
    if n_boot < 100 or block_length < 1:
        raise ValueError("Bootstrap requires >=100 iterations, valid positive block length")
    results = []
    rng = np.random.default_rng(seed)
    for period in PERIODS:
        for area in ("EU", "USA"):
            subset = panel.loc[(panel.periodo == period) & (panel.area == area)]
            # Use only months with all six tracked tickers, equal weight 1/3 in group.
            pivot = subset.pivot(index="date", columns="ticker", values="r_rel").sort_index()
            high_names, low_names = (USA_HIGH, USA_LOW) if area == "USA" else (EU_HIGH, EU_LOW)
            if not set(high_names + low_names).issubset(pivot.columns):
                raise ValueError(f"Missing at least one ticker in {period}/{area}")
            pivot = pivot[list(high_names + low_names)].dropna()
            high, low = pivot[list(high_names)].mean(axis=1), pivot[list(low_names)].mean(axis=1)
            dates = pivot.index.to_series()
            # Time-series methods require consecutive months, no silently skipped gaps.
            if not (month_num(dates).diff().dropna() == 1).all():
                raise ValueError(f"Monthly gaps in {period}/{area}: investigate first")
            h, l = high.to_numpy(), low.to_numpy()
            diff = annual_sharpe(h) - annual_sharpe(l)
            boots = np.empty(n_boot)
            for j in range(n_boot):
                sample = circular_block_indices(len(h), block_length, rng)
                boots[j] = annual_sharpe(h[sample]) - annual_sharpe(l[sample])
            boots = boots[np.isfinite(boots)]
            if len(boots) < n_boot * .99:
                raise ValueError("Most Sharpe bootstrap replicates are degenerate")
            ci = np.quantile(boots, [.025, .975])
            # Approximate centered bootstrap null. The original tail-counting
            # against |observed| using UNcentered draws was invalid.
            centered = boots - diff
            p = (1 + np.sum(np.abs(centered) >= abs(diff))) / (len(boots) + 1)
            results.append({"periodo": period, "area": area,
                            "sharpe_high": annual_sharpe(h),
                            "sharpe_low": annual_sharpe(l),
                            "delta_sharpe": diff,
                            "ci95_low": ci[0], "ci95_high": ci[1],
                            "p_bootstrap_approx": p,
                            "n_months": len(h), "block_months": block_length})
    return pd.DataFrame(results)


def run(data_dir: Path, output_dir: Path, trees: int = 400, n_boot: int = 5000) -> None:
    sources = {
        "prices": data_dir / "prezzi_mensili_aggiornato.csv",
        "benchmarks": data_dir / "benchmarks_monthly_returns.csv",
        "esg": data_dir / "SALVATORE MEGNA DATI PANEL.xlsx",
    }
    missing = [str(p) for p in sources.values() if not p.is_file()]
    if missing:
        raise FileNotFoundError("Missing original data (run scripts/fetch_originals.py): " + ", ".join(missing))
    p = prepare_panel(read_prices(sources["prices"]),
                      read_benchmarks(sources["benchmarks"]),
                      read_esg(sources["esg"]))
    target = forward_12m_by_period(p)
    metrics, importance = train_evaluate(target, n_trees=trees)
    sharpe = paired_sharpe_analysis(p, n_boot=n_boot)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, table in [("panel_integrity", p.groupby(["periodo", "area"], as_index=False).agg(
                           n_obs=("ticker", "size"), n_months=("date", "nunique"))),
                        ("rf_purged_holdout", metrics),
                        ("rf_importance_heldout", importance),
                        ("sharpe_block_bootstrap", sharpe)]:
        table.to_csv(output_dir / f"{name}.csv", index=False, float_format="%.8f")
    print("Model evaluation (not historical scores):")
    print(metrics.round(4).to_string(index=False))
    print("Block bootstrap Sharpe (not historical p-values):")
    print(sharpe.round(4).to_string(index=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--out", type=Path, default=Path("outputs"))
    parser.add_argument("--trees", type=int, default=400)
    parser.add_argument("--bootstrap", type=int, default=5000)
    args = parser.parse_args()
    run(args.data_dir, args.out, trees=args.trees, n_boot=args.bootstrap)


if __name__ == "__main__":
    main()
