# colombo depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to declared depots. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-3-1474-0859-s043860 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1104-0254-s000000 | line-1 | 33 | 3,663.0 | 3,993.0 | unverified |
| line-1-0325-1220-s036554 | line-1 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-2-0308-0299-s000000 | line-2 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-2-1273-0668-s029072 | line-2 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-3-0048-0462-s000000 | line-3 | 41 | 4,551.0 | 4,961.0 | unverified |
| line-3-1474-0859-s043860 | line-3 | 41 | 4,551.0 | 4,961.0 | unverified |
| line-4-0566-1078-s000000 | line-4 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-4-1215-0316-s027466 | line-4 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-5-0636-0164-s000000 | line-5 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-5-1132-1228-s030139 | line-5 | 28 | 3,108.0 | 3,388.0 | unverified |
| line-6-0155-1049-s000000 | line-6 | 28 | 3,108.0 | 3,388.0 | unverified |
| line-6-0839-0174-s029413 | line-6 | 28 | 3,108.0 | 3,388.0 | unverified |
| line-7-0793-0161-s000000 | line-7 | 25 | 2,775.0 | 3,025.0 | unverified |
| line-7-1339-0954-s027380 | line-7 | 25 | 2,775.0 | 3,025.0 | unverified |
| line-8-0578-0200-s000000 | line-8 | 24 | 2,664.0 | 2,904.0 | unverified |
| line-8-1402-0446-s023779 | line-8 | 23 | 2,553.0 | 2,783.0 | unverified |
| line-9-0578-0200-s000355 | line-9 | 17 | 1,887.0 | 2,057.0 | unverified |
| line-9-0636-0164-s072009 | line-9 | 17 | 1,887.0 | 2,057.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
