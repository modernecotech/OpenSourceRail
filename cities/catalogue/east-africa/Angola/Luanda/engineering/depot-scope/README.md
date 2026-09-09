# luanda depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The configured policy is distributed overnight stabling at powered stations, with coordinated morning starts. Main-depot bays serve maintenance and defective trains. The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-2076-0245-s058632 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0546-1911-s000000 | line-1 | 54 | 5,994.0 | 6,534.0 | unverified |
| line-1-2076-0245-s058632 | line-1 | 54 | 5,994.0 | 6,534.0 | unverified |
| line-2-1718-0350-s000000 | line-2 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-2-0979-1276-s029998 | line-2 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-3-2172-0503-s000000 | line-3 | 40 | 4,440.0 | 4,840.0 | unverified |
| line-3-0975-1651-s043872 | line-3 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-4-0945-0840-s000000 | line-4 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-4-2361-1682-s042563 | line-4 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-5-2059-2085-s000000 | line-5 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-5-1257-0596-s039943 | line-5 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-6-0962-1023-s000000 | line-6 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-6-2212-0908-s031133 | line-6 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-7-1601-2132-s000000 | line-7 | 33 | 3,663.0 | 3,993.0 | unverified |
| line-7-1169-0807-s033940 | line-7 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-8-1031-2002-s000000 | line-8 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-8-1379-0592-s032879 | line-8 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-9-1112-1616-s000000 | line-9 | 19 | 2,109.0 | 2,299.0 | unverified |
| line-9-1152-1480-s074278 | line-9 | 18 | 1,998.0 | 2,178.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
