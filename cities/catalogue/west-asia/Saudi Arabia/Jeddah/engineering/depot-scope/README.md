# jeddah depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to declared depots. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0002-0746-s050233 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1924-1474-s000000 | line-1 | 47 | 5,217.0 | 5,687.0 | unverified |
| line-1-0002-0746-s050233 | line-1 | 46 | 5,106.0 | 5,566.0 | unverified |
| line-2-1645-1227-s000000 | line-2 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-2-0561-0795-s028687 | line-2 | 25 | 2,775.0 | 3,025.0 | unverified |
| line-3-0230-1106-s000000 | line-3 | 41 | 4,551.0 | 4,961.0 | unverified |
| line-3-1828-1770-s044377 | line-3 | 40 | 4,440.0 | 4,840.0 | unverified |
| line-4-0564-1342-s000000 | line-4 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-4-2245-0879-s043650 | line-4 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-5-1385-2285-s000000 | line-5 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-5-1003-0892-s037107 | line-5 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-6-1747-2233-s000000 | line-6 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-6-1120-1060-s032445 | line-6 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-7-0301-1712-s000000 | line-7 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-7-1275-1339-s028985 | line-7 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-8-0522-1812-s000000 | line-8 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-8-1287-1042-s027430 | line-8 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-9-0608-0959-s000000 | line-9 | 19 | 2,109.0 | 2,299.0 | unverified |
| line-9-0664-0950-s081181 | line-9 | 19 | 2,109.0 | 2,299.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
