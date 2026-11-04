# Data sources

| File | Provider / acquisition | Coverage | Observation |
| --- | --- | --- | --- |
| `COEBiddingResultsPrices.csv` | LTA; supplied by SDS for the datathon | Jan 2010–Oct 2026; 1,990 rows | Category within a bidding exercise; 398 exercises |
| `NewRegistrationofCarsbyMake.csv` | LTA; supplied by SDS for the datathon | Jan 2016–May 2025; 51,669 rows | Month, make, importer type, fuel and vehicle type |
| `M032-Car_Cost_Update_Sep_2026.csv` | Team-provided CSV of the LTA September car cost report | Sep 2026; 237 listed entries | Listed model entry, COE category and monthly average OMV |

Original acquisition dates were not recorded. The files are the fixed snapshots used in the project, rather than live feeds. Numerical results use these local files.

## References

- [LTA September 2026 car cost report](https://onemotoring.lta.gov.sg/content/dam/onemotoring/Buying/Car_Cost_Update/M032-Car_Cost_Update.pdf). The report link may be updated; this repository retains the September 2026 CSV snapshot. Its coverage is local authorised distributors' registered models, without registration counts.
- [LTA vehicle-statistics notes: historical A/B definitions](https://www.lta.gov.sg/content/dam/ltagov/who_we_are/statistics_and_publications/statistics/pdf/MVP02-1_New_Reg_by_COE.pdf).
- [LTA circular: May 2022 Category A electric-car power threshold](https://onemotoring.lta.gov.sg/content/dam/onemotoring/pdf/Circulars%20to%20ESAs/2022/VRL_04_2022.pdf).

## Interpretation

Registration blanks are unknown counts and remain missing. Explicit zeros remain zeros. Registrations do not identify individual models or their COE category. The OMV snapshot supplies average values for listed entries, without sales weights. Bidding suspensions are retained as gaps rather than interpolated exercises.

The proposed three- and five-band feebate amounts are team scenario inputs, fully specified in `main.ipynb`; they are not official policy parameters. Forecasts and merged-price proxies are calculated in the notebook and are not input datasets.

## File checksums (SHA-256)

| File | SHA-256 |
| --- | --- |
| `COEBiddingResultsPrices.csv` | `82ca7034008793e1241531f70c6363b78c16e358cdbd4985dcec5443f06d48b6` |
| `NewRegistrationofCarsbyMake.csv` | `196ea98f567c63844ad66cb7e8f410c9d60029768e6fe1506bec18849265af76` |
| `M032-Car_Cost_Update_Sep_2026.csv` | `575d22de3497bdb7667499e38735254a1ec3b52ebdaba734d1247bde82db1d21` |
