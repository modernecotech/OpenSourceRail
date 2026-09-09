# yaounde depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to storage on its own line. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-2-0094-0108-s047440 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0366-1351-s000000 | line-1 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-1-1659-0305-s045213 | line-1 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-2-1387-1479-s000000 | line-2 | 45 | 4,995.0 | 5,445.0 | unverified |
| line-2-0094-0108-s047440 | line-2 | 45 | 4,995.0 | 5,445.0 | unverified |
| line-3-1086-1755-s000000 | line-3 | 33 | 3,663.0 | 3,993.0 | unverified |
| line-3-0792-0520-s035370 | line-3 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-4-1044-1308-s000000 | line-4 | 19 | 2,109.0 | 2,299.0 | unverified |
| line-4-0961-0525-s020399 | line-4 | 18 | 1,998.0 | 2,178.0 | unverified |
| line-5-0333-0692-s000000 | line-5 | 17 | 1,887.0 | 2,057.0 | unverified |
| line-5-0509-0708-s067175 | line-5 | 17 | 1,887.0 | 2,057.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
