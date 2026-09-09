# yangon depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The configured policy is distributed overnight stabling at powered stations, with coordinated morning starts. Main-depot bays serve maintenance and defective trains. The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-4-1637-0275-s051687 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0219-1089-s000000 | line-1 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-1-1884-1217-s041016 | line-1 | 37 | 4,107.0 | 4,477.0 | unverified |
| line-2-1787-1022-s000000 | line-2 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-2-0269-0946-s036832 | line-2 | 34 | 3,774.0 | 4,114.0 | unverified |
| line-3-1746-1932-s000000 | line-3 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-3-0644-0592-s047018 | line-3 | 43 | 4,773.0 | 5,203.0 | unverified |
| line-4-0196-1837-s000000 | line-4 | 47 | 5,217.0 | 5,687.0 | unverified |
| line-4-1637-0275-s051687 | line-4 | 46 | 5,106.0 | 5,566.0 | unverified |
| line-5-1257-1658-s000000 | line-5 | 42 | 4,662.0 | 5,082.0 | unverified |
| line-5-0006-0671-s041983 | line-5 | 41 | 4,551.0 | 4,961.0 | unverified |
| line-6-1360-0852-s000000 | line-6 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-6-0484-2080-s037277 | line-6 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-7-0668-0170-s000000 | line-7 | 40 | 4,440.0 | 4,840.0 | unverified |
| line-7-0908-1738-s043467 | line-7 | 40 | 4,440.0 | 4,840.0 | unverified |
| line-8-0638-0786-s000000 | line-8 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-8-1666-1568-s036321 | line-8 | 34 | 3,774.0 | 4,114.0 | unverified |
| line-9-0521-0596-s000000 | line-9 | 19 | 2,109.0 | 2,299.0 | unverified |
| line-9-0569-0596-s080282 | line-9 | 18 | 1,998.0 | 2,178.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
