# san-salvador depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to declared depots. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-4-0191-1582-s040358 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0934-0200-s000000 | line-1 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-1-0824-1345-s030191 | line-1 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-2-0201-0997-s000000 | line-2 | 29 | 2,175.0 | 2,465.0 | unverified |
| line-2-1460-0306-s036885 | line-2 | 28 | 2,100.0 | 2,380.0 | unverified |
| line-3-1477-1595-s000000 | line-3 | 30 | 2,250.0 | 2,550.0 | unverified |
| line-3-0613-0383-s038450 | line-3 | 29 | 2,175.0 | 2,465.0 | unverified |
| line-4-1113-0355-s000000 | line-4 | 30 | 2,250.0 | 2,550.0 | unverified |
| line-4-0191-1582-s040358 | line-4 | 30 | 2,250.0 | 2,550.0 | unverified |
| line-5-1273-0935-s000000 | line-5 | 27 | 2,025.0 | 2,295.0 | unverified |
| line-5-0069-0428-s034241 | line-5 | 27 | 2,025.0 | 2,295.0 | unverified |
| line-6-0500-0402-s000000 | line-6 | 15 | 1,125.0 | 1,275.0 | unverified |
| line-6-0613-0383-s073920 | line-6 | 15 | 1,125.0 | 1,275.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
