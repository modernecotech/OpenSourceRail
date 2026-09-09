# dakar depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The configured policy is distributed overnight stabling at powered stations, with coordinated morning starts. Main-depot bays serve maintenance and defective trains. The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0696-0349-s040331 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0350-1820-s000000 | line-1 | 40 | 4,440.0 | 4,840.0 | unverified |
| line-1-0696-0349-s040331 | line-1 | 39 | 4,329.0 | 4,719.0 | unverified |
| line-2-0812-0380-s000000 | line-2 | 28 | 3,108.0 | 3,388.0 | unverified |
| line-2-0768-1504-s030260 | line-2 | 28 | 3,108.0 | 3,388.0 | unverified |
| line-3-0573-0432-s000000 | line-3 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-3-0223-1606-s031310 | line-3 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-4-0316-1152-s000000 | line-4 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-4-0931-0450-s026397 | line-4 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-5-0645-1815-s000000 | line-5 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-5-0993-0627-s028276 | line-5 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-6-0498-0440-s000000 | line-6 | 15 | 1,665.0 | 1,815.0 | unverified |
| line-6-0573-0432-s063534 | line-6 | 15 | 1,665.0 | 1,815.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
