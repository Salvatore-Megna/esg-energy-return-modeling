"""Unit tests with synthetic fixture ONLY; never presented as empirical data."""
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from esg_analysis import (
    EU_HIGH, EU_LOW, USA_HIGH, USA_LOW,
    circular_block_indices, forward_12m_by_period,
    paired_sharpe_analysis, purged_holdout,
)
from scripts.fetch_originals import git_blob_sha1


class TemporalValidationTests(unittest.TestCase):
    @staticmethod
    def dummy_panel():
        # SYNTHETIC data: used solely for testing date arithmetic.
        rng = np.random.default_rng(102)
        months = pd.date_range("2013-01-31", periods=96, freq="ME")
        rows = []
        for ticker in USA_HIGH + USA_LOW + EU_HIGH + EU_LOW:
            for dt in months:
                rows.append({"date": dt, "ticker": ticker,
                             "periodo": "pre_trump" if dt.year <= 2016 else "trump",
                             "area": "USA" if ticker in USA_HIGH + USA_LOW else "EU",
                             "esg_class": "High" if ticker in USA_HIGH + EU_HIGH else "Low",
                             "r_rel": rng.normal(0, .02)})
        return pd.DataFrame(rows)

    def test_target_stays_in_period_and_is_exactly_12_months(self):
        panel = self.dummy_panel()
        y = forward_12m_by_period(panel)
        self.assertTrue((y.target_end.dt.year <= 2020).all())
        self.assertTrue((y.target_end.dt.year - y.date.dt.year <= 1).all())
        self.assertTrue((y.target_end.dt.year * 12 + y.target_end.dt.month -
                         y.date.dt.year * 12 - y.date.dt.month == 12).all())
        # Last anchor within 2013–2016 must be December 2015, not 2016.
        a = y[y.periodo == "pre_trump"]
        self.assertEqual(a.date.max(), pd.Timestamp("2015-12-31"))
        self.assertEqual(len(a), 12 * 36)
        # The first month has 12 successive returns, but none beyond 2016.
        self.assertEqual(y[(y.ticker == "NEE") & (y.date == "2013-01-31")].shape[0], 1)

    def test_purged_unique_months_and_no_target_overlap(self):
        panel = self.dummy_panel()
        y = forward_12m_by_period(panel)
        example = y[(y.periodo == "pre_trump") & (y.area == "USA")]
        tr, te = purged_holdout(example)
        self.assertGreater(len(tr), 0)
        self.assertGreater(len(te), 0)
        self.assertLess(tr.target_end.max(), te.date.min())
        self.assertEqual(len(set(tr.date).intersection(te.date)), 0)
        self.assertEqual(tr.groupby("date").ticker.nunique().min(), 6)
        self.assertEqual(te.groupby("date").ticker.nunique().min(), 6)
        self.assertGreaterEqual((te.date.min().year * 12 + te.date.min().month) -
                                (tr.date.max().year * 12 + tr.date.max().month), 13)

    def test_forward_sum_preserves_arithmetic_historical_definition(self):
        panel = self.dummy_panel()
        panel["r_rel"] = .01
        y = forward_12m_by_period(panel)
        self.assertTrue(np.allclose(y.r_rel_12m_fwd, .12))


class BootstrapTests(unittest.TestCase):
    def test_resampling_keeps_temporal_blocks(self):
        rng = np.random.default_rng(4)
        ids = circular_block_indices(40, 6, rng)
        self.assertEqual(len(ids), 40)
        for b in range(0, 36, 6):
            np.testing.assert_array_equal(np.diff(ids[b:b+6]) % 40, np.ones(5, dtype=int))

    def test_equal_group_returns_give_zero_difference_and_p_one(self):
        panel = TemporalValidationTests.dummy_panel()
        series = {(p, d): np.random.default_rng(7 + d).normal(0, .01, 48)
                  for p in ("pre_trump", "trump") for d in (0, 1)}
        for idx, row in panel.iterrows():
            t = int(row.date.year - 2013) * 12 + row.date.month - 1
            y = 0 if row.area == "USA" else 1
            panel.at[idx, "r_rel"] = series[(row.periodo, y)][t % 48]
        # Ensure the third period is available to the original two-period fixture.
        for period in ("pre_trump", "trump"):
            part = panel[panel.periodo == period]
            self.assertEqual(part.date.nunique(), 48)
        # Subset test paired block method on a 3-period fixture.
        extra = panel[panel.periodo == "trump"].copy()
        extra["date"] = extra["date"] + pd.DateOffset(years=4)
        extra["periodo"] = "biden"
        full = pd.concat([panel, extra], ignore_index=True)
        result = paired_sharpe_analysis(full, n_boot=150, block_length=6)
        self.assertTrue(np.allclose(result.delta_sharpe, 0, atol=1e-12))
        self.assertTrue(np.allclose(result.p_bootstrap_approx, 1))
        self.assertTrue(np.allclose(result.ci95_low, 0, atol=1e-12))
        self.assertTrue(np.allclose(result.ci95_high, 0, atol=1e-12))

    def test_correct_git_blob_hash_example(self):
        # Git's documented "blob <size>\\0<payload>" object hashing.
        self.assertEqual(git_blob_sha1(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")


if __name__ == "__main__":
    unittest.main()
