# bamako depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0032-0412-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-1289-0508-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-1312-0792-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-1408-1726-s053707 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0599-1002-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-0346-0737-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-1195-1280-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-1323-1008-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-9-1271-0526-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0032-0412-s000000 | line-1 | 53 | 3,975.0 | 4,505.0 | unverified |
| line-1-1489-1327-s047755 | line-1 | 52 | 3,900.0 | 4,420.0 | unverified |
| line-2-1289-0508-s000000 | line-2 | 30 | 2,250.0 | 2,550.0 | unverified |
| line-2-0547-1266-s029883 | line-2 | 30 | 2,250.0 | 2,550.0 | unverified |
| line-3-1312-0792-s000000 | line-3 | 18 | 1,350.0 | 1,530.0 | unverified |
| line-3-0729-1227-s016316 | line-3 | 17 | 1,275.0 | 1,445.0 | unverified |
| line-4-0959-0592-s000000 | line-4 | 55 | 4,125.0 | 4,675.0 | unverified |
| line-4-1408-1726-s053707 | line-4 | 54 | 4,050.0 | 4,590.0 | unverified |
| line-5-0599-1002-s000000 | line-5 | 21 | 1,575.0 | 1,785.0 | unverified |
| line-5-1531-0939-s019825 | line-5 | 20 | 1,500.0 | 1,700.0 | unverified |
| line-6-0346-0737-s000000 | line-6 | 28 | 2,100.0 | 2,380.0 | unverified |
| line-6-0482-0739-s107906 | line-6 | 28 | 2,100.0 | 2,380.0 | unverified |
| line-7-1195-1280-s000000 | line-7 | 8 | 600.0 | 680.0 | unverified |
| line-7-0948-1421-s008006 | line-7 | 7 | 525.0 | 595.0 | unverified |
| line-8-1323-1008-s000000 | line-8 | 10 | 750.0 | 850.0 | unverified |
| line-8-1562-1362-s010526 | line-8 | 9 | 675.0 | 765.0 | unverified |
| line-9-1271-0526-s000000 | line-9 | 17 | 1,275.0 | 1,445.0 | unverified |
| line-9-1287-1089-s014829 | line-9 | 17 | 1,275.0 | 1,445.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
