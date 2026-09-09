# faisalabad depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The configured policy is distributed overnight stabling at powered stations, with coordinated morning starts. Main-depot bays serve maintenance and defective trains. The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0297-1294-s032259 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0955-0272-s000000 | line-1 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-1-0297-1294-s032259 | line-1 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-2-0495-0853-s000000 | line-2 | 21 | 2,331.0 | 2,541.0 | unverified |
| line-2-0790-0092-s022907 | line-2 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-3-0905-0962-s000000 | line-3 | 21 | 2,331.0 | 2,541.0 | unverified |
| line-3-0600-0121-s023068 | line-3 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-4-0291-0369-s000000 | line-4 | 21 | 2,331.0 | 2,541.0 | unverified |
| line-4-1172-0736-s022796 | line-4 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-5-0403-0615-s000000 | line-5 | 25 | 2,775.0 | 3,025.0 | unverified |
| line-5-1295-0129-s024748 | line-5 | 24 | 2,664.0 | 2,904.0 | unverified |
| line-6-0620-0341-s000000 | line-6 | 11 | 1,221.0 | 1,331.0 | unverified |
| line-6-0686-0302-s042262 | line-6 | 10 | 1,110.0 | 1,210.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
