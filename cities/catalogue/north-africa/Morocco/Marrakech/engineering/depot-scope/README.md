# marrakech depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0666-0472-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0176-1241-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-0821-0410-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-1429-0421-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0102-0195-s030578 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-0742-0504-s002368 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0666-0472-s000000 | line-1 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-1-1414-1431-s027751 | line-1 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-2-0176-1241-s000000 | line-2 | 22 | 1,650.0 | 1,870.0 | unverified |
| line-2-0992-0531-s025056 | line-2 | 21 | 1,575.0 | 1,785.0 | unverified |
| line-3-0821-0410-s000000 | line-3 | 20 | 1,500.0 | 1,700.0 | unverified |
| line-3-0712-1395-s021135 | line-3 | 20 | 1,500.0 | 1,700.0 | unverified |
| line-4-1429-0421-s000000 | line-4 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-4-0365-0834-s025369 | line-4 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-5-1330-0747-s000000 | line-5 | 27 | 2,025.0 | 2,295.0 | unverified |
| line-5-0102-0195-s030578 | line-5 | 26 | 1,950.0 | 2,210.0 | unverified |
| line-6-0742-0504-s002368 | line-6 | 12 | 900.0 | 1,020.0 | unverified |
| line-6-0821-0410-s051710 | line-6 | 11 | 825.0 | 935.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
