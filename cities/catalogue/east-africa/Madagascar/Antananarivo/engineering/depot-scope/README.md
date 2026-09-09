# antananarivo depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The configured policy is distributed overnight stabling at powered stations, with coordinated morning starts. Main-depot bays serve maintenance and defective trains. The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-6-0642-0265-s035454 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1358-0772-s000000 | line-1 | 33 | 3,663.0 | 3,993.0 | unverified |
| line-1-0173-1201-s035411 | line-1 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-2-1142-1146-s000000 | line-2 | 28 | 3,108.0 | 3,388.0 | unverified |
| line-2-0277-0467-s029354 | line-2 | 28 | 3,108.0 | 3,388.0 | unverified |
| line-3-1135-0045-s000000 | line-3 | 34 | 3,774.0 | 4,114.0 | unverified |
| line-3-0746-1266-s034181 | line-3 | 34 | 3,774.0 | 4,114.0 | unverified |
| line-4-0816-1332-s000000 | line-4 | 24 | 2,664.0 | 2,904.0 | unverified |
| line-4-1215-0384-s025701 | line-4 | 24 | 2,664.0 | 2,904.0 | unverified |
| line-5-0597-0856-s000000 | line-5 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-5-1796-1080-s029230 | line-5 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-6-1067-1638-s000000 | line-6 | 33 | 3,663.0 | 3,993.0 | unverified |
| line-6-0642-0265-s035454 | line-6 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-7-0871-0514-s000000 | line-7 | 31 | 3,441.0 | 3,751.0 | unverified |
| line-7-0335-1662-s032343 | line-7 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-8-1281-1151-s000000 | line-8 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-8-0429-0242-s029503 | line-8 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-9-0653-0546-s000000 | line-9 | 18 | 1,998.0 | 2,178.0 | unverified |
| line-9-0707-0496-s071838 | line-9 | 18 | 1,998.0 | 2,178.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
