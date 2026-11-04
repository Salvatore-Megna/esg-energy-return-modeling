# ESG Scores and Energy Equity Returns (2013–2024)

**Reproducibility audit · Random Forest · Time-aware evaluation · Relative portfolio returns**

Reassessment of the historical ESG Energy study across 12 US and European energy stocks and three four-year windows. The 2025 academic report and the original notebook are retained as **historical records**, while this package supplies a clearly labeled corrected Python analysis.

> **Validation status:** the methods and synthetic unit tests have passed locally. **Results on the authentic ESG panel have not yet been recomputed or GitHub Actions-validated**: this sandbox cannot download the three original data files from the existing GitHub site. The historical numerical tables are **not** results from the corrected methodology. Do not release a revised results report until the authentic-data run succeeds.

## Study at a glance

| Topic | Details |
|---|---|
| Assets | 12 energy stocks: 6 USA, 6 EU |
| Periods | 2013–2016, 2017–2020, 2021–2024 |
| Inputs | Monthly stock prices, US/EU sector benchmark returns, historical E/S/G/total ESG scores |
| Original model | Random Forest, prediction of *arithmetic sum* of next 12 monthly relative returns |
| Revised evaluation | Unique-calendar-month holdout, 12-month target purging, train-only mean baseline |
| Relative performance | Equal-weight monthly active returns; annualized information ratio and paired block-bootstrap uncertainty |
| Original results | All six test R² values are negative **under the historical split**; not transferable to revised evaluation |

## Why a revision was necessary

The historical notebook applies the 80/20 split to **ticker-month rows**, making same-month train/test overlap possible. It also calculates rolling forward-12-month labels before filtering by the three periods; adjacent labels share future returns across split boundaries. The original bootstrap p-value is based on an uncentered bootstrap distribution and is not a valid two-sided null test. See [scientific audit](docs/SCIENTIFIC_AUDIT.md).

The revised model retains the historical universe, two area-specific benchmark columns, ESG lag-one features and **non-compounded** 12-month active-return target. Target construction now stays inside each four-year period and each ticker. A holdout is split by distinct calendar months, then *all training rows whose target ends on or after the first test month are purged*. Tests assert the non-overlap. The model is compared with a **train-mean baseline** using both MAE and R²; held-out permutation importance is descriptive only.

**Important:** High/Low membership is a preselected utility-versus-oil-and-gas grouping, not an ESG threshold learned from the data. An observed difference cannot identify an ESG effect. Because the original risk-adjusted ratio uses **benchmark-relative** returns instead of a risk-free return, it is more precisely an *annualized information ratio*, historically named “relative Sharpe”. A paired **6-month circular block bootstrap** preserves month matching and some serial dependence. Its centered two-sided p-value is approximate and exploratory, not a definitive inference. Compare block lengths in sensitivity analyses before public claims.

## How to reproduce

Use Python 3.11+ and start from the project root:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -p 'test_*.py' -v
python scripts/fetch_originals.py
python src/esg_analysis.py
```

The download script retrieves **only the three authentic source files** from the pre-existing [historical GitHub portfolio](https://github.com/Salvatore-Megna/Salvatore-Megna.github.io/tree/main/projects/esg-performance/assets), verifying **file size and Git blob SHA-1** against the recovery manifest before writing to `data/raw/`. **No synthetic or randomly generated ESG records are used for the empirical analysis.** Synthetic data appear only in isolated unit tests.

Outputs (when the authentic source files are available) are written to `outputs/`, and are intentionally excluded from Git. These four CSVs contain cohort integrity, the six time-purged regression comparisons, held-out exploratory importance and the six group-paired bootstrap estimates.

The included `.github/workflows/checks.yml` runs the unit tests and a complete authenticated-source reproduction **after the files are uploaded to a new private repository**. Workflow configuration is not proof that a run succeeded.

## Directory map

```text
src/esg_analysis.py       Single canonical corrected Python analysis
scripts/fetch_originals.py  Recover and verify the three historical input files
tests/                   Focused synthetic methodology tests
docs/                    Source manifest and method/provenance review
report/                  2025 report re-typeset in IVPS LaTeX style (historical values)
data/                    Input attribution; original data excluded from package
.github/workflows/       Proposed CI checks, not yet executed on GitHub
```

## Data ownership, research limitations and publication gate

The original ESG panel is attributed to a third-party score provider in the historical work; the **rights to redistribute it have not been established**. The input files are not embedded in this ZIP. The benchmark identities (XLE and EXH1.DE) are historical code annotations and have not been independently audited against all CSV construction steps. Corporate-sector differences, factor exposures, dates of ESG-score publication, short time horizons, overlapping 12-month targets inside each holdout, and benchmark definitions limit interpretation. All analysis is observational and exploratory.

Do **not** present the report PDF as a scientifically corrected empirical report: it preserves historical numbers for traceability only. Replace the tables and discussion after a clean run with real inputs and a final methodological review. The separate historical **US mean-of-stocks benchmark variant** is intentionally excluded rather than silently combined with this study.
