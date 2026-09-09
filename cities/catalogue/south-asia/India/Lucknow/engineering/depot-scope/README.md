# lucknow depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The configured policy is distributed overnight stabling at powered stations, with coordinated morning starts. Main-depot bays serve maintenance and defective trains. The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-5-0160-2295-s054414 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1245-0578-s000000 | line-1 | 45 | 4,995.0 | 5,445.0 | unverified |
| line-1-0748-2404-s048713 | line-1 | 45 | 4,995.0 | 5,445.0 | unverified |
| line-2-1898-1316-s000000 | line-2 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-2-0638-1148-s035351 | line-2 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-3-1648-0892-s000000 | line-3 | 25 | 2,775.0 | 3,025.0 | unverified |
| line-3-1161-1703-s027120 | line-3 | 25 | 2,775.0 | 3,025.0 | unverified |
| line-4-1584-1399-s000000 | line-4 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-4-0730-1374-s021949 | line-4 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-5-1603-0682-s000000 | line-5 | 52 | 5,772.0 | 6,292.0 | unverified |
| line-5-0160-2295-s054414 | line-5 | 52 | 5,772.0 | 6,292.0 | unverified |
| line-6-1771-2241-s000000 | line-6 | 47 | 5,217.0 | 5,687.0 | unverified |
| line-6-1077-0416-s048414 | line-6 | 47 | 5,217.0 | 5,687.0 | unverified |
| line-7-1292-1500-s000000 | line-7 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-7-0770-0044-s037639 | line-7 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-8-0865-0582-s003500 | line-8 | 22 | 2,442.0 | 2,662.0 | unverified |
| line-8-0995-0478-s094195 | line-8 | 21 | 2,331.0 | 2,541.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
