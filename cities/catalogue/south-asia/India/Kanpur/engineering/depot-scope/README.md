# kanpur depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-1624-1597-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0605-0659-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-1233-2232-s064551 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-1660-0624-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-1294-1580-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-0347-0907-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-1979-0688-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-0850-0705-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1624-1597-s000000 | line-1 | 25 | 2,775.0 | 3,025.0 | unverified |
| line-1-0931-0732-s025022 | line-1 | 25 | 2,775.0 | 3,025.0 | unverified |
| line-2-0605-0659-s000000 | line-2 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-2-1371-1490-s025356 | line-2 | 25 | 2,775.0 | 3,025.0 | unverified |
| line-3-1096-0171-s000000 | line-3 | 66 | 7,326.0 | 7,986.0 | unverified |
| line-3-1233-2232-s064551 | line-3 | 65 | 7,215.0 | 7,865.0 | unverified |
| line-4-1660-0624-s000000 | line-4 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-4-0626-1950-s037975 | line-4 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-5-1294-1580-s000000 | line-5 | 25 | 2,775.0 | 3,025.0 | unverified |
| line-5-1505-0357-s026125 | line-5 | 25 | 2,775.0 | 3,025.0 | unverified |
| line-6-0347-0907-s000000 | line-6 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-6-2392-1277-s044752 | line-6 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-7-1979-0688-s000000 | line-7 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-7-1350-1319-s020434 | line-7 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-8-0850-0705-s000000 | line-8 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-8-0930-0642-s110671 | line-8 | 26 | 2,886.0 | 3,146.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
