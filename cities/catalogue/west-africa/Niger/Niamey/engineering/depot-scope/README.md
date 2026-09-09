# niamey depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to declared depots. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0339-0496-s027252 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1220-0898-s000000 | line-1 | 22 | 1,650.0 | 1,870.0 | unverified |
| line-1-0339-0496-s027252 | line-1 | 21 | 1,575.0 | 1,785.0 | unverified |
| line-2-0548-0307-s000000 | line-2 | 15 | 1,125.0 | 1,275.0 | unverified |
| line-2-0700-1022-s018911 | line-2 | 15 | 1,125.0 | 1,275.0 | unverified |
| line-3-0478-0840-s000000 | line-3 | 15 | 1,125.0 | 1,275.0 | unverified |
| line-3-0860-0351-s016772 | line-3 | 14 | 1,050.0 | 1,190.0 | unverified |
| line-4-0712-0343-s000000 | line-4 | 16 | 1,200.0 | 1,360.0 | unverified |
| line-4-0929-1179-s021666 | line-4 | 16 | 1,200.0 | 1,360.0 | unverified |
| line-5-0292-0204-s000000 | line-5 | 16 | 1,200.0 | 1,360.0 | unverified |
| line-5-0934-0669-s019493 | line-5 | 15 | 1,125.0 | 1,275.0 | unverified |
| line-6-0535-0421-s000849 | line-6 | 11 | 825.0 | 935.0 | unverified |
| line-6-0595-0381-s052652 | line-6 | 10 | 750.0 | 850.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
