# surabaya depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-1195-0998-s045429 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0151-1409-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-0460-0990-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0448-0639-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0914-1114-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-1013-0284-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-0517-0126-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-0723-0958-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-9-0705-0391-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0001-0684-s000000 | line-1 | 48 | 5,328.0 | 5,808.0 | unverified |
| line-1-1195-0998-s045429 | line-1 | 47 | 5,217.0 | 5,687.0 | unverified |
| line-2-0151-1409-s000000 | line-2 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-2-1193-0642-s036053 | line-2 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-3-0460-0990-s000000 | line-3 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-3-1433-0106-s031352 | line-3 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-4-0448-0639-s000000 | line-4 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-4-1428-0708-s028072 | line-4 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-5-0914-1114-s000000 | line-5 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-5-0210-0013-s035162 | line-5 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-6-1013-0284-s000000 | line-6 | 23 | 2,553.0 | 2,783.0 | unverified |
| line-6-0782-1168-s019805 | line-6 | 23 | 2,553.0 | 2,783.0 | unverified |
| line-7-0517-0126-s000000 | line-7 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-7-0673-1022-s019732 | line-7 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-8-0723-0958-s000000 | line-8 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-8-0866-0175-s018067 | line-8 | 19 | 2,109.0 | 2,299.0 | unverified |
| line-9-0705-0391-s000000 | line-9 | 18 | 1,998.0 | 2,178.0 | unverified |
| line-9-0844-0398-s055434 | line-9 | 17 | 1,887.0 | 2,057.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
