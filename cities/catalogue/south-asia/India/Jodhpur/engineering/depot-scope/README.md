# jodhpur depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-1305-0919-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0875-0490-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-1418-0634-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0628-0549-s024676 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0565-0643-s001051 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1305-0919-s000000 | line-1 | 23 | 1,725.0 | 1,955.0 | unverified |
| line-1-0195-0871-s024219 | line-1 | 22 | 1,650.0 | 1,870.0 | unverified |
| line-2-0875-0490-s000000 | line-2 | 21 | 1,575.0 | 1,785.0 | unverified |
| line-2-0348-1228-s020286 | line-2 | 20 | 1,500.0 | 1,700.0 | unverified |
| line-3-1418-0634-s000000 | line-3 | 20 | 1,500.0 | 1,700.0 | unverified |
| line-3-0542-0657-s019360 | line-3 | 20 | 1,500.0 | 1,700.0 | unverified |
| line-4-1299-1410-s000000 | line-4 | 21 | 1,575.0 | 1,785.0 | unverified |
| line-4-0628-0549-s024676 | line-4 | 20 | 1,500.0 | 1,700.0 | unverified |
| line-5-0565-0643-s001051 | line-5 | 11 | 825.0 | 935.0 | unverified |
| line-5-0631-0622-s045868 | line-5 | 10 | 750.0 | 850.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
