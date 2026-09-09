# kabul depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to storage on its own line. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-2-0487-0134-s033687 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0477-1068-s000000 | line-1 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-1-1095-0224-s029570 | line-1 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-2-1175-1030-s000000 | line-2 | 33 | 3,663.0 | 3,993.0 | unverified |
| line-2-0487-0134-s033687 | line-2 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-3-0934-0177-s000000 | line-3 | 22 | 2,442.0 | 2,662.0 | unverified |
| line-3-0517-0872-s022992 | line-3 | 21 | 2,331.0 | 2,541.0 | unverified |
| line-4-1312-0202-s000000 | line-4 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-4-0792-1249-s029843 | line-4 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-5-0688-0221-s000000 | line-5 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-5-1016-1511-s030804 | line-5 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-6-1185-1306-s000000 | line-6 | 21 | 2,331.0 | 2,541.0 | unverified |
| line-6-0664-0757-s020771 | line-6 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-7-0736-0328-s000000 | line-7 | 14 | 1,554.0 | 1,694.0 | unverified |
| line-7-0933-0293-s055597 | line-7 | 14 | 1,554.0 | 1,694.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
