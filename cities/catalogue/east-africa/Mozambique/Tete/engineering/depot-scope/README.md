# tete depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to storage on its own line. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0851-0539-s014495 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0297-0416-s000000 | line-1 | 15 | 742.5 | 892.5 | unverified |
| line-1-0851-0539-s014495 | line-1 | 15 | 742.5 | 892.5 | unverified |
| line-2-0745-0787-s000000 | line-2 | 14 | 693.0 | 833.0 | unverified |
| line-2-0329-0468-s012615 | line-2 | 13 | 643.5 | 773.5 | unverified |
| line-3-0533-0514-s000000 | line-3 | 12 | 594.0 | 714.0 | unverified |
| line-3-0262-0845-s010756 | line-3 | 12 | 594.0 | 714.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
