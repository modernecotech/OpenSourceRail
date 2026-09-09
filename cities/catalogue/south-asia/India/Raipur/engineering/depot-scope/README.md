# raipur depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The configured policy is distributed overnight stabling at powered stations, with coordinated morning starts. Main-depot bays serve maintenance and defective trains. The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0842-0215-s034502 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0813-1560-s000000 | line-1 | 27 | 2,025.0 | 2,295.0 | unverified |
| line-1-0842-0215-s034502 | line-1 | 27 | 2,025.0 | 2,295.0 | unverified |
| line-2-1246-0805-s000000 | line-2 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-2-0060-1016-s031728 | line-2 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-3-0651-1181-s000000 | line-3 | 13 | 975.0 | 1,105.0 | unverified |
| line-3-0738-0583-s014603 | line-3 | 12 | 900.0 | 1,020.0 | unverified |
| line-4-1246-1468-s000000 | line-4 | 17 | 1,275.0 | 1,445.0 | unverified |
| line-4-0915-0625-s020629 | line-4 | 17 | 1,275.0 | 1,445.0 | unverified |
| line-5-0321-1192-s000000 | line-5 | 19 | 1,425.0 | 1,615.0 | unverified |
| line-5-1291-0954-s023732 | line-5 | 19 | 1,425.0 | 1,615.0 | unverified |
| line-6-0882-1189-s000000 | line-6 | 7 | 525.0 | 595.0 | unverified |
| line-6-0982-1138-s028056 | line-6 | 6 | 450.0 | 510.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
