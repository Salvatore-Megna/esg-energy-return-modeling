# ESG Scores and Relative Returns in the Energy Sector

[Project overview — English (PDF)](docs/project-page.pdf) · [Original report — Italian](report/report.pdf) · [Full report — English](report/en/report.pdf)

An analysis of 12 energy companies in the US and Europe between 2013 and 2024. I examine whether monthly ESG scores help predict returns relative to sector benchmarks, and compare the risk-adjusted returns of utility and oil & gas portfolios.

The project uses Random Forest regression for the forecasting exercise and an annualized information ratio for the portfolio comparison.

[Original 2025 report — LaTeX edition](report/report.pdf) · [Results of the revised analysis](docs/results.md)

## Data and sample

| | United States | Europe |
|---|---|---|
| Utilities / transition | NextEra Energy, Xcel Energy, Duke Energy | Enel, Iberdrola, E.ON |
| Oil & gas | Exxon Mobil, Chevron, Occidental Petroleum | TotalEnergies, BP, ENI |

The input files cover monthly prices, sector-benchmark returns and E, S, G and overall ESG scores. I consider three periods: **2013–2016**, **2017–2020** and **2021–2024**.

The two groups are defined by business activity, not by an estimated cutoff in ESG scores. This matters when interpreting differences between them. [Data sources and file details](data/README.md).

## Results of the revised analysis

The PDF report preserves the methodology, formula, tables and conclusions of the original 2025 study. The results below instead refer to the later Python evaluation with calendar-month holdouts; the two sets of estimates should not be mixed.

- Random Forest test R² is **negative in five of the six** period–region combinations. The only positive result is for the US in 2017–2020 (**R² = 0.396**); that test covers just eight distinct months, so the finding needs further validation.
- In Europe in 2017–2020, the difference between the two portfolios' annualized information ratios is **1.676** (95% block-bootstrap interval **0.196 to 3.247**). The result is exploratory: the groups differ by industry, and the six comparisons have not been corrected for multiple testing.
- Across the other periods, the portfolio differences are less conclusive. The study does not establish a causal ESG premium.

## Method

Monthly stock returns are calculated from the available price series and expressed relative to a benchmark for each region. The prediction target is the **sum of the following 12 monthly relative returns**; E, S, G and overall ESG scores enter with a one-month lag.

Six Random Forest models (400 trees each) are fitted separately by period and region. Training and test sets are separated by **calendar month**, and training observations are removed when their forward-looking target reaches into the test period. Performance is compared against the mean target observed in training. The portfolio analysis uses equal-weight monthly returns and a paired six-month block bootstrap.

Details of the temporal split, the bootstrap procedure and differences from the earlier notebook are in [methodology notes](docs/methodology.md).

## Run the analysis

Python 3.11 or later is recommended. From the repository root:

```bash
python -m pip install -r requirements.txt
python scripts/fetch_originals.py
python src/esg_analysis.py
```

The input script downloads the three source files from the [earlier project archive](https://github.com/Salvatore-Megna/Salvatore-Megna.github.io/tree/main/projects/esg-performance/assets) and checks their recorded Git blob hashes. They are not committed here because redistribution permissions for the ESG panel have not been confirmed.

Results are saved as CSV files under `outputs/`. To run the checks:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

The analysis and tests also run in [GitHub Actions](https://github.com/Salvatore-Megna/esg-energy-return-modeling/actions/runs/41823752182).

## Files

| Location | Contents |
|---|---|
| `src/esg_analysis.py` | Data preparation, models and portfolio analysis |
| `scripts/fetch_originals.py` | Source-file retrieval and checks |
| `report/` | Original 2025 report, typeset in LaTeX without changing its content |
| `docs/results.md` | Full results by period and region |
| `docs/methodology.md` | Method choices and limitations |
| `tests/` | Unit and integration tests |

## Limitations

This is a small observational study. Overlapping 12-month targets, short test windows, sector differences and the treatment of dividends all limit the conclusions. The precise construction of the benchmark files and the dates on which ESG scores became available have not been independently established. The reported bootstrap intervals depend on the block length; they are not evidence of causality.
