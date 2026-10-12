# ramadi depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0491-0802-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0654-0283-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-0421-0641-s017263 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0491-0802-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0529-0212-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0491-0802-s000000 | line-1 | 22 | 1,089.0 | 1,309.0 | unverified |
| line-1-0527-0190-s012600 | line-1 | 21 | 1,039.5 | 1,249.5 | unverified |
| line-2-0654-0283-s000000 | line-2 | 23 | 1,138.5 | 1,368.5 | unverified |
| line-2-0361-0731-s014321 | line-2 | 23 | 1,138.5 | 1,368.5 | unverified |
| line-3-0476-0055-s000000 | line-3 | 28 | 1,386.0 | 1,666.0 | unverified |
| line-3-0421-0641-s017263 | line-3 | 28 | 1,386.0 | 1,666.0 | unverified |
| line-4-0491-0802-s000000 | line-4 | 9 | 445.5 | 535.5 | unverified |
| line-4-0362-0934-s005639 | line-4 | 9 | 445.5 | 535.5 | unverified |
| line-5-0529-0212-s000000 | line-5 | 9 | 445.5 | 535.5 | unverified |
| line-5-0613-0038-s005082 | line-5 | 9 | 445.5 | 535.5 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
