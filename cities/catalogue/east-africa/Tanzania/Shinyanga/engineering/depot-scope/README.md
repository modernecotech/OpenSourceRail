# shinyanga depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The configured policy is distributed overnight stabling at powered stations, with coordinated morning starts. Main-depot bays serve maintenance and defective trains. The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0494-0328-s015942 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0031-0708-s000000 | line-1 | 16 | 624.0 | 784.0 | unverified |
| line-1-0494-0328-s015942 | line-1 | 16 | 624.0 | 784.0 | unverified |
| line-2-0254-0114-s000000 | line-2 | 10 | 390.0 | 490.0 | unverified |
| line-2-0468-0382-s009583 | line-2 | 10 | 390.0 | 490.0 | unverified |
| line-3-0422-0428-s000000 | line-3 | 12 | 468.0 | 588.0 | unverified |
| line-3-0661-0272-s011259 | line-3 | 12 | 468.0 | 588.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
