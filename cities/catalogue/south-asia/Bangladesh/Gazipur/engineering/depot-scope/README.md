# gazipur depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The configured policy is distributed overnight stabling at powered stations, with coordinated morning starts. Main-depot bays serve maintenance and defective trains. The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-3-1474-0032-s048493 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1537-0682-s000000 | line-1 | 30 | 2,250.0 | 2,550.0 | unverified |
| line-1-0254-0960-s037529 | line-1 | 30 | 2,250.0 | 2,550.0 | unverified |
| line-2-0655-0057-s000000 | line-2 | 26 | 1,950.0 | 2,210.0 | unverified |
| line-2-1197-1482-s035200 | line-2 | 26 | 1,950.0 | 2,210.0 | unverified |
| line-3-0178-1544-s000000 | line-3 | 38 | 2,850.0 | 3,230.0 | unverified |
| line-3-1474-0032-s048493 | line-3 | 37 | 2,775.0 | 3,145.0 | unverified |
| line-4-1545-1301-s000000 | line-4 | 38 | 2,850.0 | 3,230.0 | unverified |
| line-4-0074-0112-s046961 | line-4 | 37 | 2,775.0 | 3,145.0 | unverified |
| line-5-0082-0566-s000000 | line-5 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-5-1406-0504-s030263 | line-5 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-6-0739-0235-s000000 | line-6 | 14 | 1,050.0 | 1,190.0 | unverified |
| line-6-0892-0226-s062706 | line-6 | 13 | 975.0 | 1,105.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
