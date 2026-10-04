# baghdad depot scope reconciliation

<!-- OSR CURRENT SCOPE CONTEXT -->
> **Original catalogue or earlier scope reference.** The figures and policies below retain their original assumptions; they are not the latest Baghdad staffing, depot, procurement or funding basis. See the [current Baghdad recalculation](../programme-recalculation/README.md) and [current city summary](../../README.md). National/portfolio totals have not been repriced with that conditional Baghdad option.
<!-- END OSR CURRENT SCOPE CONTEXT -->

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to storage on its own line. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-2-0595-0296-s052851 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-2500-0775-s000000 | line-1 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-1-0166-0866-s049067 | line-1 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-2-1987-2192-s000000 | line-2 | 51 | 5,661.0 | 6,171.0 | unverified |
| line-2-0595-0296-s052851 | line-2 | 50 | 5,550.0 | 6,050.0 | unverified |
| line-3-2271-1120-s000000 | line-3 | 49 | 5,439.0 | 5,929.0 | unverified |
| line-3-0151-1637-s049496 | line-3 | 48 | 5,328.0 | 5,808.0 | unverified |
| line-4-0146-0199-s000000 | line-4 | 40 | 4,440.0 | 4,840.0 | unverified |
| line-4-1246-1628-s042068 | line-4 | 40 | 4,440.0 | 4,840.0 | unverified |
| line-5-1199-0260-s000000 | line-5 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-5-0677-2304-s047321 | line-5 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-6-2322-0251-s000000 | line-6 | 50 | 5,550.0 | 6,050.0 | unverified |
| line-6-0495-1669-s052503 | line-6 | 50 | 5,550.0 | 6,050.0 | unverified |
| line-7-1069-2206-s000000 | line-7 | 40 | 4,440.0 | 4,840.0 | unverified |
| line-7-1531-0418-s039957 | line-7 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-8-2231-1783-s000000 | line-8 | 45 | 4,995.0 | 5,445.0 | unverified |
| line-8-0785-0290-s047849 | line-8 | 45 | 4,995.0 | 5,445.0 | unverified |
| line-9-0678-0582-s000000 | line-9 | 22 | 2,442.0 | 2,662.0 | unverified |
| line-9-0819-0573-s090161 | line-9 | 21 | 2,331.0 | 2,541.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
