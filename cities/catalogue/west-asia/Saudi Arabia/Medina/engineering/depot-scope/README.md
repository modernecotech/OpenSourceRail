# medina depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The configured policy is distributed overnight stabling at powered stations, with coordinated morning starts. Main-depot bays serve maintenance and defective trains. The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-1509-1385-s034203 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0485-0427-s000000 | line-1 | 27 | 2,025.0 | 2,295.0 | unverified |
| line-1-1509-1385-s034203 | line-1 | 27 | 2,025.0 | 2,295.0 | unverified |
| line-2-1235-0549-s000000 | line-2 | 19 | 1,425.0 | 1,615.0 | unverified |
| line-2-0677-1193-s021254 | line-2 | 18 | 1,350.0 | 1,530.0 | unverified |
| line-3-0762-0521-s000000 | line-3 | 16 | 1,200.0 | 1,360.0 | unverified |
| line-3-1406-1008-s020656 | line-3 | 16 | 1,200.0 | 1,360.0 | unverified |
| line-4-0552-1137-s000000 | line-4 | 19 | 1,425.0 | 1,615.0 | unverified |
| line-4-1079-0263-s024173 | line-4 | 18 | 1,350.0 | 1,530.0 | unverified |
| line-5-0623-0725-s000000 | line-5 | 14 | 1,050.0 | 1,190.0 | unverified |
| line-5-0938-1459-s018738 | line-5 | 14 | 1,050.0 | 1,190.0 | unverified |
| line-6-0805-1346-s000000 | line-6 | 12 | 900.0 | 1,020.0 | unverified |
| line-6-0815-1252-s058268 | line-6 | 12 | 900.0 | 1,020.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
