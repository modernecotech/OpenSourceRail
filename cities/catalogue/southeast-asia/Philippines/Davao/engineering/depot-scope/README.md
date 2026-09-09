# davao depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to declared depots. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-1535-0474-s047206 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0053-1476-s000000 | line-1 | 36 | 2,700.0 | 3,060.0 | unverified |
| line-1-1535-0474-s047206 | line-1 | 36 | 2,700.0 | 3,060.0 | unverified |
| line-2-0183-0000-s000000 | line-2 | 31 | 2,325.0 | 2,635.0 | unverified |
| line-2-1301-1106-s040381 | line-2 | 31 | 2,325.0 | 2,635.0 | unverified |
| line-3-0756-1623-s000000 | line-3 | 27 | 2,025.0 | 2,295.0 | unverified |
| line-3-0755-0141-s036373 | line-3 | 27 | 2,025.0 | 2,295.0 | unverified |
| line-4-0985-0195-s000000 | line-4 | 29 | 2,175.0 | 2,465.0 | unverified |
| line-4-1034-1655-s036888 | line-4 | 29 | 2,175.0 | 2,465.0 | unverified |
| line-5-0153-0389-s000000 | line-5 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-5-1121-1229-s032059 | line-5 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-6-0480-0425-s003501 | line-6 | 17 | 1,275.0 | 1,445.0 | unverified |
| line-6-0519-0314-s087114 | line-6 | 17 | 1,275.0 | 1,445.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
