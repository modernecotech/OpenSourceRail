# kano depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-1475-0106-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-1897-2046-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-1800-0132-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-1969-1809-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0655-2069-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-0754-0896-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-2184-0687-s050093 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-1575-1359-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-9-0869-0549-s000068 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1475-0106-s000000 | line-1 | 38 | 4,218.0 | 4,598.0 | unverified |
| line-1-1113-1777-s039600 | line-1 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-2-1897-2046-s000000 | line-2 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-2-0827-0458-s043310 | line-2 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-3-1800-0132-s000000 | line-3 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-3-0704-1563-s040896 | line-3 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-4-1969-1809-s000000 | line-4 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-4-1013-0579-s035435 | line-4 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-5-0655-2069-s000000 | line-5 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-5-1615-0774-s036720 | line-5 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-6-0754-0896-s000000 | line-6 | 33 | 3,663.0 | 3,993.0 | unverified |
| line-6-2104-1255-s030265 | line-6 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-7-0229-1566-s000000 | line-7 | 50 | 5,550.0 | 6,050.0 | unverified |
| line-7-2184-0687-s050093 | line-7 | 50 | 5,550.0 | 6,050.0 | unverified |
| line-8-1575-1359-s000000 | line-8 | 45 | 4,995.0 | 5,445.0 | unverified |
| line-8-0031-0097-s044654 | line-8 | 44 | 4,884.0 | 5,324.0 | unverified |
| line-9-0869-0549-s000068 | line-9 | 21 | 2,331.0 | 2,541.0 | unverified |
| line-9-1013-0579-s080027 | line-9 | 20 | 2,220.0 | 2,420.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
