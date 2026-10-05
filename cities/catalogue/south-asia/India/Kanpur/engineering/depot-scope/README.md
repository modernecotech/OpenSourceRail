# kanpur depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-1612-1572-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0605-0659-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-1096-0171-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-1660-0624-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-1305-1570-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-2392-1277-s044752 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-1979-0688-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-0850-0705-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1612-1572-s000000 | line-1 | 25 | 2,775.0 | 3,025.0 | unverified |
| line-1-0931-0732-s025916 | line-1 | 24 | 2,664.0 | 2,904.0 | unverified |
| line-2-0605-0659-s000000 | line-2 | 23 | 2,553.0 | 2,783.0 | unverified |
| line-2-1371-1490-s025356 | line-2 | 23 | 2,553.0 | 2,783.0 | unverified |
| line-3-1096-0171-s000000 | line-3 | 40 | 4,440.0 | 4,840.0 | unverified |
| line-3-1233-2232-s042980 | line-3 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-4-1660-0624-s000000 | line-4 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-4-0626-1950-s037975 | line-4 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-5-1305-1570-s000000 | line-5 | 25 | 2,775.0 | 3,025.0 | unverified |
| line-5-1505-0357-s025766 | line-5 | 25 | 2,775.0 | 3,025.0 | unverified |
| line-6-0347-0907-s000000 | line-6 | 42 | 4,662.0 | 5,082.0 | unverified |
| line-6-2392-1277-s044752 | line-6 | 42 | 4,662.0 | 5,082.0 | unverified |
| line-7-1979-0688-s000000 | line-7 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-7-1350-1319-s020434 | line-7 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-8-0850-0705-s000000 | line-8 | 19 | 2,109.0 | 2,299.0 | unverified |
| line-8-0976-0651-s080118 | line-8 | 19 | 2,109.0 | 2,299.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
