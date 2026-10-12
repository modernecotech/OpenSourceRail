# aleppo depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-1156-0150-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-1010-1095-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-0474-0813-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0592-0097-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-1211-0580-s029202 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-0444-0371-s004109 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-0710-1071-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-0361-0899-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-9-0416-0739-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1156-0150-s000000 | line-1 | 56 | 4,200.0 | 4,760.0 | unverified |
| line-1-0529-0949-s028668 | line-1 | 55 | 4,125.0 | 4,675.0 | unverified |
| line-2-1010-1095-s000000 | line-2 | 31 | 2,325.0 | 2,635.0 | unverified |
| line-2-0383-0244-s027941 | line-2 | 30 | 2,250.0 | 2,550.0 | unverified |
| line-3-0474-0813-s000000 | line-3 | 27 | 2,025.0 | 2,295.0 | unverified |
| line-3-0809-0374-s015710 | line-3 | 26 | 1,950.0 | 2,210.0 | unverified |
| line-4-0592-0097-s000000 | line-4 | 46 | 3,450.0 | 3,910.0 | unverified |
| line-4-0701-1017-s027368 | line-4 | 45 | 3,375.0 | 3,825.0 | unverified |
| line-5-0173-0719-s000000 | line-5 | 46 | 3,450.0 | 3,910.0 | unverified |
| line-5-1211-0580-s029202 | line-5 | 45 | 3,375.0 | 3,825.0 | unverified |
| line-6-0444-0371-s004109 | line-6 | 13 | 975.0 | 1,105.0 | unverified |
| line-6-0674-0282-s057793 | line-6 | 12 | 900.0 | 1,020.0 | unverified |
| line-7-0710-1071-s000000 | line-7 | 5 | 375.0 | 425.0 | unverified |
| line-7-0762-1264-s004407 | line-7 | 5 | 375.0 | 425.0 | unverified |
| line-8-0361-0899-s000000 | line-8 | 7 | 525.0 | 595.0 | unverified |
| line-8-0212-1063-s006982 | line-8 | 6 | 450.0 | 510.0 | unverified |
| line-9-0416-0739-s000000 | line-9 | 6 | 450.0 | 510.0 | unverified |
| line-9-0488-0587-s005503 | line-9 | 5 | 375.0 | 425.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
