# damanhur depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0370-0539-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0647-1100-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-0354-0950-s021698 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0435-0518-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0611-0500-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0370-0539-s000000 | line-1 | 16 | 792.0 | 952.0 | unverified |
| line-1-0731-0566-s009405 | line-1 | 16 | 792.0 | 952.0 | unverified |
| line-2-0647-1100-s000000 | line-2 | 26 | 1,287.0 | 1,547.0 | unverified |
| line-2-0526-0378-s016176 | line-2 | 26 | 1,287.0 | 1,547.0 | unverified |
| line-3-0740-0226-s000000 | line-3 | 34 | 1,683.0 | 2,023.0 | unverified |
| line-3-0354-0950-s021698 | line-3 | 34 | 1,683.0 | 2,023.0 | unverified |
| line-4-0435-0518-s000000 | line-4 | 12 | 594.0 | 714.0 | unverified |
| line-4-0241-0290-s006655 | line-4 | 11 | 544.5 | 654.5 | unverified |
| line-5-0611-0500-s000000 | line-5 | 8 | 396.0 | 476.0 | unverified |
| line-5-0811-0514-s004315 | line-5 | 7 | 346.5 | 416.5 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
