# bamako depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The configured policy is distributed overnight stabling at powered stations, with coordinated morning starts. Main-depot bays serve maintenance and defective trains. The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-1489-1327-s043508 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0032-0412-s000000 | line-1 | 36 | 2,700.0 | 3,060.0 | unverified |
| line-1-1489-1327-s043508 | line-1 | 36 | 2,700.0 | 3,060.0 | unverified |
| line-2-1289-0508-s000000 | line-2 | 21 | 1,575.0 | 1,785.0 | unverified |
| line-2-0547-1266-s027794 | line-2 | 20 | 1,500.0 | 1,700.0 | unverified |
| line-3-1312-0785-s000000 | line-3 | 16 | 1,200.0 | 1,360.0 | unverified |
| line-3-0729-1227-s020025 | line-3 | 15 | 1,125.0 | 1,275.0 | unverified |
| line-4-0959-0592-s000000 | line-4 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-4-1408-1726-s030717 | line-4 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-5-0599-1002-s000000 | line-5 | 18 | 1,350.0 | 1,530.0 | unverified |
| line-5-1531-0939-s023121 | line-5 | 18 | 1,350.0 | 1,530.0 | unverified |
| line-6-0346-0737-s000000 | line-6 | 13 | 975.0 | 1,105.0 | unverified |
| line-6-0563-0755-s061573 | line-6 | 12 | 900.0 | 1,020.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
