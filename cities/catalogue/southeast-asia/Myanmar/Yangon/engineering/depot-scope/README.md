# yangon depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0219-1089-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-1787-1022-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-0644-0592-s059439 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0196-1837-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-1256-1641-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-1360-0852-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-0668-0170-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-0638-0786-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-9-0521-0596-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0219-1089-s000000 | line-1 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-1-1884-1217-s035760 | line-1 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-2-1787-1022-s000000 | line-2 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-2-0269-0946-s031788 | line-2 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-3-1746-1932-s000000 | line-3 | 66 | 7,326.0 | 7,986.0 | unverified |
| line-3-0644-0592-s059439 | line-3 | 65 | 7,215.0 | 7,865.0 | unverified |
| line-4-0196-1837-s000000 | line-4 | 51 | 5,661.0 | 6,171.0 | unverified |
| line-4-1637-0275-s053999 | line-4 | 51 | 5,661.0 | 6,171.0 | unverified |
| line-5-1256-1641-s000000 | line-5 | 54 | 5,994.0 | 6,534.0 | unverified |
| line-5-0006-0671-s048452 | line-5 | 54 | 5,994.0 | 6,534.0 | unverified |
| line-6-1360-0852-s000000 | line-6 | 33 | 3,663.0 | 3,993.0 | unverified |
| line-6-0484-2080-s035136 | line-6 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-7-0668-0170-s000000 | line-7 | 42 | 4,662.0 | 5,082.0 | unverified |
| line-7-0908-1738-s036122 | line-7 | 41 | 4,551.0 | 4,961.0 | unverified |
| line-8-0638-0786-s000000 | line-8 | 64 | 7,104.0 | 7,744.0 | unverified |
| line-8-1666-1568-s051626 | line-8 | 63 | 6,993.0 | 7,623.0 | unverified |
| line-9-0521-0596-s000000 | line-9 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-9-0644-0784-s089452 | line-9 | 26 | 2,886.0 | 3,146.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
