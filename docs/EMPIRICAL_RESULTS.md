# Authenticated empirical results — 4 November 2026

**Source and execution:** 12 historical energy equities, 2013–2024. The three source files were downloaded and verified against the historical Git blob hashes. [GitHub Actions run 41822713577](https://github.com/Salvatore-Megna/esg-energy-return-modeling/actions/runs/41822713577) passed both jobs. Four original CSV results from the run are available in [artifact 13318280263](https://github.com/Salvatore-Megna/esg-energy-return-modeling/actions/runs/41822713577/artifacts/13318280263). Values below are rounded from the actual CI log, **not inferred from historical output or synthetic tests**.

## Forward 12-month Random Forest — corrected purged temporal holdout

The split is by **unique calendar months** rather than ticker–month rows. Every training label ends before the first test month. Features are lagged E, S, G and total ESG, and the prediction target is the *arithmetic sum* of the following twelve monthly active returns, with no crossing of historical period boundaries. Baseline is the mean of training targets only.

| Period | Area | Test R² RF | Test R² baseline | MAE RF | MAE baseline | Training months | Test months | Rows train/test |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2013–2016 | EU | −2.6960 | −1.7356 | 0.2040 | 0.1729 | 16 | 7 | 96 / 42 |
| 2013–2016 | USA | −0.1910 | −0.1213 | 0.1185 | 0.1129 | 16 | 7 | 96 / 42 |
| 2017–2020 | EU | −0.6119 | −0.3270 | 0.3705 | 0.3434 | 16 | 8 | 96 / 48 |
| 2017–2020 | USA | **0.3955** | −0.1689 | **0.1952** | 0.2722 | 16 | 8 | 96 / 48 |
| 2021–2024 | EU | −3.6122 | −0.9409 | 0.2590 | 0.1610 | 16 | 8 | 96 / 48 |
| 2021–2024 | USA | −3.2624 | −0.8458 | 0.2585 | 0.1825 | 16 | 8 | 96 / 48 |

The **USA 2017–2020** model is the sole exception with positive out-of-sample R² and an MAE below baseline. All other model evaluations have negative test R² and greater MAE than the constant baseline. This is a short, single holdout with overlapping labels inside the test; **test rows are not independent observations**.

## Portfolio-relative information ratio and paired block bootstrap

The original “relative Sharpe” is an **annualized information ratio**, defined as mean monthly return *relative to the sector benchmark* divided by its sample standard deviation, multiplied by √12. The two three-stock groups are equally weighted. High and Low are matched by month and resampled using 6-month circular blocks, 5,000 replicates, seed 42. P-values use a *centered, approximate* two-sided bootstrap null calculation and are **not adjusted for six comparisons**.

| Period | Area | IR High | IR Low | High − Low | 95% bootstrap interval | Approx. p | Paired months |
|---|---|---:|---:|---:|---|---:|---:|
| 2013–2016 | EU | 0.1525 | 0.1125 | 0.0400 | [−0.5935, 0.6897] | 0.9054 | 47 |
| 2013–2016 | USA | 0.4313 | 0.0939 | 0.3374 | [−0.3066, 1.0089] | 0.3157 | 47 |
| 2017–2020 | EU | 0.8941 | −0.7820 | **1.6762** | **[0.1955, 3.2472]** | **0.0326** | 48 |
| 2017–2020 | USA | 0.6683 | 0.0425 | 0.6259 | [−0.3287, 1.6722] | 0.2030 | 48 |
| 2021–2024 | EU | −0.2245 | 0.3972 | −0.6217 | [−1.8599, 0.7739] | 0.3471 | 48 |
| 2021–2024 | USA | −0.6672 | 0.0980 | −0.7652 | [−2.0837, 0.7044] | 0.2801 | 48 |

**Important:** the EU 2017–2020 interval excludes zero at this particular block length, but the nominal p-value does not establish an ESG premium. The portfolios were grouped in advance by industry (utilities/transitional versus oil and gas). Multiplicity, serial dependence, market regimes, the small universe and score-timestamp uncertainty prevent causal interpretation.

## Differences from the 2025 original

The historical notebook reported six negative R² values under its ticker-row 80/20 split. In the corrected analysis the temporal unit is month, a 12-month purge is applied and labels cannot cross the three period boundaries, so those six values are **not directly comparable** with this table. The historical bootstrap p-values were not computed from a centered null distribution; in particular, the reported European 2017–2020 p-value of 0.530 conflicted with the historical percentile interval excluding zero. The new numbers use a different, explicitly documented block-bootstrap procedure.

**Remaining scientific checks before publication:** trace benchmark series to the actual underlying ETFs; verify adjustment of stock prices for distributions, availability timestamps of ESG ratings, and redistribution rights; test sensitivity to 3/6/12-month block lengths and to alternative benchmark/portfolio specifications.
