"""Synthetic INTEGRATION fixture: no empirical results are inferred from this test."""
from pathlib import Path
import contextlib
import io
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from esg_analysis import TICKERS, MAP_ESG_TO_TICKER, run


class TestSyntheticWorkflow(unittest.TestCase):
    def test_all_outputs_without_leakage(self):
        rng = np.random.default_rng(89)
        ticker_inverse = {v: k for k, v in MAP_ESG_TO_TICKER.items()}
        dates = pd.date_range("2013-01-31", periods=144, freq="ME")
        prices, esg, bench = [], [], []
        for dt in dates:
            bench.append({"date": dt, "bm_USA": rng.normal(0, .01),
                          "bm_EU": rng.normal(0, .01)})
        for ticker in TICKERS:
            price = 100.
            for dt in dates:
                price *= 1 + rng.normal(.003, .035)
                prices.append({"date": dt, "ticker": ticker, "price": price})
                esg.append({"Date": dt.strftime("%m/%y"),
                            "Ticker": ticker_inverse[ticker],
                            "ESG-E SCORE": rng.uniform(30, 70),
                            "ESG-S SCORE": rng.uniform(30, 70),
                            "ESG-G SCORE": rng.uniform(30, 70),
                            "ESG TOT SCORE": rng.uniform(30, 70)})
        with tempfile.TemporaryDirectory() as temp:
            data, out = Path(temp) / "raw", Path(temp) / "out"
            data.mkdir()
            pd.DataFrame(prices).to_csv(data / "prezzi_mensili_aggiornato.csv", index=False)
            pd.DataFrame(bench).to_csv(data / "benchmarks_monthly_returns.csv", index=False)
            pd.DataFrame(esg).to_excel(data / "SALVATORE MEGNA DATI PANEL.xlsx", index=False)
            # Non stampare risultati fittizi nell'output dei test.
            with contextlib.redirect_stdout(io.StringIO()):
                run(data, out, trees=15, n_boot=120)
            files = {x.name for x in out.glob("*.csv")}
            self.assertEqual(files, {"panel_integrity.csv", "rf_purged_holdout.csv",
                                     "rf_importance_heldout.csv", "sharpe_block_bootstrap.csv"})
            metrics = pd.read_csv(out / "rf_purged_holdout.csv")
            sharpe = pd.read_csv(out / "sharpe_block_bootstrap.csv")
            self.assertEqual(len(metrics), 6)
            self.assertEqual(len(sharpe), 6)
            self.assertTrue(metrics.MAE_test.notna().all())
            self.assertTrue((pd.to_datetime(metrics.train_last_label_month) <
                             pd.to_datetime(metrics.test_first_month)).all())
            self.assertTrue((sharpe.p_bootstrap_approx >= 0).all())
            self.assertTrue((sharpe.p_bootstrap_approx <= 1).all())


if __name__ == "__main__":
    unittest.main()
