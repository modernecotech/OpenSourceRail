# baghdad depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to storage on its own line. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-2-0595-0296-s052851 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-2500-0775-s000000 | line-1 | 47 | 5,217.0 | 5,687.0 | unverified |
| line-1-0166-0866-s049067 | line-1 | 47 | 5,217.0 | 5,687.0 | unverified |
| line-2-1987-2192-s000000 | line-2 | 48 | 5,328.0 | 5,808.0 | unverified |
| line-2-0595-0296-s052851 | line-2 | 48 | 5,328.0 | 5,808.0 | unverified |
| line-3-2271-1120-s000000 | line-3 | 46 | 5,106.0 | 5,566.0 | unverified |
| line-3-0151-1637-s049496 | line-3 | 46 | 5,106.0 | 5,566.0 | unverified |
| line-4-0146-0199-s000000 | line-4 | 42 | 4,662.0 | 5,082.0 | unverified |
| line-4-1230-1627-s041932 | line-4 | 41 | 4,551.0 | 4,961.0 | unverified |
| line-5-1199-0260-s000000 | line-5 | 45 | 4,995.0 | 5,445.0 | unverified |
| line-5-0677-2304-s047345 | line-5 | 45 | 4,995.0 | 5,445.0 | unverified |
| line-6-2322-0251-s000000 | line-6 | 52 | 5,772.0 | 6,292.0 | unverified |
| line-6-0495-1669-s052503 | line-6 | 52 | 5,772.0 | 6,292.0 | unverified |
| line-7-1069-2206-s000000 | line-7 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-7-1531-0418-s039957 | line-7 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-8-2231-1783-s000000 | line-8 | 46 | 5,106.0 | 5,566.0 | unverified |
| line-8-0785-0290-s048137 | line-8 | 46 | 5,106.0 | 5,566.0 | unverified |
| line-9-0608-0636-s003011 | line-9 | 24 | 2,664.0 | 2,904.0 | unverified |
| line-9-0689-0569-s097350 | line-9 | 23 | 2,553.0 | 2,783.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
