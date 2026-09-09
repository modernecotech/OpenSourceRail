# kigali depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to storage on its own line. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0898-1179-s032505 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0617-0008-s000000 | line-1 | 26 | 1,950.0 | 2,210.0 | unverified |
| line-1-0898-1179-s032505 | line-1 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-2-0472-0250-s000000 | line-2 | 21 | 1,575.0 | 1,785.0 | unverified |
| line-2-0645-0967-s022830 | line-2 | 21 | 1,575.0 | 1,785.0 | unverified |
| line-3-1030-0493-s000000 | line-3 | 18 | 1,350.0 | 1,530.0 | unverified |
| line-3-0341-0561-s018537 | line-3 | 17 | 1,275.0 | 1,445.0 | unverified |
| line-4-0165-0854-s000000 | line-4 | 19 | 1,425.0 | 1,615.0 | unverified |
| line-4-0914-0292-s024190 | line-4 | 18 | 1,350.0 | 1,530.0 | unverified |
| line-5-0201-0247-s000000 | line-5 | 19 | 1,425.0 | 1,615.0 | unverified |
| line-5-0938-0832-s024924 | line-5 | 19 | 1,425.0 | 1,615.0 | unverified |
| line-6-0382-0420-s004093 | line-6 | 12 | 900.0 | 1,020.0 | unverified |
| line-6-0535-0309-s059629 | line-6 | 12 | 900.0 | 1,020.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
