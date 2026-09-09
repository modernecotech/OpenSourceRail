# lusaka depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to storage on its own line. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-1009-0554-s038518 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0450-1876-s000000 | line-1 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-1-1009-0554-s038518 | line-1 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-2-0718-1568-s000000 | line-2 | 24 | 2,664.0 | 2,904.0 | unverified |
| line-2-1212-0768-s026247 | line-2 | 23 | 2,553.0 | 2,783.0 | unverified |
| line-3-1233-1602-s000000 | line-3 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-3-0735-0576-s027489 | line-3 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-4-0960-1449-s000000 | line-4 | 23 | 2,553.0 | 2,783.0 | unverified |
| line-4-0631-0716-s023846 | line-4 | 22 | 2,442.0 | 2,662.0 | unverified |
| line-5-0566-1117-s000000 | line-5 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-5-1503-1013-s028409 | line-5 | 25 | 2,775.0 | 3,025.0 | unverified |
| line-6-0298-1692-s000000 | line-6 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-6-0858-0582-s032437 | line-6 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-7-0415-0933-s000000 | line-7 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-7-1368-0383-s028663 | line-7 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-8-0244-0910-s000000 | line-8 | 18 | 1,998.0 | 2,178.0 | unverified |
| line-8-0415-0933-s070082 | line-8 | 17 | 1,887.0 | 2,057.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
