# Baghdad chronological charging-energy and cost screen

The base traction intensity and timetable imply **2,053.8 GWh/year**. The dedicated plant is 1,018.6 MW, plus existing on-site PV and 354 MWh storage. The base model's annual generation netting is not firm delivered charging. Ten percent of traction purchased at USD 0.10/kWh is **USD 20.538m/year**, an arithmetic sensitivity, not a forecast.

[Hourly CSVs](chronological-energy.json) contain three 8,760-hour synthetic representative weather/age years for each of owned solar, contracted solar and additional hybrid storage. They use the same timetable-derived service duty, with overnight schedules split across midnight; charger loss, PV performance/wheeling loss, storage charge/discharge losses, SoC floor, age degradation, import limits and curtailment are explicit. A seven-day poor-production spell is included. Initial storage sits at its protected floor, supplying no free energy. End storage is recorded and not sold.

| Synthetic case | Grid GWh | Unserved GWh | Annual energy USD m | Extra hybrid equipment USD m |
| --- | --- | --- | --- | --- |
| synthetic_reference:owned_solar | 937.3 | 2.705 | 137.751 | 0.0 |
| synthetic_reference:contracted_solar | 937.3 | 2.705 | 204.663 | 0.0 |
| synthetic_reference:hybrid_storage | 455.7 | 2.705 | 89.590 | 180.0 |
| synthetic_poor_year:owned_solar | 1066.4 | 2.873 | 146.260 | 0.0 |
| synthetic_poor_year:contracted_solar | 1066.4 | 2.873 | 193.389 | 0.0 |
| synthetic_poor_year:hybrid_storage | 813.0 | 2.873 | 120.927 | 180.0 |
| synthetic_aged_year_10:owned_solar | 957.1 | 2.705 | 139.733 | 0.0 |
| synthetic_aged_year_10:contracted_solar | 957.1 | 2.705 | 206.645 | 0.0 |
| synthetic_aged_year_10:hybrid_storage | 520.1 | 2.705 | 96.031 | 180.0 |

Electricity purchase, wheeling, balancing, capacity connection and owned-plant maintenance / contracted-solar payment are separate. PPA pays generated output even if curtailed; no surplus power sale is booked. The contracted case removes dedicated solar ownership capital and O&M, not existing station equipment. Hybrid storage adds its priced equipment once, with installed compound/protection, disposal and replacement costs still unquoted. Twenty-year indexed discounted cost is a **partial comparison**, not lifecycle bankability; no contract or tariffs are accepted. Unserved demand means the assumed service is unmet: no unchanged fares are credited to that service.

Aggregate connection and storage pooling are optimistic and unestablished. This screen does not supply site-specific wheeling rights or instantaneous charger arrival/queue proof. Measured multi-year weather/soiling, per-site feeder/charger duty, auxiliary loads, storage cycling/degradation, grid outages and binding backup contracts must be replayed before changing the funding programme's electricity allowance or selecting an ownership option.
