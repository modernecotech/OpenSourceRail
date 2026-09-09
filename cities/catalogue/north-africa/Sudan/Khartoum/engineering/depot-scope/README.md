# khartoum depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to declared depots. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-3-2035-2007-s055965 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1674-1346-s000000 | line-1 | 38 | 4,218.0 | 4,598.0 | unverified |
| line-1-0467-0536-s040752 | line-1 | 38 | 4,218.0 | 4,598.0 | unverified |
| line-2-0958-1784-s000000 | line-2 | 34 | 3,774.0 | 4,114.0 | unverified |
| line-2-1142-0484-s035581 | line-2 | 34 | 3,774.0 | 4,114.0 | unverified |
| line-3-0297-0674-s000000 | line-3 | 51 | 5,661.0 | 6,171.0 | unverified |
| line-3-2035-2007-s055965 | line-3 | 51 | 5,661.0 | 6,171.0 | unverified |
| line-4-0750-0571-s000000 | line-4 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-4-1659-1236-s031721 | line-4 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-5-0483-1235-s000000 | line-5 | 40 | 4,440.0 | 4,840.0 | unverified |
| line-5-1875-0674-s041653 | line-5 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-6-1986-1016-s000000 | line-6 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-6-0774-1436-s034186 | line-6 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-7-0781-0129-s000000 | line-7 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-7-1357-1624-s040708 | line-7 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-8-1313-0517-s000000 | line-8 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-8-0070-0949-s036614 | line-8 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-9-0684-0783-s002890 | line-9 | 23 | 2,553.0 | 2,783.0 | unverified |
| line-9-0740-0682-s099175 | line-9 | 22 | 2,442.0 | 2,662.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
