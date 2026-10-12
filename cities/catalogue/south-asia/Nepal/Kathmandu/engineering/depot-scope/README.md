# kathmandu depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0141-0110-s038145 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-1081-0122-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-0313-0742-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0194-0595-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0700-1326-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-0516-0468-s003006 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-0514-1014-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-0997-1195-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-9-0740-0369-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0997-1195-s000000 | line-1 | 53 | 3,975.0 | 4,505.0 | unverified |
| line-1-0141-0110-s038145 | line-1 | 53 | 3,975.0 | 4,505.0 | unverified |
| line-2-1081-0122-s000000 | line-2 | 30 | 2,250.0 | 2,550.0 | unverified |
| line-2-0445-0975-s029416 | line-2 | 30 | 2,250.0 | 2,550.0 | unverified |
| line-3-0313-0742-s000000 | line-3 | 35 | 2,625.0 | 2,975.0 | unverified |
| line-3-0941-0749-s022048 | line-3 | 35 | 2,625.0 | 2,975.0 | unverified |
| line-4-0194-0595-s000000 | line-4 | 29 | 2,175.0 | 2,465.0 | unverified |
| line-4-1094-0420-s025121 | line-4 | 28 | 2,100.0 | 2,380.0 | unverified |
| line-5-0700-1326-s000000 | line-5 | 34 | 2,550.0 | 2,890.0 | unverified |
| line-5-0669-0143-s031461 | line-5 | 34 | 2,550.0 | 2,890.0 | unverified |
| line-6-0516-0468-s003006 | line-6 | 13 | 975.0 | 1,105.0 | unverified |
| line-6-0691-0354-s053591 | line-6 | 13 | 975.0 | 1,105.0 | unverified |
| line-7-0514-1014-s000000 | line-7 | 6 | 450.0 | 510.0 | unverified |
| line-7-0411-1138-s006312 | line-7 | 5 | 375.0 | 425.0 | unverified |
| line-8-0997-1195-s000000 | line-8 | 20 | 1,500.0 | 1,700.0 | unverified |
| line-8-0562-0963-s024113 | line-8 | 19 | 1,425.0 | 1,615.0 | unverified |
| line-9-0740-0369-s000000 | line-9 | 5 | 375.0 | 425.0 | unverified |
| line-9-0834-0219-s004861 | line-9 | 5 | 375.0 | 425.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
