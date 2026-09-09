# nairobi depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The configured policy is distributed overnight stabling at powered stations, with coordinated morning starts. Main-depot bays serve maintenance and defective trains. The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-6-0557-0100-s059932 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0098-2227-s000000 | line-1 | 54 | 5,994.0 | 6,534.0 | unverified |
| line-1-1731-0592-s057880 | line-1 | 53 | 5,883.0 | 6,413.0 | unverified |
| line-2-1300-2489-s000000 | line-2 | 51 | 5,661.0 | 6,171.0 | unverified |
| line-2-1330-0405-s054501 | line-2 | 51 | 5,661.0 | 6,171.0 | unverified |
| line-3-0693-0971-s000000 | line-3 | 48 | 5,328.0 | 5,808.0 | unverified |
| line-3-2435-1699-s052240 | line-3 | 48 | 5,328.0 | 5,808.0 | unverified |
| line-4-1104-1663-s000000 | line-4 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-4-1135-0336-s032542 | line-4 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-5-0599-1609-s000000 | line-5 | 44 | 4,884.0 | 5,324.0 | unverified |
| line-5-1668-0072-s046082 | line-5 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-6-2190-1920-s000000 | line-6 | 54 | 5,994.0 | 6,534.0 | unverified |
| line-6-0557-0100-s059932 | line-6 | 54 | 5,994.0 | 6,534.0 | unverified |
| line-7-0263-0206-s000000 | line-7 | 52 | 5,772.0 | 6,292.0 | unverified |
| line-7-1684-1761-s053920 | line-7 | 52 | 5,772.0 | 6,292.0 | unverified |
| line-8-1893-0736-s000000 | line-8 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-8-0242-1201-s043584 | line-8 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-9-1102-0512-s000000 | line-9 | 24 | 2,664.0 | 2,904.0 | unverified |
| line-9-1191-0478-s102703 | line-9 | 24 | 2,664.0 | 2,904.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
