# Input data provenance

This repository-ready package deliberately excludes the original user-provided ESG panel because the third-party score-provider redistribution rights have not been checked. The three files are already hosted on the user's historical **public** GitHub site; this package does not create or publish a second copy.

Run `python scripts/fetch_originals.py` from the project root to fetch and verify:

| Input file | Historical blob SHA-1 | Role |
|---|---|---|
| `SALVATORE MEGNA DATI PANEL.xlsx` | `78c6357d377d6124d3e64c64777d9a266c4e1a45` | Monthly E/S/G and total ESG scores |
| `prezzi_mensili_aggiornato.csv` | `7d812d37898c914ec5712506021d472e20af590a` | Monthly ticker prices |
| `benchmarks_monthly_returns.csv` | `14e03de0fd48a9782eec829ef643f53ec0f5b6e9` | Monthly USA/EU benchmark active-return inputs |

Checksums are **Git object hashes**, not plain SHA-1 checksums. The original source path is `https://github.com/Salvatore-Megna/Salvatore-Megna.github.io/tree/main/projects/esg-performance/assets`. The independent 2025 raw data source, quality, license, score publication timestamps and benchmark methodology remain to be audited before any claim of research-grade causal interpretation.
