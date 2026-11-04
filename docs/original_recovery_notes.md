# ESG Energy — Specifiche documentate e conflitti

**Stato**: memo di recupero, NON revisione scientifica e NON nuova analisi. Data: 2026-11-04.

## A. Variante storica pubblicata sul sito GitHub (codice verificato nel notebook sorgente)

- Studio aziende energetiche USA/EU, 2013-2024; tre periodi: `pre_trump` 2013–2016, `trump` 2017–2020, `biden` 2021–2024. I nomi sono semplici etichette di periodo.
- Dodici ticker: USA High `[NEE, XEL, DUK]`, USA Low `[XOM, CVX, OXY]`, EU High `[ENEL.MI, IBE.MC, EOAN.DE]`, EU Low `[TTE.PA, BP.L, ENI.MI]`.
- **Attenzione**: High/Low sono gruppi assegnati nel codice per ticker, non categorie apprese da una soglia ESG calcolata sui dati.
- Fonte ESG nel codice: primo foglio di `SALVATORE MEGNA DATI PANEL.xlsx`, colonne `Date`, `Ticker`, `ESG-E SCORE`, `ESG-S SCORE`, `ESG-G SCORE`, `ESG TOT SCORE`. Mapping dei codici ESG con suffissi geografici nei ticker Yahoo. La struttura materiale dell'Excel rimane da controllare direttamente.
- Prezzi mensili `date,ticker,price`; prezzi allineati alla fine del mese, per ticker/mese conservata l'ultima osservazione. Calcola rendimenti mensili semplici tramite `pct_change()`.
- Benchmark **separati per area** da `benchmarks_monthly_returns.csv` (`bm_USA`, `bm_EU`, citati nel codice come USA≈XLE e EU≈EXH1.DE); rendimenti relativi `r_titolo - r_benchmark_area`.
- ESG E/S/G/TOT con lag **per titolo** usando `groupby(ticker).shift(1)`.
- **Layer A storico**: target = somma aritmetica dei successivi 12 rendimenti relativi mensili (variabile `r_rel_12m_fwd`); non un rendimento composto. RandomForestRegressor(400 alberi, random_state 42), split 80/20 con ordinamento temporale all'interno di ciascun periodo e area. Metriche `R2_test` e `MAE_test`.
- **Layer B storico**: serie di rendimento relativo equal weight per gruppi High/Low definiti a priori, Sharpe annualizzato sqrt(12); confronto delta High–Low mediante bootstrap su mesi abbinati (5000 repliche), con IC 95% e p-value **come calcolato nello script originale**.
- Il notebook GitHub contiene due celle e una sola stampa di output, non grafici embedded. Non usa `TimeSeriesSplit`, `permutation_importance` né matplotlib. PDF report/slides presenti ma non ispezionati pagina per pagina.
- Output storici nel notebook: tutti i **6 R² test riportati sono negativi**: pre_trump EU -1.399, USA -0.475; trump EU -1.813, USA -0.395; biden EU -1.071, USA -1.387. **Valori stampati storici, non ricalcolati.**

## B. Versione successiva fornita nella chat (codice Cursor e notebook dell'assistente)

- Usa un **insieme USA diverso**: `[XOM, CVX, COP, EOG, SLB, KMI]`, EU `[ENEL.MI, IBE.MC, EOAN.DE, TTE.PA, BP.L, ENI.MI]`.
- Benchmark nella prima versione = **media dei rendimenti dei titoli USA**, non XLE/EXH1.DE; target = rendimento relativo **mensile**, non 12m avanti.
- Il codice Python incollato dall'utente (versione Cursor) crea esplicitamente ESG **casuali simulati** e risultati High/Low Sharpe casuali. Non considerarli osservazioni empiriche.
- Il notebook creato successivamente in chat `Analisi_ESG_Rendimenti_solo_reale.ipynb` prova a usare ESG reali, ma **non è l'originale GitHub** e non è stato verificato end-to-end con i dati. Le sue assunzioni sul layout Excel (quattro fogli) potrebbero confliggere con il primo foglio long atteso dal notebook storico; non affermare compatibilità.
- Il notebook chat ha `TimeSeriesSplit` e importanze permutazionali, assenti nello storico GitHub. Nessun test di significatività delle singole feature è documentato come risultato storico verificato.

## C. Punti da verificare scientificamente (non risolti qui)

- Leakage tra train/test nella costruzione del target forward-12m e nella ripartizione a livello di riga anziché blocchi temporali completamente separati.
- Verifica dei benchmark e della loro costruzione, allineamento dei ticker e temporalità ESG; licenza dei dati ESG e prezzi.
- Interpretazione dei gruppi High/Low predefiniti rispetto ai punteggi effettivamente osservati.
- Bootstrap temporale e calcolo del p-value: nel risultato stampato per EU/trump IC95% delta Sharpe [0.371,3.223] e p-value 0.530, **incoerenti con un test usuale a due code per H0 delta=0**. Occorre audit del test, non reinterpretare come validazione positiva.
- Validazione rispetto a baseline e test delle feature, stabilità delle importanze, comparabilità fra periodi/aree.

Il codice, i risultati e gli asset originali NON sono stati riscritti o ricalcolati in questo recupero.
