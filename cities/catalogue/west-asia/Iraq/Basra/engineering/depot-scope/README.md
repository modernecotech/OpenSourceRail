# basra depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0080-0724-s048286 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-1620-1366-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-1713-2270-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-1070-0777-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-2152-0348-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-1003-0997-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-0731-0954-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-1737-0647-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-9-1215-1540-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-10-1728-1461-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-11-0084-0721-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1783-1156-s000000 | line-1 | 48 | 5,328.0 | 5,808.0 | unverified |
| line-1-0080-0724-s048286 | line-1 | 47 | 5,217.0 | 5,687.0 | unverified |
| line-2-1620-1366-s000000 | line-2 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-2-0839-1170-s021872 | line-2 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-3-1713-2270-s000000 | line-3 | 40 | 4,440.0 | 4,840.0 | unverified |
| line-3-1128-0589-s041544 | line-3 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-4-1070-0777-s000000 | line-4 | 33 | 3,663.0 | 3,993.0 | unverified |
| line-4-1405-2361-s034971 | line-4 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-5-2152-0348-s000000 | line-5 | 41 | 4,551.0 | 4,961.0 | unverified |
| line-5-1179-1578-s041191 | line-5 | 40 | 4,440.0 | 4,840.0 | unverified |
| line-6-1003-0997-s000000 | line-6 | 24 | 2,664.0 | 2,904.0 | unverified |
| line-6-2118-0683-s026389 | line-6 | 24 | 2,664.0 | 2,904.0 | unverified |
| line-7-0731-0954-s000000 | line-7 | 23 | 2,553.0 | 2,783.0 | unverified |
| line-7-0861-0920-s092212 | line-7 | 22 | 2,442.0 | 2,662.0 | unverified |
| line-8-1737-0647-s000000 | line-8 | 12 | 1,332.0 | 1,452.0 | unverified |
| line-8-1514-0237-s010670 | line-8 | 11 | 1,221.0 | 1,331.0 | unverified |
| line-9-1215-1540-s000000 | line-9 | 13 | 1,443.0 | 1,573.0 | unverified |
| line-9-1238-1162-s011354 | line-9 | 13 | 1,443.0 | 1,573.0 | unverified |
| line-10-1728-1461-s000000 | line-10 | 10 | 1,110.0 | 1,210.0 | unverified |
| line-10-1563-1212-s009935 | line-10 | 9 | 999.0 | 1,089.0 | unverified |
| line-11-0084-0721-s000000 | line-11 | 7 | 777.0 | 847.0 | unverified |
| line-11-0013-0489-s006585 | line-11 | 7 | 777.0 | 847.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
