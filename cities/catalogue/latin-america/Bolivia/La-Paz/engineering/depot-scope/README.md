# la-paz depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The configured policy is distributed overnight stabling at powered stations, with coordinated morning starts. Main-depot bays serve maintenance and defective trains. The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-2-0767-1497-s037195 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0094-1470-s000000 | line-1 | 28 | 2,100.0 | 2,380.0 | unverified |
| line-1-0914-0402-s033718 | line-1 | 28 | 2,100.0 | 2,380.0 | unverified |
| line-2-0618-0177-s000000 | line-2 | 29 | 2,175.0 | 2,465.0 | unverified |
| line-2-0767-1497-s037195 | line-2 | 29 | 2,175.0 | 2,465.0 | unverified |
| line-3-0542-1152-s000000 | line-3 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-3-1334-0251-s030042 | line-3 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-4-1271-1449-s000000 | line-4 | 27 | 2,025.0 | 2,295.0 | unverified |
| line-4-0370-0471-s033347 | line-4 | 27 | 2,025.0 | 2,295.0 | unverified |
| line-5-1251-0639-s000000 | line-5 | 22 | 1,650.0 | 1,870.0 | unverified |
| line-5-0222-0838-s027582 | line-5 | 21 | 1,575.0 | 1,785.0 | unverified |
| line-6-0677-0388-s000887 | line-6 | 13 | 975.0 | 1,105.0 | unverified |
| line-6-0833-0419-s057830 | line-6 | 12 | 900.0 | 1,020.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
