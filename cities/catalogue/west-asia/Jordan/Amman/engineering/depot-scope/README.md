# amman depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The configured policy is distributed overnight stabling at powered stations, with coordinated morning starts. Main-depot bays serve maintenance and defective trains. The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-2-1728-0841-s048043 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1275-0331-s000000 | line-1 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-1-0185-1639-s043984 | line-1 | 42 | 4,662.0 | 5,082.0 | unverified |
| line-2-0017-0646-s000000 | line-2 | 45 | 4,995.0 | 5,445.0 | unverified |
| line-2-1728-0841-s048043 | line-2 | 45 | 4,995.0 | 5,445.0 | unverified |
| line-3-1491-0674-s000000 | line-3 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-3-0384-0624-s030305 | line-3 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-4-0444-0878-s000000 | line-4 | 23 | 2,553.0 | 2,783.0 | unverified |
| line-4-1333-0930-s024013 | line-4 | 22 | 2,442.0 | 2,662.0 | unverified |
| line-5-0516-0076-s000000 | line-5 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-5-1178-1169-s032369 | line-5 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-6-0573-1433-s000000 | line-6 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-6-0812-0079-s034854 | line-6 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-7-0752-1259-s000000 | line-7 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-7-0377-0204-s028375 | line-7 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-8-0090-1437-s000000 | line-8 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-8-1020-0487-s034330 | line-8 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-9-0708-0390-s000000 | line-9 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-9-0793-0330-s079545 | line-9 | 19 | 2,109.0 | 2,299.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
