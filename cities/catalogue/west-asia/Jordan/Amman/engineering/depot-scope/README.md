# amman depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-1275-0331-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-1728-0841-s042426 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-1491-0674-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0444-0878-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0516-0076-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-0573-1433-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-0751-1260-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-0090-1437-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-9-0679-0418-s000900 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1275-0331-s000000 | line-1 | 38 | 4,218.0 | 4,598.0 | unverified |
| line-1-0185-1639-s039411 | line-1 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-2-0017-0646-s000000 | line-2 | 41 | 4,551.0 | 4,961.0 | unverified |
| line-2-1728-0841-s042426 | line-2 | 40 | 4,440.0 | 4,840.0 | unverified |
| line-3-1491-0674-s000000 | line-3 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-3-0384-0626-s022957 | line-3 | 25 | 2,775.0 | 3,025.0 | unverified |
| line-4-0444-0878-s000000 | line-4 | 23 | 2,553.0 | 2,783.0 | unverified |
| line-4-1333-0931-s018231 | line-4 | 22 | 2,442.0 | 2,662.0 | unverified |
| line-5-0516-0076-s000000 | line-5 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-5-1191-1175-s029381 | line-5 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-6-0573-1433-s000000 | line-6 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-6-0812-0079-s032473 | line-6 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-7-0751-1260-s000000 | line-7 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-7-0377-0204-s024922 | line-7 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-8-0090-1437-s000000 | line-8 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-8-1020-0487-s029048 | line-8 | 28 | 3,108.0 | 3,388.0 | unverified |
| line-9-0679-0418-s000900 | line-9 | 19 | 2,109.0 | 2,299.0 | unverified |
| line-9-0723-0360-s076961 | line-9 | 19 | 2,109.0 | 2,299.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
