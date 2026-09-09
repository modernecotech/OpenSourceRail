# chittagong depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to declared depots. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-3-2205-1847-s047618 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1737-1246-s000000 | line-1 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-1-0045-0697-s041910 | line-1 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-2-1714-1318-s000000 | line-2 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-2-0679-1422-s028984 | line-2 | 28 | 3,108.0 | 3,388.0 | unverified |
| line-3-0371-1207-s000000 | line-3 | 45 | 4,995.0 | 5,445.0 | unverified |
| line-3-2205-1847-s047618 | line-3 | 44 | 4,884.0 | 5,324.0 | unverified |
| line-4-0617-2159-s000000 | line-4 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-4-1410-1170-s033320 | line-4 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-5-1359-1166-s000000 | line-5 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-5-0210-1918-s035819 | line-5 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-6-1096-1139-s000000 | line-6 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-6-1529-2226-s029926 | line-6 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-7-1201-1087-s000000 | line-7 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-7-2014-2377-s037034 | line-7 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-8-0586-1192-s000000 | line-8 | 16 | 1,776.0 | 1,936.0 | unverified |
| line-8-0763-1188-s065556 | line-8 | 16 | 1,776.0 | 1,936.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
