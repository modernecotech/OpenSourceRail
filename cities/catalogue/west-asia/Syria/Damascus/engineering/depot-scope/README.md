# damascus depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0370-1314-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0991-0976-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-1040-0695-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0314-0227-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-1174-0240-s030115 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-0575-0379-s002275 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-0819-0786-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-1040-0713-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-9-1022-0792-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0370-1314-s000000 | line-1 | 31 | 2,325.0 | 2,635.0 | unverified |
| line-1-0839-0361-s028546 | line-1 | 30 | 2,250.0 | 2,550.0 | unverified |
| line-2-0991-0976-s000000 | line-2 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-2-0478-0099-s028912 | line-2 | 23 | 1,725.0 | 1,955.0 | unverified |
| line-3-1040-0695-s000000 | line-3 | 23 | 1,725.0 | 1,955.0 | unverified |
| line-3-0042-0682-s029375 | line-3 | 23 | 1,725.0 | 1,955.0 | unverified |
| line-4-0314-0227-s000000 | line-4 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-4-0780-0903-s026714 | line-4 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-5-0371-0969-s000000 | line-5 | 39 | 2,925.0 | 3,315.0 | unverified |
| line-5-1174-0240-s030115 | line-5 | 39 | 2,925.0 | 3,315.0 | unverified |
| line-6-0575-0379-s002275 | line-6 | 15 | 1,125.0 | 1,275.0 | unverified |
| line-6-0615-0289-s067406 | line-6 | 15 | 1,125.0 | 1,275.0 | unverified |
| line-7-0819-0786-s000000 | line-7 | 7 | 525.0 | 595.0 | unverified |
| line-7-0687-0962-s005516 | line-7 | 6 | 450.0 | 510.0 | unverified |
| line-8-1040-0713-s000000 | line-8 | 6 | 450.0 | 510.0 | unverified |
| line-8-1163-0563-s004944 | line-8 | 6 | 450.0 | 510.0 | unverified |
| line-9-1022-0792-s000000 | line-9 | 6 | 450.0 | 510.0 | unverified |
| line-9-1238-0937-s006298 | line-9 | 5 | 375.0 | 425.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
