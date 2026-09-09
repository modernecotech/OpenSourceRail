# maputo depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to declared depots. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-4-0067-0191-s027543 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0905-0469-s000000 | line-1 | 20 | 1,500.0 | 1,700.0 | unverified |
| line-1-0196-1087-s024333 | line-1 | 19 | 1,425.0 | 1,615.0 | unverified |
| line-2-0861-0895-s000000 | line-2 | 19 | 1,425.0 | 1,615.0 | unverified |
| line-2-0188-0550-s021664 | line-2 | 18 | 1,350.0 | 1,530.0 | unverified |
| line-3-0140-0902-s000000 | line-3 | 19 | 1,425.0 | 1,615.0 | unverified |
| line-3-0744-0377-s021917 | line-3 | 18 | 1,350.0 | 1,530.0 | unverified |
| line-4-0905-0805-s000000 | line-4 | 21 | 1,575.0 | 1,785.0 | unverified |
| line-4-0067-0191-s027543 | line-4 | 20 | 1,500.0 | 1,700.0 | unverified |
| line-5-0616-1051-s000000 | line-5 | 19 | 1,425.0 | 1,615.0 | unverified |
| line-5-0626-0233-s021926 | line-5 | 18 | 1,350.0 | 1,530.0 | unverified |
| line-6-0396-0425-s000000 | line-6 | 12 | 900.0 | 1,020.0 | unverified |
| line-6-0605-0350-s051317 | line-6 | 11 | 825.0 | 935.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
