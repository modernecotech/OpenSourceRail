# kanpur depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to declared depots. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-3-1233-2232-s051836 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1616-1602-s000000 | line-1 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-1-0931-0732-s027325 | line-1 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-2-0605-0659-s000000 | line-2 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-2-1371-1490-s029123 | line-2 | 28 | 3,108.0 | 3,388.0 | unverified |
| line-3-1096-0171-s000000 | line-3 | 49 | 5,439.0 | 5,929.0 | unverified |
| line-3-1233-2232-s051836 | line-3 | 49 | 5,439.0 | 5,929.0 | unverified |
| line-4-1660-0624-s000000 | line-4 | 42 | 4,662.0 | 5,082.0 | unverified |
| line-4-0626-1950-s043076 | line-4 | 41 | 4,551.0 | 4,961.0 | unverified |
| line-5-1305-1570-s000000 | line-5 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-5-1505-0357-s032355 | line-5 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-6-0347-0907-s000000 | line-6 | 48 | 5,328.0 | 5,808.0 | unverified |
| line-6-2392-1277-s051378 | line-6 | 47 | 5,217.0 | 5,687.0 | unverified |
| line-7-1979-0688-s000000 | line-7 | 23 | 2,553.0 | 2,783.0 | unverified |
| line-7-1350-1319-s023255 | line-7 | 23 | 2,553.0 | 2,783.0 | unverified |
| line-8-0715-0835-s004217 | line-8 | 22 | 2,442.0 | 2,662.0 | unverified |
| line-8-0848-0707-s094104 | line-8 | 21 | 2,331.0 | 2,541.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
