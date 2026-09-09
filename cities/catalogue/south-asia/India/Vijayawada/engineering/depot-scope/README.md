# vijayawada depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to storage on its own line. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-3-0864-0002-s043419 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0346-0116-s000000 | line-1 | 26 | 1,950.0 | 2,210.0 | unverified |
| line-1-0997-1082-s033077 | line-1 | 26 | 1,950.0 | 2,210.0 | unverified |
| line-2-0399-0964-s000000 | line-2 | 23 | 1,725.0 | 1,955.0 | unverified |
| line-2-1244-0409-s028792 | line-2 | 22 | 1,650.0 | 1,870.0 | unverified |
| line-3-0683-1536-s000000 | line-3 | 33 | 2,475.0 | 2,805.0 | unverified |
| line-3-0864-0002-s043419 | line-3 | 32 | 2,400.0 | 2,720.0 | unverified |
| line-4-0864-1021-s000000 | line-4 | 21 | 1,575.0 | 1,785.0 | unverified |
| line-4-0120-0429-s025005 | line-4 | 20 | 1,500.0 | 1,700.0 | unverified |
| line-5-0689-0979-s000000 | line-5 | 17 | 1,275.0 | 1,445.0 | unverified |
| line-5-1500-0637-s023296 | line-5 | 17 | 1,275.0 | 1,445.0 | unverified |
| line-6-0606-0448-s000148 | line-6 | 15 | 1,125.0 | 1,275.0 | unverified |
| line-6-0829-0502-s069371 | line-6 | 14 | 1,050.0 | 1,190.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
