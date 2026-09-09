# beirut depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to declared depots. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0098-1068-s031936 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1174-0479-s000000 | line-1 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-1-0098-1068-s031936 | line-1 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-2-0556-0385-s000000 | line-2 | 18 | 1,350.0 | 1,530.0 | unverified |
| line-2-1095-0659-s018089 | line-2 | 17 | 1,275.0 | 1,445.0 | unverified |
| line-3-0672-0377-s000000 | line-3 | 17 | 1,275.0 | 1,445.0 | unverified |
| line-3-0439-1119-s020281 | line-3 | 17 | 1,275.0 | 1,445.0 | unverified |
| line-4-0650-1073-s000000 | line-4 | 14 | 1,050.0 | 1,190.0 | unverified |
| line-4-0836-0386-s017376 | line-4 | 13 | 975.0 | 1,105.0 | unverified |
| line-5-0604-0501-s000000 | line-5 | 15 | 1,125.0 | 1,275.0 | unverified |
| line-5-1118-0916-s018494 | line-5 | 14 | 1,050.0 | 1,190.0 | unverified |
| line-6-0530-0912-s000000 | line-6 | 7 | 525.0 | 595.0 | unverified |
| line-6-0657-0785-s031543 | line-6 | 7 | 525.0 | 595.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
