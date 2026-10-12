# surabaya depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-1151-1011-s043751 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0151-1409-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-0460-0990-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0473-0667-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0914-1114-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-1013-0284-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-0517-0126-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-0723-0958-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-9-0581-0460-s003607 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0001-0684-s000000 | line-1 | 53 | 5,883.0 | 6,413.0 | unverified |
| line-1-1151-1011-s043751 | line-1 | 53 | 5,883.0 | 6,413.0 | unverified |
| line-2-0151-1409-s000000 | line-2 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-2-1193-0642-s041273 | line-2 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-3-0460-0990-s000000 | line-3 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-3-1433-0106-s040794 | line-3 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-4-0473-0667-s000000 | line-4 | 45 | 4,995.0 | 5,445.0 | unverified |
| line-4-1428-0708-s033828 | line-4 | 45 | 4,995.0 | 5,445.0 | unverified |
| line-5-0914-1114-s000000 | line-5 | 52 | 5,772.0 | 6,292.0 | unverified |
| line-5-0210-0013-s036296 | line-5 | 52 | 5,772.0 | 6,292.0 | unverified |
| line-6-1013-0284-s000000 | line-6 | 21 | 2,331.0 | 2,541.0 | unverified |
| line-6-0782-1168-s019805 | line-6 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-7-0517-0126-s000000 | line-7 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-7-0673-1022-s019732 | line-7 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-8-0723-0958-s000000 | line-8 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-8-0866-0175-s018067 | line-8 | 19 | 2,109.0 | 2,299.0 | unverified |
| line-9-0581-0460-s003607 | line-9 | 17 | 1,887.0 | 2,057.0 | unverified |
| line-9-0844-0398-s055434 | line-9 | 17 | 1,887.0 | 2,057.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
