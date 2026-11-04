# Methodology notes

## Forecasting setup

Monthly prices are converted to simple returns, with the last available observation retained for each ticker and month. A stock's relative return is its monthly return minus the corresponding regional benchmark return.

For a given month, the response is the arithmetic sum of the next twelve relative monthly returns. Targets are calculated only when twelve consecutive months are available within the same analysis period. The explanatory variables are E, S, G and total ESG scores, each lagged by one month.

Each of the six region–period samples is evaluated separately with a Random Forest of 400 trees. The final calendar months form the test set. An observation is included in training only when the full 12-month response window ends before the first test month; no month is split between train and test. A constant prediction based on the training mean provides a baseline. Test R² and MAE are reported for both models.

This differs from the 2025 notebook, where the 80/20 split was applied to ordered ticker–month rows and forward-response overlap was not excluded. For that reason the earlier prediction metrics are not directly comparable with those in the current report. The original material is retained in the [project archive](https://github.com/Salvatore-Megna/Salvatore-Megna.github.io/tree/main/projects/esg-performance/assets).

## Portfolio comparison

High and Low refer to predefined groups of utilities/transitional companies and oil & gas companies, respectively. For each group, three stocks are equally weighted within a month. The reported annualized information ratio is the mean monthly relative return divided by its sample standard deviation, multiplied by the square root of twelve.

High and Low portfolios are matched by month. Their information-ratio difference is evaluated with 5,000 paired circular block-bootstrap draws, using six-month blocks. The displayed intervals are percentile intervals; the p-values use an approximate centered bootstrap calculation. The six comparisons are not adjusted for multiple testing.

The earlier notebook reported bootstrap p-values from a different calculation. These have not been reused in the current results.

## Scope and limitations

The analysis is descriptive and exploratory, not a test of a causal effect of ESG scores. Sector exposure and commodity prices differ strongly between the predefined groups. With 12-month targets, purging leaves only sixteen training months and seven or eight test months for each model. Targets within the test sample still overlap, so the number of stock–month rows should not be interpreted as independent observations.

Additional checks would be needed on the underlying benchmarks, price adjustments for dividends, ESG score publication dates and sensitivity to different bootstrap block lengths.
