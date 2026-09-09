# mandalay depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The configured policy is distributed overnight stabling at powered stations, with coordinated morning starts. Main-depot bays serve maintenance and defective trains. The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-1627-0780-s043876 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0060-0454-s000000 | line-1 | 35 | 2,625.0 | 2,975.0 | unverified |
| line-1-1627-0780-s043876 | line-1 | 35 | 2,625.0 | 2,975.0 | unverified |
| line-2-0550-0371-s000000 | line-2 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-2-1651-1074-s032265 | line-2 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-3-1588-0076-s000000 | line-3 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-3-0728-1018-s031964 | line-3 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-4-0961-0623-s000000 | line-4 | 20 | 1,500.0 | 1,700.0 | unverified |
| line-4-0159-1206-s025811 | line-4 | 20 | 1,500.0 | 1,700.0 | unverified |
| line-5-0907-1047-s000000 | line-5 | 23 | 1,725.0 | 1,955.0 | unverified |
| line-5-1610-0400-s027267 | line-5 | 22 | 1,650.0 | 1,870.0 | unverified |
| line-6-0550-0371-s000220 | line-6 | 12 | 900.0 | 1,020.0 | unverified |
| line-6-0781-0207-s054668 | line-6 | 12 | 900.0 | 1,020.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
