# coimbatore depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The configured policy is distributed overnight stabling at powered stations, with coordinated morning starts. Main-depot bays serve maintenance and defective trains. The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0132-1530-s048163 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1466-0328-s000000 | line-1 | 48 | 5,328.0 | 5,808.0 | unverified |
| line-1-0132-1530-s048163 | line-1 | 47 | 5,217.0 | 5,687.0 | unverified |
| line-2-0799-1316-s000000 | line-2 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-2-0671-0283-s028411 | line-2 | 25 | 2,775.0 | 3,025.0 | unverified |
| line-3-0126-1033-s000000 | line-3 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-3-1078-0454-s032783 | line-3 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-4-1200-0710-s000000 | line-4 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-4-0271-1579-s032211 | line-4 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-5-0569-0370-s000000 | line-5 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-5-0679-1528-s031071 | line-5 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-6-1647-1010-s000000 | line-6 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-6-0373-0506-s037771 | line-6 | 36 | 3,996.0 | 4,356.0 | unverified |
| line-7-0784-0090-s000000 | line-7 | 22 | 2,442.0 | 2,662.0 | unverified |
| line-7-0944-0978-s023409 | line-7 | 21 | 2,331.0 | 2,541.0 | unverified |
| line-8-1359-0832-s000000 | line-8 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-8-0173-0646-s032053 | line-8 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-9-0712-0356-s000000 | line-9 | 18 | 1,998.0 | 2,178.0 | unverified |
| line-9-0807-0385-s073947 | line-9 | 18 | 1,998.0 | 2,178.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
