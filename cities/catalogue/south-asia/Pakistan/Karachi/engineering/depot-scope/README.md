# karachi depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-1337-2263-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0157-1187-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-1206-0042-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-1122-1840-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0192-1594-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-0077-0802-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-0377-0188-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-1533-0561-s047253 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-9-0807-0665-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1337-2263-s000000 | line-1 | 40 | 4,440.0 | 4,840.0 | unverified |
| line-1-0997-0434-s042076 | line-1 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-2-0157-1187-s000000 | line-2 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-2-1612-0833-s033801 | line-2 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-3-1206-0042-s000000 | line-3 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-3-1591-2081-s044295 | line-3 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-4-1122-1840-s000000 | line-4 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-4-0856-0607-s027543 | line-4 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-5-0192-1594-s000000 | line-5 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-5-1763-1006-s038029 | line-5 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-6-0077-0802-s000000 | line-6 | 38 | 4,218.0 | 4,598.0 | unverified |
| line-6-1699-1464-s038644 | line-6 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-7-0377-0188-s000000 | line-7 | 41 | 4,551.0 | 4,961.0 | unverified |
| line-7-1862-1213-s040558 | line-7 | 41 | 4,551.0 | 4,961.0 | unverified |
| line-8-0627-1834-s000000 | line-8 | 51 | 5,661.0 | 6,171.0 | unverified |
| line-8-1533-0561-s047253 | line-8 | 51 | 5,661.0 | 6,171.0 | unverified |
| line-9-0807-0665-s000000 | line-9 | 33 | 3,663.0 | 3,993.0 | unverified |
| line-9-0857-0607-s141260 | line-9 | 32 | 3,552.0 | 3,872.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
