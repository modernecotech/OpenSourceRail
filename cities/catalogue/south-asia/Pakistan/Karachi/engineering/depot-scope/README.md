# karachi depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-1337-2263-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0157-1187-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-1591-2081-s044295 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-1122-1840-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0192-1594-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-0077-0802-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-0377-0188-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-0627-1834-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-9-0698-0771-s003468 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1337-2263-s000000 | line-1 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-1-0997-0434-s042076 | line-1 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-2-0157-1187-s000000 | line-2 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-2-1605-0812-s034016 | line-2 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-3-1206-0042-s000000 | line-3 | 42 | 4,662.0 | 5,082.0 | unverified |
| line-3-1591-2081-s044295 | line-3 | 41 | 4,551.0 | 4,961.0 | unverified |
| line-4-1122-1840-s000000 | line-4 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-4-0831-0619-s028338 | line-4 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-5-0192-1594-s000000 | line-5 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-5-1752-0986-s038548 | line-5 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-6-0077-0802-s000000 | line-6 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-6-1670-1473-s039202 | line-6 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-7-0377-0188-s000000 | line-7 | 38 | 4,218.0 | 4,598.0 | unverified |
| line-7-1860-1230-s040538 | line-7 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-8-0627-1834-s000000 | line-8 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-8-1533-0561-s035026 | line-8 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-9-0698-0771-s003468 | line-9 | 22 | 2,442.0 | 2,662.0 | unverified |
| line-9-0831-0619-s093396 | line-9 | 21 | 2,331.0 | 2,541.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
