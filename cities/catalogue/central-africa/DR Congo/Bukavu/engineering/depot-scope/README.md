# bukavu depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0325-0925-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0859-1060-s022005 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-0764-0574-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0482-0500-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0616-0445-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-0632-0416-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-0396-0437-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-0571-0521-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-9-0642-0400-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0325-0925-s000000 | line-1 | 24 | 1,188.0 | 1,428.0 | unverified |
| line-1-0642-0400-s013595 | line-1 | 24 | 1,188.0 | 1,428.0 | unverified |
| line-2-0309-0394-s000000 | line-2 | 38 | 1,881.0 | 2,261.0 | unverified |
| line-2-0859-1060-s022005 | line-2 | 38 | 1,881.0 | 2,261.0 | unverified |
| line-3-0764-0574-s000000 | line-3 | 29 | 1,435.5 | 1,725.5 | unverified |
| line-3-0104-0927-s017441 | line-3 | 28 | 1,386.0 | 1,666.0 | unverified |
| line-4-0482-0500-s000000 | line-4 | 13 | 643.5 | 773.5 | unverified |
| line-4-0411-0288-s005623 | line-4 | 12 | 594.0 | 714.0 | unverified |
| line-5-0616-0445-s000000 | line-5 | 7 | 346.5 | 416.5 | unverified |
| line-5-0763-0487-s003288 | line-5 | 7 | 346.5 | 416.5 | unverified |
| line-6-0632-0416-s000000 | line-6 | 7 | 346.5 | 416.5 | unverified |
| line-6-0513-0338-s003026 | line-6 | 7 | 346.5 | 416.5 | unverified |
| line-7-0396-0437-s000000 | line-7 | 12 | 594.0 | 714.0 | unverified |
| line-7-0561-0236-s005938 | line-7 | 12 | 594.0 | 714.0 | unverified |
| line-8-0571-0521-s000000 | line-8 | 10 | 495.0 | 595.0 | unverified |
| line-8-0813-0612-s005594 | line-8 | 9 | 445.5 | 535.5 | unverified |
| line-9-0642-0400-s000000 | line-9 | 15 | 742.5 | 892.5 | unverified |
| line-9-0344-0353-s007824 | line-9 | 15 | 742.5 | 892.5 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
