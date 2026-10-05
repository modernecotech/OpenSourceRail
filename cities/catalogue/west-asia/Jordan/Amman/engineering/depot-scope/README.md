# amman depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-1275-0331-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-1728-0841-s039487 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-1491-0674-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0444-0878-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0516-0076-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-0573-1433-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-0727-1241-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-0090-1437-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-9-0679-0417-s000886 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1275-0331-s000000 | line-1 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-1-0185-1639-s038449 | line-1 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-2-0017-0646-s000000 | line-2 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-2-1728-0841-s039487 | line-2 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-3-1491-0674-s000000 | line-3 | 21 | 2,331.0 | 2,541.0 | unverified |
| line-3-0414-0619-s023427 | line-3 | 21 | 2,331.0 | 2,541.0 | unverified |
| line-4-0444-0878-s000000 | line-4 | 18 | 1,998.0 | 2,178.0 | unverified |
| line-4-1330-0960-s018836 | line-4 | 18 | 1,998.0 | 2,178.0 | unverified |
| line-5-0516-0076-s000000 | line-5 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-5-1190-1197-s029520 | line-5 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-6-0573-1433-s000000 | line-6 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-6-0812-0079-s031585 | line-6 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-7-0727-1241-s000000 | line-7 | 25 | 2,775.0 | 3,025.0 | unverified |
| line-7-0377-0204-s025456 | line-7 | 24 | 2,664.0 | 2,904.0 | unverified |
| line-8-0090-1437-s000000 | line-8 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-8-1020-0487-s029048 | line-8 | 28 | 3,108.0 | 3,388.0 | unverified |
| line-9-0679-0417-s000886 | line-9 | 18 | 1,998.0 | 2,178.0 | unverified |
| line-9-0723-0360-s075199 | line-9 | 18 | 1,998.0 | 2,178.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
