# hama depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0708-0757-s022781 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0768-0539-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-0581-0072-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0427-0606-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0587-0751-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0194-0142-s000000 | line-1 | 39 | 1,930.5 | 2,320.5 | unverified |
| line-1-0708-0757-s022781 | line-1 | 39 | 1,930.5 | 2,320.5 | unverified |
| line-2-0768-0539-s000000 | line-2 | 17 | 841.5 | 1,011.5 | unverified |
| line-2-0313-0629-s009846 | line-2 | 17 | 841.5 | 1,011.5 | unverified |
| line-3-0581-0072-s000000 | line-3 | 36 | 1,782.0 | 2,142.0 | unverified |
| line-3-0586-0750-s021278 | line-3 | 36 | 1,782.0 | 2,142.0 | unverified |
| line-4-0427-0606-s000000 | line-4 | 15 | 742.5 | 892.5 | unverified |
| line-4-0187-0438-s009101 | line-4 | 15 | 742.5 | 892.5 | unverified |
| line-5-0587-0751-s000000 | line-5 | 8 | 396.0 | 476.0 | unverified |
| line-5-0587-0833-s004024 | line-5 | 7 | 346.5 | 416.5 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
