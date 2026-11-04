# ESG Scores and Energy Equity Returns (2013–2024)

**Energy finance · Random Forest · Leakage-aware time-series evaluation · Information ratio**

A reproducible reanalysis of 12 energy stocks across the United States and Europe, using historical E/S/G scores, monthly stock prices, and area-specific sector benchmark returns. The 2025 academic study is preserved as a **historical record**; this repository contains an explicitly revised Python pipeline and a separate report of the corrected evaluation.

> **Status: computationally validated, private review candidate.** [GitHub Actions run 41822713577](https://github.com/Salvatore-Megna/esg-energy-return-modeling/actions/runs/41822713577) successfully executed the seven methodology tests, downloaded and hash-verified all three original inputs, and recomputed the results below. Publication is pending review of third-party data rights, benchmark construction, and the final report. No causal ESG effect is claimed.

## Key findings

- Under a **calendar-month holdout with 12-month label purging**, the Random Forest has **negative test R² in five of six period × area groups** and underperforms a train-only mean baseline in those five groups.
- **USA, 2017–2020** is the sole positive group: test R² = **0.396** (baseline −0.169), MAE = **0.195** (baseline 0.272). This is a small, exploratory holdout of **eight distinct months**, not proof of stable forecasting skill.
- In **Europe, 2017–2020**, the High-minus-Low annualized relative information ratio is **1.676**, with six-month paired block-bootstrap 95% interval **[0.196, 3.247]** and an approximate, unadjusted p-value **0.033**. This should not be interpreted as an isolated ESG premium: the predefined groups also differ fundamentally between utilities and oil & gas.

[Read the updated analysis report](report/report.pdf) · [Full results and test sizes](docs/EMPIRICAL_RESULTS.md) · [View the authenticated-data CI run](https://github.com/Salvatore-Megna/esg-energy-return-modeling/actions/runs/41822713577)

## Study and methods

| Component | Description |
|---|---|
| Assets | 12 stocks (6 US, 6 European) |
| Periods | 2013–2016, 2017–2020, 2021–2024 |
| Inputs | Monthly stock prices, two area benchmark series, E/S/G and total ESG scores |
| Target | **Arithmetic sum** of the next 12 monthly stock-minus-sector returns, inside each period |
| Features | E, S, G, total ESG, all lagged one calendar month |
| Model | RandomForestRegressor (400 trees, fixed seed), fitted separately per period × area |
| Validation | Unique-month holdout; purge training labels overlapping the test; train-only mean baseline |
| Secondary analysis | Equal-weight High/Low group information ratios; paired six-month block bootstrap |

The original notebook split ticker–month **rows**, potentially sharing the same calendar month across train and test, and did not purge overlapping forward targets. The corrected analysis retains the original universe and sector-benchmark specification but chooses a single holdout by *distinct months*. All training observations whose 12-month label reaches the first test month are removed. The targets are also restricted to 12 consecutive months within each historical period. The resulting train set contains **16 distinct months** in each model; the test sets contain **7–8 months**.

The measure called “relative Sharpe” in the original study is more precisely an **annualized information ratio**, as the reference is the sector index, not the risk-free rate. The revised paired block bootstrap preserves both group alignment and some monthly dependence; its p-values are exploratory and **not adjusted for six comparisons**.

## Reproduce

From the project root, with **Python 3.11+** and internet access to the already-public historical repository:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/fetch_originals.py
python src/esg_analysis.py
```

The fetch script obtains three **authentic** source files from the historical GitHub site, checking byte lengths and Git blob SHA-1 hashes against the recovery manifest before use. No synthetic patient, market, or ESG data are included in the empirical analysis; synthetic records are used **only in isolated unit tests**. The data are deliberately **not duplicated** in this repository because the ESG data provider's redistribution permissions have not been verified.

The script regenerates four CSVs inside the ignored `outputs/` directory: `panel_integrity.csv`, `rf_purged_holdout.csv`, `rf_importance_heldout.csv` and `sharpe_block_bootstrap.csv`. The same four files are downloadable as a [GitHub Actions run artifact](https://github.com/Salvatore-Megna/esg-energy-return-modeling/actions/runs/41822713577/artifacts/13318280263) (requires access to this private repository).

## Repository map

```text
src/esg_analysis.py          Canonical revised empirical analysis
scripts/fetch_originals.py  Retrieve and authenticate three original inputs
tests/                     Methodology and synthetic integration checks
report/main.tex             Revised scientific report (IVPS LaTeX styling)
report/report.pdf            Typeset report of the verified evaluation
report/main_historical.tex  Historical 2025 report retypeset in the same style
docs/                      Actual results, scientific audit and source manifest
data/README.md              Input provenance and redistribution caution
.github/workflows/          Real-data and unit-test reproducibility checks
```

The [original 2025 notebook and report](https://github.com/Salvatore-Megna/Salvatore-Megna.github.io/tree/main/projects/esg-performance/assets) remain available on the existing portfolio site. The later alternative with a **US stock-mean benchmark** is intentionally *not* merged with the sector-benchmark study.

## Interpretation and limitations

This is an **observational, exploratory** comparison, not a trading system and not evidence that ESG ratings cause returns. The “High” and “Low” groups were selected by **business type** (utilities/transitional vs oil & gas), not by a data-driven ESG-score threshold. Potential confounding by industry, commodity prices, interest rates and risk exposures is substantial. Other limitations include overlapping forward labels inside test samples, small effective temporal sample sizes, unverified historical *availability timestamps* of ESG scores, potentially non-total-return price series, and benchmark source definitions not yet independently traced to ETF data. The bootstrap depends on block length and multiple comparisons.

The report and code do **not** represent the original 2025 model results as newly validated. Original results have their own provenance in the historical report; **new model metrics** and methodological differences are documented here.
