# dammam depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The policy assigns two revenue trains per selected powered station for coordinated morning starts and the remaining fleet to declared depots. Depot storage tracks are sized separately from maintenance bays; see the [station/depot allocation](../stabling/README.md). The dispatch table below diagnoses the current simulator initialization; it is not a proposed overnight parking allocation or a requirement for more depots.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0039-0318-s045782 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

The equipment reference is an unapproved sensitivity using existing repository rates. It is not added to CAPEX; allowance inclusion and installed scope remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1573-1343-s000000 | line-1 | 36 | 2,700.0 | 3,060.0 | unverified |
| line-1-0039-0318-s045782 | line-1 | 36 | 2,700.0 | 3,060.0 | unverified |
| line-2-0312-0057-s000000 | line-2 | 31 | 2,325.0 | 2,635.0 | unverified |
| line-2-1017-1325-s037719 | line-2 | 30 | 2,250.0 | 2,550.0 | unverified |
| line-3-0634-1301-s000000 | line-3 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-3-1063-0237-s029821 | line-3 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-4-1341-0225-s000000 | line-4 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-4-0878-1333-s031876 | line-4 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-5-0003-0715-s000000 | line-5 | 32 | 2,400.0 | 2,720.0 | unverified |
| line-5-1505-0499-s040518 | line-5 | 31 | 2,325.0 | 2,635.0 | unverified |
| line-6-0493-0393-s000000 | line-6 | 16 | 1,200.0 | 1,360.0 | unverified |
| line-6-0543-0380-s084934 | line-6 | 16 | 1,200.0 | 1,360.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
