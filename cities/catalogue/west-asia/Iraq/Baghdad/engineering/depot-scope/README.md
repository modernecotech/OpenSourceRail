# baghdad depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The configured policy is distributed overnight stabling at powered stations, with coordinated morning starts. Main-depot bays serve maintenance and defective trains. The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0325-0249-s058110 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1887-2051-s000000 | line-1 | 51 | 5,661.0 | 6,171.0 | unverified |
| line-1-0325-0249-s058110 | line-1 | 51 | 5,661.0 | 6,171.0 | unverified |
| line-2-0680-0190-s000000 | line-2 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-2-1746-1584-s045806 | line-2 | 42 | 4,662.0 | 5,082.0 | unverified |
| line-3-2322-0251-s000000 | line-3 | 53 | 5,883.0 | 6,413.0 | unverified |
| line-3-0492-1526-s055088 | line-3 | 52 | 5,772.0 | 6,292.0 | unverified |
| line-4-1066-0011-s000000 | line-4 | 51 | 5,661.0 | 6,171.0 | unverified |
| line-4-1069-2206-s052920 | line-4 | 50 | 5,550.0 | 6,050.0 | unverified |
| line-5-0092-0824-s000000 | line-5 | 41 | 4,551.0 | 4,961.0 | unverified |
| line-5-1711-1271-s043123 | line-5 | 40 | 4,440.0 | 4,840.0 | unverified |
| line-6-0578-1225-s000000 | line-6 | 45 | 4,995.0 | 5,445.0 | unverified |
| line-6-2399-0681-s047232 | line-6 | 45 | 4,995.0 | 5,445.0 | unverified |
| line-7-1333-0171-s000000 | line-7 | 52 | 5,772.0 | 6,292.0 | unverified |
| line-7-0677-2304-s056905 | line-7 | 51 | 5,661.0 | 6,171.0 | unverified |
| line-8-1329-1654-s000000 | line-8 | 34 | 3,774.0 | 4,114.0 | unverified |
| line-8-0172-0482-s036358 | line-8 | 33 | 3,663.0 | 3,993.0 | unverified |
| line-9-1077-0587-s000000 | line-9 | 25 | 2,775.0 | 3,025.0 | unverified |
| line-9-1170-0574-s103690 | line-9 | 25 | 2,775.0 | 3,025.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
