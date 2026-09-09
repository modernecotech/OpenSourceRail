# kampala depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to storage on its own line. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0931-0035-s036071 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0447-1356-s000000 | line-1 | 29 | 2,175.0 | 2,465.0 | unverified |
| line-1-0931-0035-s036071 | line-1 | 28 | 2,100.0 | 2,380.0 | unverified |
| line-2-1014-0784-s000000 | line-2 | 23 | 1,725.0 | 1,955.0 | unverified |
| line-2-0080-0474-s028431 | line-2 | 22 | 1,650.0 | 1,870.0 | unverified |
| line-3-1033-0576-s000000 | line-3 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-3-0014-0908-s031639 | line-3 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-4-0292-0154-s000000 | line-4 | 26 | 1,950.0 | 2,210.0 | unverified |
| line-4-0772-1138-s031810 | line-4 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-5-0300-0965-s000000 | line-5 | 23 | 1,725.0 | 1,955.0 | unverified |
| line-5-1234-0666-s028451 | line-5 | 22 | 1,650.0 | 1,870.0 | unverified |
| line-6-0625-0328-s000000 | line-6 | 13 | 975.0 | 1,105.0 | unverified |
| line-6-0713-0336-s063143 | line-6 | 13 | 975.0 | 1,105.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
