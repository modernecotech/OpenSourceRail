# marrakech depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The configured policy is distributed overnight stabling at powered stations, with coordinated morning starts. Main-depot bays serve maintenance and defective trains. The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-5-0102-0195-s034036 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0666-0472-s000000 | line-1 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-1-1414-1431-s029160 | line-1 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-2-0176-1241-s000000 | line-2 | 23 | 1,725.0 | 1,955.0 | unverified |
| line-2-0992-0531-s027205 | line-2 | 23 | 1,725.0 | 1,955.0 | unverified |
| line-3-0821-0410-s000000 | line-3 | 21 | 1,575.0 | 1,785.0 | unverified |
| line-3-0712-1395-s026429 | line-3 | 20 | 1,500.0 | 1,700.0 | unverified |
| line-4-1429-0421-s000000 | line-4 | 23 | 1,725.0 | 1,955.0 | unverified |
| line-4-0365-0834-s027223 | line-4 | 22 | 1,650.0 | 1,870.0 | unverified |
| line-5-1330-0747-s000000 | line-5 | 27 | 2,025.0 | 2,295.0 | unverified |
| line-5-0102-0195-s034036 | line-5 | 27 | 2,025.0 | 2,295.0 | unverified |
| line-6-0721-0519-s002704 | line-6 | 10 | 750.0 | 850.0 | unverified |
| line-6-0821-0410-s048793 | line-6 | 10 | 750.0 | 850.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
