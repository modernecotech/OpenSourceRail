# san-salvador depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0934-0200-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-1460-0306-s040925 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-1477-1595-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-1110-0360-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-1272-0934-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-0500-0402-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-0699-1357-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-0420-1114-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-9-0201-0997-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0934-0200-s000000 | line-1 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-1-0824-1345-s027198 | line-1 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-2-0201-0997-s000000 | line-2 | 31 | 2,325.0 | 2,635.0 | unverified |
| line-2-1460-0306-s040925 | line-2 | 31 | 2,325.0 | 2,635.0 | unverified |
| line-3-1477-1595-s000000 | line-3 | 34 | 2,550.0 | 2,890.0 | unverified |
| line-3-0611-0386-s040648 | line-3 | 33 | 2,475.0 | 2,805.0 | unverified |
| line-4-1110-0360-s000000 | line-4 | 29 | 2,175.0 | 2,465.0 | unverified |
| line-4-0191-1582-s035922 | line-4 | 28 | 2,100.0 | 2,380.0 | unverified |
| line-5-1272-0934-s000000 | line-5 | 27 | 2,025.0 | 2,295.0 | unverified |
| line-5-0069-0428-s029506 | line-5 | 27 | 2,025.0 | 2,295.0 | unverified |
| line-6-0500-0402-s000000 | line-6 | 14 | 1,050.0 | 1,190.0 | unverified |
| line-6-0610-0386-s072342 | line-6 | 14 | 1,050.0 | 1,190.0 | unverified |
| line-7-0699-1357-s000000 | line-7 | 6 | 450.0 | 510.0 | unverified |
| line-7-0614-1564-s006642 | line-7 | 6 | 450.0 | 510.0 | unverified |
| line-8-0420-1114-s000000 | line-8 | 5 | 375.0 | 425.0 | unverified |
| line-8-0261-1114-s005057 | line-8 | 5 | 375.0 | 425.0 | unverified |
| line-9-0201-0997-s000000 | line-9 | 10 | 750.0 | 850.0 | unverified |
| line-9-0375-1246-s011015 | line-9 | 10 | 750.0 | 850.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
