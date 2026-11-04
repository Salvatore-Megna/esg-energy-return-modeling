# Data

Three input files are used in the analysis. They are retrieved from the [existing project archive](https://github.com/Salvatore-Megna/Salvatore-Megna.github.io/tree/main/projects/esg-performance/assets) by `scripts/fetch_originals.py`.

| File | Contents |
|---|---|
| `SALVATORE MEGNA DATI PANEL.xlsx` | Monthly E, S, G and overall ESG scores for the selected companies |
| `prezzi_mensili_aggiornato.csv` | Monthly prices by ticker |
| `benchmarks_monthly_returns.csv` | Monthly sector-benchmark returns for the US and Europe |

The script checks file sizes and Git blob hashes recorded in `docs/source_manifest.json`. The downloaded files are placed in `data/raw/` and are ignored by Git.

The ESG dataset is not redistributed in this repository because the provider's data-use terms have not been confirmed. The available price series have not been independently verified as total-return series, and the underlying construction of the benchmark returns requires further checking.
