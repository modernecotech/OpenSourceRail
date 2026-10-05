# kinshasa depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0368-0684-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-1138-1729-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-1310-1498-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-1515-1008-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-1628-0002-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-1268-1346-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-1673-0600-s091683 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-0711-1576-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-9-0547-0718-s000986 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0368-0684-s000000 | line-1 | 114 | 12,654.0 | 13,794.0 | unverified |
| line-1-1332-1739-s062822 | line-1 | 114 | 12,654.0 | 13,794.0 | unverified |
| line-2-1138-1729-s000000 | line-2 | 121 | 13,431.0 | 14,641.0 | unverified |
| line-2-0231-0783-s066912 | line-2 | 120 | 13,320.0 | 14,520.0 | unverified |
| line-3-1310-1498-s000000 | line-3 | 54 | 5,994.0 | 6,534.0 | unverified |
| line-3-0746-0242-s031845 | line-3 | 54 | 5,994.0 | 6,534.0 | unverified |
| line-4-1515-1008-s000000 | line-4 | 113 | 12,543.0 | 13,673.0 | unverified |
| line-4-0242-1021-s064092 | line-4 | 112 | 12,432.0 | 13,552.0 | unverified |
| line-5-1628-0002-s000000 | line-5 | 49 | 5,439.0 | 5,929.0 | unverified |
| line-5-0979-2057-s048631 | line-5 | 48 | 5,328.0 | 5,808.0 | unverified |
| line-6-1268-1346-s000000 | line-6 | 86 | 9,546.0 | 10,406.0 | unverified |
| line-6-0165-0034-s049382 | line-6 | 86 | 9,546.0 | 10,406.0 | unverified |
| line-7-0255-1502-s000000 | line-7 | 108 | 11,988.0 | 13,068.0 | unverified |
| line-7-1673-0600-s091683 | line-7 | 107 | 11,877.0 | 12,947.0 | unverified |
| line-8-0711-1576-s000000 | line-8 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-8-1198-0078-s035993 | line-8 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-9-0547-0718-s000986 | line-9 | 42 | 4,662.0 | 5,082.0 | unverified |
| line-9-0582-0685-s106574 | line-9 | 41 | 4,551.0 | 4,961.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
