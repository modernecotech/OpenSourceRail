# surabaya depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to declared depots. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-3-1433-0106-s037394 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0001-0684-s000000 | line-1 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-1-1195-0998-s035123 | line-1 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-2-0151-1409-s000000 | line-2 | 33 | 3,663.0 | 3,993.0 | unverified |
| line-2-1198-0641-s033398 | line-2 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-3-0460-0990-s000000 | line-3 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-3-1433-0106-s037394 | line-3 | 34 | 3,774.0 | 4,114.0 | unverified |
| line-4-0477-0625-s000000 | line-4 | 25 | 2,775.0 | 3,025.0 | unverified |
| line-4-1428-0708-s026292 | line-4 | 24 | 2,664.0 | 2,904.0 | unverified |
| line-5-0914-1114-s000000 | line-5 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-5-0210-0013-s033831 | line-5 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-6-1013-0284-s000000 | line-6 | 24 | 2,664.0 | 2,904.0 | unverified |
| line-6-0782-1168-s024037 | line-6 | 23 | 2,553.0 | 2,783.0 | unverified |
| line-7-0517-0126-s000000 | line-7 | 23 | 2,553.0 | 2,783.0 | unverified |
| line-7-0673-1022-s023089 | line-7 | 22 | 2,442.0 | 2,662.0 | unverified |
| line-8-0723-0958-s000000 | line-8 | 21 | 2,331.0 | 2,541.0 | unverified |
| line-8-0866-0175-s020966 | line-8 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-9-0705-0391-s000000 | line-9 | 15 | 1,665.0 | 1,815.0 | unverified |
| line-9-0771-0377-s057768 | line-9 | 14 | 1,554.0 | 1,694.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
