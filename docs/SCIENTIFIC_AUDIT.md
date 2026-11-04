# Audit scientifico — ESG Energy, 4 novembre 2026

## Perché questa è una nuova implementazione, non il notebook storico

La versione storica pubblicata nel sito GitHub usa 12 titoli fissi, benchmark settoriali in due colonne (`bm_USA`, `bm_EU`), rendimenti mensili **semplici**, punteggi ESG spostati di un mese e un target uguale alla **somma aritmetica dei successivi 12 rendimenti relativi**. In sei regressioni area × periodo applica `RandomForestRegressor(n_estimators=400, random_state=42)` e uno split 80/20 **per riga**. Tutti gli R² stampati erano negativi (vedi report storico).

Il notebook successivo della chat, che usa altri titoli e un benchmark costruito dalla media dei titoli USA, **non è equivalente** e non viene utilizzato. Non sono stati uniti i risultati delle due versioni.

## Correzioni metodologiche implementate e testate sulla logica

1. **Unità temporale:** ordinamento e split sugli effettivi mesi unici, non sul numero di righe ticker–mese; nessun mese è contemporaneamente nel training e nel test.
2. **Orizzonte del target:** per ogni ticker e per ogni intervallo politico-regolatorio, 12 rendimenti relativi **successivi**, con verifica della contiguità mensile; il target non può attraversare una delle tre finestre di quattro anni.
3. **Purging:** un'osservazione di training rimane soltanto se la sua etichetta (`target_end`) è **strettamente antecedente** al primo mese di test. Questo evita che la costruzione del target utilizzi rendimenti del test nel training; non elimina la correlazione fra target futuri sovrapposti all'interno di ciascun sottoinsieme.
4. **Baseline:** media del target calcolata esclusivamente sui dati di training. Vengono riportati R²/MAE della Random Forest e della baseline per evitare di attribuire valore predittivo a una prestazione semplicemente migliore di zero.
5. **Parametri:** 400 alberi e `random_state=42`, mantenendo gli stessi iperparametri del modello storico (nessuna ricerca iperparametrica eseguita sul test).
6. **Feature importance:** permutazione solo sui dati di test, con perdita MAE; risultato esplorativo poiché E/S/G/ESG totale sono correlati e le osservazioni hanno dipendenza temporale.
7. **Risk-adjusted return:** la misura costruita su rendimenti al netto del benchmark è tecnicamente un *information ratio annualizzato*, non uno Sharpe classico al netto del tasso privo di rischio. Manteniamo l'etichetta storica "Sharpe relativo" solo come rimando documentale.
8. **Bootstrap:** mesi High e Low sempre campionati con gli **stessi indici**; blocchi circolari contigui di 6 mesi per attenuare l'ipotesi di indipendenza mensile. Gli intervalli sono percentili bootstrap; il p-value esplorativo utilizza la distribuzione **centrata** `delta_boot - delta_osservato`, confrontando i valori assoluti con `|delta_osservato|`, con correzione add-one. Il p-value storico (distribuzione non centrata) non è valido per il test H0: delta=0. L'approssimazione centrata non sostituisce un test formale affidabile in campioni molto piccoli; fare analisi di sensibilità per blocchi 3/6/12 mesi.
9. **Composizione dei portafogli:** per le serie High/Low sono usati soltanto mesi con le tre società di ciascun gruppo presenti; questo rende stabile il peso 1/3 per titolo e non introduce variazioni arbitrarie di composizione.

## Controlli superati ora e controlli aperti

- **Superati localmente:** sette test logici e di integrazione su dati sintetici di sola verifica; verifica dei 12 mesi consecutivi e dei confini dei periodi; eliminazione dell'overlap train/test; riproduzione della somma aritmetica target; campionamento in blocchi abbinato; differenza nulla per portafogli identici; esecuzione sintetica completa dei sei modelli e sei confronti Sharpe; implementazione SHA Git corretta.
- **Non ancora eseguiti:** download dei tre file autentici dal sito GitHub, audit della struttura interna di `SALVATORE MEGNA DATI PANEL.xlsx`, esecuzione end-to-end su 2013–2024, risultati numerici corretti di R², MAE, importanze, Sharpe e IC/p-value, confronto/sensibilità dei bootstrap e controllo indipendente di XLE/EXH1.DE.
- **Report storico:** il LaTeX `report/main_historical.tex` e il PDF `report/report_historical_retypeset.pdf` preservano i risultati 2025 e la veste tipografica IVPS. **Non sono stati aggiornati con numeri del modello corretto**, perché quei numeri non sono stati calcolati su dati reali. La tabella originaria EU 2017–2020 riporta IC95% [0,371; 3,223] e p=0,530: è un'incoerenza metodologica nota, non un dato validato.

## Limiti fondamentali da dichiarare nel report finale

- **High/Low ESG è in realtà anche un confronto tra modelli di business** utility/transizione vs oil & gas, con forte confondimento settoriale. Non dimostra effetto ESG, causale o separato dal ciclo delle commodity.
- **Informazione disponibile:** uno `shift(1)` dei punteggi ESG non prova che il rating fosse stato pubblicato e disponibile a un investitore alla data usata. Il rischio di revisione retrospettiva dei rating non è verificato.
- **Pochi mesi:** un target a 12 mesi riduce gli anchor utili a circa 35 per ciascun blocco di 48 mesi; il purging ne sottrae altri 12. Una quota test di circa 7 mesi per blocco dà stime R² instabili e non molto comparabili a studi su lunghi orizzonti.
- **Prezzi e rendimenti:** l'uso di `price.pct_change()` non equivale necessariamente a un *total return* comprensivo di dividendi e corretta gestione delle azioni societarie. Verificare se i prezzi originali fossero aggiustati.
- **Benchmark:** la presenza delle colonne XLE/EXH1.DE nei commenti del codice non certifica l'origine e l'allineamento di tutte le serie benchmark.
- **Dati di terze parti:** l'Excel ESG era già pubblicato sul vecchio sito, ma questo non garantisce che la sua redistribuzione in un nuovo repository pubblico sia permessa.

## Principio di rendicontazione

Non inventare risultati. Le prestazioni del notebook 2025 sono **storiche**. Le prestazioni della nuova pipeline potranno essere pubblicate soltanto dopo l'esecuzione verificabile sugli originali, preferibilmente in un nuovo repository inizialmente privato con GitHub Actions verde. Non cancellare il sito esistente e non cambiare nessuna repository da privata a pubblica senza consenso.
