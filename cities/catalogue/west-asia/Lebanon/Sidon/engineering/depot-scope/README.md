# sidon depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0055-0553-s012782 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0499-0328-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-0380-0462-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0370-0415-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0568-0433-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-0585-0374-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0585-0374-s000000 | line-1 | 15 | 585.0 | 735.0 | unverified |
| line-1-0055-0553-s012782 | line-1 | 14 | 546.0 | 686.0 | unverified |
| line-2-0499-0328-s000000 | line-2 | 7 | 273.0 | 343.0 | unverified |
| line-2-0587-0461-s003588 | line-2 | 6 | 234.0 | 294.0 | unverified |
| line-3-0380-0462-s000000 | line-3 | 12 | 468.0 | 588.0 | unverified |
| line-3-0041-0657-s009072 | line-3 | 11 | 429.0 | 539.0 | unverified |
| line-4-0370-0415-s000000 | line-4 | 5 | 195.0 | 245.0 | unverified |
| line-4-0439-0340-s002849 | line-4 | 4 | 156.0 | 196.0 | unverified |
| line-5-0568-0433-s000000 | line-5 | 6 | 234.0 | 294.0 | unverified |
| line-5-0385-0536-s004513 | line-5 | 6 | 234.0 | 294.0 | unverified |
| line-6-0585-0374-s000000 | line-6 | 6 | 234.0 | 294.0 | unverified |
| line-6-0686-0235-s003617 | line-6 | 5 | 195.0 | 245.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
