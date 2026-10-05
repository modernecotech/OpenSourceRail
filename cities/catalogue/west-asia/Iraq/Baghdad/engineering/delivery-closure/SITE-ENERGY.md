# Chronological site-limited energy and installed upgrades

Each station retains its own storage capacity/power and grid limit. Timetable train-km allocate duty between lines; installed charger kW allocate duty within a line. **This is a synthetic allocation, not measured charger events or a queue/feeder acceptance test.** The utility plant is allocated by duty, on-site PV has no wheeling loss, and utility PV has the explicit loss/charge. Each node conserves hourly energy and preserves losses, curtailment, shortages and SoC.

| Weather | Imports GWh | Unserved GWh | Firm energy services USD m/year | Required grid upgrade MW | Charger overload MW |
| --- | --- | --- | --- | --- | --- |
| reference | 859.4 | 2.2 | 127.820 | 77.824 | 129.320 |
| poor | 976.1 | 4.0 | 135.683 | 81.190 | 129.320 |
| aged10 | 877.6 | 2.3 | 129.645 | 77.824 | 129.320 |

The firm-service cash sensitivity buys unmet energy and pays the increased connection charges. It **requires physical connection and charger upgrades whose capital is unpriced**. It does not claim a trip can be served by paying a bill. [Site totals](site-energy.json) and reference line-hourly ledgers expose every node requirement. Whole-grid pooling is removed; within-line duty allocation, site transformer/feeder limits, rights/outages, charging times, installed storage ageing and weather still need measurements. Original annual-netting finance remains unchanged, with no export income or energy ownership proceeds invented.

[All 28 aggregate shortage hours](aggregate-reference-shortage-hours.csv) remain an explicit pooled comparator. [Site-specific shortage hours](energy-site-shortage-hours.csv) expose grid/charger limits, opening/closing stored energy, local PV and remote generation before wheeling. Local PV never incurs remote wheeling losses/charges. The installed-throughput case reduces fare, station and additional commercial receipts; it is an energy upper bound, not a validated achieved timetable.
