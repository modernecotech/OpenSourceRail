# jeddah depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0002-0746-s047300 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-1645-1227-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-0230-1106-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0594-1322-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-1385-2285-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-1747-2233-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-0301-1712-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-0522-1812-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-9-0589-1018-s000361 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1924-1474-s000000 | line-1 | 46 | 5,106.0 | 5,566.0 | unverified |
| line-1-0002-0746-s047300 | line-1 | 45 | 4,995.0 | 5,445.0 | unverified |
| line-2-1645-1227-s000000 | line-2 | 28 | 3,108.0 | 3,388.0 | unverified |
| line-2-0561-0795-s030344 | line-2 | 28 | 3,108.0 | 3,388.0 | unverified |
| line-3-0230-1106-s000000 | line-3 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-3-1828-1770-s039191 | line-3 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-4-0594-1322-s000000 | line-4 | 42 | 4,662.0 | 5,082.0 | unverified |
| line-4-2245-0879-s045370 | line-4 | 42 | 4,662.0 | 5,082.0 | unverified |
| line-5-1385-2285-s000000 | line-5 | 34 | 3,774.0 | 4,114.0 | unverified |
| line-5-1003-0892-s033184 | line-5 | 33 | 3,663.0 | 3,993.0 | unverified |
| line-6-1747-2233-s000000 | line-6 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-6-1120-1060-s030162 | line-6 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-7-0301-1712-s000000 | line-7 | 23 | 2,553.0 | 2,783.0 | unverified |
| line-7-1276-1338-s023266 | line-7 | 23 | 2,553.0 | 2,783.0 | unverified |
| line-8-0522-1812-s000000 | line-8 | 24 | 2,664.0 | 2,904.0 | unverified |
| line-8-1273-1056-s023966 | line-8 | 23 | 2,553.0 | 2,783.0 | unverified |
| line-9-0589-1018-s000361 | line-9 | 18 | 1,998.0 | 2,178.0 | unverified |
| line-9-0633-0968-s072984 | line-9 | 18 | 1,998.0 | 2,178.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
