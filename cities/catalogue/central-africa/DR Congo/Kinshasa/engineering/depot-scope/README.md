# kinshasa depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0368-0684-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-1138-1729-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-1310-1498-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-1515-1008-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0979-2057-s047615 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-1261-1371-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-0255-1502-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-0711-1576-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-9-0578-0688-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0368-0684-s000000 | line-1 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-1-1332-1739-s032412 | line-1 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-2-1138-1729-s000000 | line-2 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-2-0231-0783-s030637 | line-2 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-3-1310-1498-s000000 | line-3 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-3-0746-0242-s030514 | line-3 | 28 | 3,108.0 | 3,388.0 | unverified |
| line-4-1515-1008-s000000 | line-4 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-4-0242-1021-s026943 | line-4 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-5-1628-0002-s000000 | line-5 | 46 | 5,106.0 | 5,566.0 | unverified |
| line-5-0979-2057-s047615 | line-5 | 45 | 4,995.0 | 5,445.0 | unverified |
| line-6-1261-1371-s000000 | line-6 | 38 | 4,218.0 | 4,598.0 | unverified |
| line-6-0165-0034-s038864 | line-6 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-7-0255-1502-s000000 | line-7 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-7-1673-0600-s037290 | line-7 | 34 | 3,774.0 | 4,114.0 | unverified |
| line-8-0711-1576-s000000 | line-8 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-8-1198-0078-s034492 | line-8 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-9-0578-0688-s000000 | line-9 | 18 | 1,998.0 | 2,178.0 | unverified |
| line-9-0727-0651-s070192 | line-9 | 18 | 1,998.0 | 2,178.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
