# yaounde depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0366-1351-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0094-0108-s042110 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-1086-1755-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-1044-1308-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0333-0692-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0366-1351-s000000 | line-1 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-1-1659-0305-s037701 | line-1 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-2-1387-1479-s000000 | line-2 | 41 | 4,551.0 | 4,961.0 | unverified |
| line-2-0094-0108-s042110 | line-2 | 40 | 4,440.0 | 4,840.0 | unverified |
| line-3-1086-1755-s000000 | line-3 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-3-0764-0531-s029924 | line-3 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-4-1044-1308-s000000 | line-4 | 17 | 1,887.0 | 2,057.0 | unverified |
| line-4-0932-0533-s017010 | line-4 | 17 | 1,887.0 | 2,057.0 | unverified |
| line-5-0333-0692-s000000 | line-5 | 15 | 1,665.0 | 1,815.0 | unverified |
| line-5-0443-0706-s060312 | line-5 | 15 | 1,665.0 | 1,815.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
