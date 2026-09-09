# benin-city depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to storage on its own line. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-2-0485-0794-s028387 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0533-0917-s000000 | line-1 | 19 | 1,425.0 | 1,615.0 | unverified |
| line-1-1029-0587-s018366 | line-1 | 18 | 1,350.0 | 1,530.0 | unverified |
| line-2-1498-0986-s000000 | line-2 | 22 | 1,650.0 | 1,870.0 | unverified |
| line-2-0485-0794-s028387 | line-2 | 21 | 1,575.0 | 1,785.0 | unverified |
| line-3-0636-0695-s000000 | line-3 | 21 | 1,575.0 | 1,785.0 | unverified |
| line-3-1244-1468-s026196 | line-3 | 21 | 1,575.0 | 1,785.0 | unverified |
| line-4-0480-1452-s000000 | line-4 | 18 | 1,350.0 | 1,530.0 | unverified |
| line-4-1063-0710-s021853 | line-4 | 18 | 1,350.0 | 1,530.0 | unverified |
| line-5-0636-0695-s000748 | line-5 | 7 | 525.0 | 595.0 | unverified |
| line-5-0696-0675-s026078 | line-5 | 6 | 450.0 | 510.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
