# bhopal depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to declared depots. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-4-0162-1430-s035847 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0856-1377-s000000 | line-1 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-1-0750-0391-s025944 | line-1 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-2-1294-0881-s000000 | line-2 | 23 | 1,725.0 | 1,955.0 | unverified |
| line-2-0447-0763-s025335 | line-2 | 22 | 1,650.0 | 1,870.0 | unverified |
| line-3-1348-1098-s000000 | line-3 | 18 | 1,350.0 | 1,530.0 | unverified |
| line-3-0554-0923-s022018 | line-3 | 17 | 1,275.0 | 1,445.0 | unverified |
| line-4-1207-0554-s000000 | line-4 | 27 | 2,025.0 | 2,295.0 | unverified |
| line-4-0162-1430-s035847 | line-4 | 27 | 2,025.0 | 2,295.0 | unverified |
| line-5-0565-0670-s000000 | line-5 | 20 | 1,500.0 | 1,700.0 | unverified |
| line-5-1223-1370-s026131 | line-5 | 19 | 1,425.0 | 1,615.0 | unverified |
| line-6-0602-0460-s000000 | line-6 | 12 | 900.0 | 1,020.0 | unverified |
| line-6-0724-0540-s055692 | line-6 | 11 | 825.0 | 935.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
