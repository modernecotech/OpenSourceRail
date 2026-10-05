# tunis depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-1235-1603-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-1514-0979-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-0505-1671-s038159 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-1271-1266-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0862-0502-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1235-1603-s000000 | line-1 | 28 | 2,100.0 | 2,380.0 | unverified |
| line-1-0749-0148-s033481 | line-1 | 28 | 2,100.0 | 2,380.0 | unverified |
| line-2-1514-0979-s000000 | line-2 | 20 | 1,500.0 | 1,700.0 | unverified |
| line-2-0383-1100-s024826 | line-2 | 19 | 1,425.0 | 1,615.0 | unverified |
| line-3-1203-0078-s000000 | line-3 | 31 | 2,325.0 | 2,635.0 | unverified |
| line-3-0505-1671-s038159 | line-3 | 30 | 2,250.0 | 2,550.0 | unverified |
| line-4-1271-1266-s000000 | line-4 | 23 | 1,725.0 | 1,955.0 | unverified |
| line-4-0349-0436-s029262 | line-4 | 23 | 1,725.0 | 1,955.0 | unverified |
| line-5-0862-0502-s000000 | line-5 | 14 | 1,050.0 | 1,190.0 | unverified |
| line-5-0951-0573-s069229 | line-5 | 14 | 1,050.0 | 1,190.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
