# sanaa depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to declared depots. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-1395-1093-s041473 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0008-0203-s000000 | line-1 | 38 | 4,218.0 | 4,598.0 | unverified |
| line-1-1395-1093-s041473 | line-1 | 38 | 4,218.0 | 4,598.0 | unverified |
| line-2-0467-0820-s000000 | line-2 | 21 | 2,331.0 | 2,541.0 | unverified |
| line-2-1220-1138-s020950 | line-2 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-3-0547-0553-s000000 | line-3 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-3-1262-1632-s032034 | line-3 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-4-1254-0792-s000000 | line-4 | 24 | 2,664.0 | 2,904.0 | unverified |
| line-4-0298-1042-s024743 | line-4 | 24 | 2,664.0 | 2,904.0 | unverified |
| line-5-0645-1513-s000000 | line-5 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-5-0890-0164-s033849 | line-5 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-6-0722-0039-s000000 | line-6 | 21 | 2,331.0 | 2,541.0 | unverified |
| line-6-0955-0906-s020944 | line-6 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-7-0342-0856-s000000 | line-7 | 14 | 1,554.0 | 1,694.0 | unverified |
| line-7-0375-0782-s057163 | line-7 | 14 | 1,554.0 | 1,694.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
