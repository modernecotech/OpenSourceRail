# mbuji-mayi depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The configured policy is distributed overnight stabling at powered stations, with coordinated morning starts. Main-depot bays serve maintenance and defective trains. The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0654-1547-s029311 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0649-0303-s000000 | line-1 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-1-0654-1547-s029311 | line-1 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-2-0910-0600-s000000 | line-2 | 14 | 1,050.0 | 1,190.0 | unverified |
| line-2-0913-1349-s016841 | line-2 | 13 | 975.0 | 1,105.0 | unverified |
| line-3-0176-1444-s000000 | line-3 | 22 | 1,650.0 | 1,870.0 | unverified |
| line-3-1103-0659-s028865 | line-3 | 21 | 1,575.0 | 1,785.0 | unverified |
| line-4-0501-0538-s004582 | line-4 | 9 | 675.0 | 765.0 | unverified |
| line-4-0661-0415-s043738 | line-4 | 8 | 600.0 | 680.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
