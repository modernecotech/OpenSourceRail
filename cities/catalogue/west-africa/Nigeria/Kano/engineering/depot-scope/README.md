# kano depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to storage on its own line. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-7-2184-0687-s052622 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1475-0106-s000000 | line-1 | 38 | 4,218.0 | 4,598.0 | unverified |
| line-1-1115-1813-s043385 | line-1 | 38 | 4,218.0 | 4,598.0 | unverified |
| line-2-1897-2046-s000000 | line-2 | 45 | 4,995.0 | 5,445.0 | unverified |
| line-2-0827-0458-s046035 | line-2 | 45 | 4,995.0 | 5,445.0 | unverified |
| line-3-1800-0132-s000000 | line-3 | 42 | 4,662.0 | 5,082.0 | unverified |
| line-3-0704-1563-s045097 | line-3 | 41 | 4,551.0 | 4,961.0 | unverified |
| line-4-1969-1809-s000000 | line-4 | 38 | 4,218.0 | 4,598.0 | unverified |
| line-4-1019-0561-s039300 | line-4 | 38 | 4,218.0 | 4,598.0 | unverified |
| line-5-0655-2069-s000000 | line-5 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-5-1615-0774-s038252 | line-5 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-6-0768-0894-s000000 | line-6 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-6-2104-1255-s033872 | line-6 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-7-0229-1566-s000000 | line-7 | 50 | 5,550.0 | 6,050.0 | unverified |
| line-7-2184-0687-s052622 | line-7 | 50 | 5,550.0 | 6,050.0 | unverified |
| line-8-1575-1359-s000000 | line-8 | 45 | 4,995.0 | 5,445.0 | unverified |
| line-8-0031-0097-s045895 | line-8 | 44 | 4,884.0 | 5,324.0 | unverified |
| line-9-0888-0542-s000000 | line-9 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-9-1019-0561-s086771 | line-9 | 20 | 2,220.0 | 2,420.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
