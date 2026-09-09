# ouagadougou depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to declared depots. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0014-1411-s038354 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1191-0456-s000000 | line-1 | 30 | 2,250.0 | 2,550.0 | unverified |
| line-1-0014-1411-s038354 | line-1 | 29 | 2,175.0 | 2,465.0 | unverified |
| line-2-0874-1303-s000000 | line-2 | 21 | 1,575.0 | 1,785.0 | unverified |
| line-2-0813-0361-s024219 | line-2 | 20 | 1,500.0 | 1,700.0 | unverified |
| line-3-1515-0554-s000000 | line-3 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-3-0574-1154-s028452 | line-3 | 23 | 1,725.0 | 1,955.0 | unverified |
| line-4-0254-0378-s000000 | line-4 | 26 | 1,950.0 | 2,210.0 | unverified |
| line-4-1268-1008-s032682 | line-4 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-5-1333-0849-s000000 | line-5 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-5-0114-0722-s032412 | line-5 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-6-0692-0311-s000000 | line-6 | 13 | 975.0 | 1,105.0 | unverified |
| line-6-0813-0361-s062585 | line-6 | 12 | 900.0 | 1,020.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
