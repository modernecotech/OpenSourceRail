# karachi depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The configured policy is distributed overnight stabling at powered stations, with coordinated morning starts. Main-depot bays serve maintenance and defective trains. The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-3-1591-2081-s054441 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1337-2263-s000000 | line-1 | 45 | 4,995.0 | 5,445.0 | unverified |
| line-1-0997-0434-s048353 | line-1 | 44 | 4,884.0 | 5,324.0 | unverified |
| line-2-0157-1187-s000000 | line-2 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-2-1631-0827-s040914 | line-2 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-3-1206-0042-s000000 | line-3 | 52 | 5,772.0 | 6,292.0 | unverified |
| line-3-1591-2081-s054441 | line-3 | 51 | 5,661.0 | 6,171.0 | unverified |
| line-4-1122-1840-s000000 | line-4 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-4-0856-0602-s037840 | line-4 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-5-0192-1594-s000000 | line-5 | 44 | 4,884.0 | 5,324.0 | unverified |
| line-5-1763-1015-s047145 | line-5 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-6-0077-0802-s000000 | line-6 | 40 | 4,440.0 | 4,840.0 | unverified |
| line-6-1700-1470-s042480 | line-6 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-7-0377-0188-s000000 | line-7 | 44 | 4,884.0 | 5,324.0 | unverified |
| line-7-1833-1216-s045463 | line-7 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-8-0627-1834-s000000 | line-8 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-8-1533-0561-s038251 | line-8 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-9-0807-0665-s000000 | line-9 | 24 | 2,664.0 | 2,904.0 | unverified |
| line-9-0856-0602-s102472 | line-9 | 23 | 2,553.0 | 2,783.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
