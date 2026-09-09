# phnom-penh depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to storage on its own line. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-3-0167-1516-s041534 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1241-0877-s000000 | line-1 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-1-0094-0525-s030282 | line-1 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-2-0659-0399-s000000 | line-2 | 23 | 1,725.0 | 1,955.0 | unverified |
| line-2-1053-1483-s029077 | line-2 | 23 | 1,725.0 | 1,955.0 | unverified |
| line-3-1094-0188-s000000 | line-3 | 33 | 2,475.0 | 2,805.0 | unverified |
| line-3-0167-1516-s041534 | line-3 | 32 | 2,400.0 | 2,720.0 | unverified |
| line-4-0074-0956-s000000 | line-4 | 27 | 2,025.0 | 2,295.0 | unverified |
| line-4-1302-0599-s033216 | line-4 | 26 | 1,950.0 | 2,210.0 | unverified |
| line-5-0224-0025-s000000 | line-5 | 26 | 1,950.0 | 2,210.0 | unverified |
| line-5-0962-1021-s033516 | line-5 | 26 | 1,950.0 | 2,210.0 | unverified |
| line-6-0551-0444-s000000 | line-6 | 14 | 1,050.0 | 1,190.0 | unverified |
| line-6-0659-0399-s067689 | line-6 | 14 | 1,050.0 | 1,190.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
