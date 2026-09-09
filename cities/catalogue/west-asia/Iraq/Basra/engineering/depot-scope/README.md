# basra depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to declared depots. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-3-1128-0589-s046101 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1783-1156-s000000 | line-1 | 42 | 4,662.0 | 5,082.0 | unverified |
| line-1-0080-0724-s045164 | line-1 | 41 | 4,551.0 | 4,961.0 | unverified |
| line-2-1620-1366-s000000 | line-2 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-2-0839-1170-s020211 | line-2 | 19 | 2,109.0 | 2,299.0 | unverified |
| line-3-1713-2270-s000000 | line-3 | 44 | 4,884.0 | 5,324.0 | unverified |
| line-3-1128-0589-s046101 | line-3 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-4-1070-0777-s000000 | line-4 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-4-1405-2361-s037340 | line-4 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-5-2152-0348-s000000 | line-5 | 38 | 4,218.0 | 4,598.0 | unverified |
| line-5-1179-1578-s039866 | line-5 | 38 | 4,218.0 | 4,598.0 | unverified |
| line-6-1003-0997-s000000 | line-6 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-6-2118-0683-s029836 | line-6 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-7-0731-0954-s000000 | line-7 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-7-0803-0946-s085345 | line-7 | 19 | 2,109.0 | 2,299.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
