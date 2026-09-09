# dar-es-salaam depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The configured policy is distributed overnight stabling at powered stations, with coordinated morning starts. Main-depot bays serve maintenance and defective trains. The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-2-0122-0312-s058983 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-2684-1282-s000000 | line-1 | 51 | 5,661.0 | 6,171.0 | unverified |
| line-1-0658-0927-s054952 | line-1 | 51 | 5,661.0 | 6,171.0 | unverified |
| line-2-1887-1610-s000000 | line-2 | 54 | 5,994.0 | 6,534.0 | unverified |
| line-2-0122-0312-s058983 | line-2 | 54 | 5,994.0 | 6,534.0 | unverified |
| line-3-1308-0642-s000000 | line-3 | 48 | 5,328.0 | 5,808.0 | unverified |
| line-3-2266-2434-s049040 | line-3 | 47 | 5,217.0 | 5,687.0 | unverified |
| line-4-0590-1073-s000000 | line-4 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-4-2367-0715-s048042 | line-4 | 42 | 4,662.0 | 5,082.0 | unverified |
| line-5-2336-0957-s000000 | line-5 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-5-1068-1254-s035918 | line-5 | 34 | 3,774.0 | 4,114.0 | unverified |
| line-6-0517-0217-s000000 | line-6 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-6-1656-0970-s039534 | line-6 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-7-1175-1257-s000000 | line-7 | 34 | 3,774.0 | 4,114.0 | unverified |
| line-7-1474-0046-s034236 | line-7 | 33 | 3,663.0 | 3,993.0 | unverified |
| line-8-1149-1240-s000000 | line-8 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-8-1975-0139-s037386 | line-8 | 34 | 3,774.0 | 4,114.0 | unverified |
| line-9-1145-0671-s006994 | line-9 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-9-1348-0449-s085243 | line-9 | 20 | 2,220.0 | 2,420.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
