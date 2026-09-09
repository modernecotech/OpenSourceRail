# indore depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to storage on its own line. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-4-1013-0866-s042681 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0893-1636-s000000 | line-1 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-1-2039-0628-s038096 | line-1 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-2-2189-1478-s000000 | line-2 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-2-0670-1182-s038155 | line-2 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-3-0769-1038-s000000 | line-3 | 41 | 4,551.0 | 4,961.0 | unverified |
| line-3-2343-0891-s041693 | line-3 | 40 | 4,440.0 | 4,840.0 | unverified |
| line-4-1748-2185-s000000 | line-4 | 41 | 4,551.0 | 4,961.0 | unverified |
| line-4-1013-0866-s042681 | line-4 | 41 | 4,551.0 | 4,961.0 | unverified |
| line-5-1522-1369-s000000 | line-5 | 40 | 4,440.0 | 4,840.0 | unverified |
| line-5-0007-1901-s041700 | line-5 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-6-0911-1004-s000000 | line-6 | 34 | 3,774.0 | 4,114.0 | unverified |
| line-6-1403-2195-s034587 | line-6 | 33 | 3,663.0 | 3,993.0 | unverified |
| line-7-1843-0329-s000000 | line-7 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-7-1053-1645-s039172 | line-7 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-8-0585-0904-s000000 | line-8 | 21 | 2,331.0 | 2,541.0 | unverified |
| line-8-0813-0850-s087630 | line-8 | 21 | 2,331.0 | 2,541.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
