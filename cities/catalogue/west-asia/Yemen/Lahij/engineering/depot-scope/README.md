# lahij depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0584-0390-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0280-0408-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-0336-0362-s009190 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0181-0377-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0352-0403-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-0463-0386-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-0181-0377-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0584-0390-s000000 | line-1 | 11 | 429.0 | 539.0 | unverified |
| line-1-0181-0377-s008179 | line-1 | 10 | 390.0 | 490.0 | unverified |
| line-2-0280-0408-s000000 | line-2 | 9 | 351.0 | 441.0 | unverified |
| line-2-0581-0385-s006222 | line-2 | 8 | 312.0 | 392.0 | unverified |
| line-3-0693-0552-s000000 | line-3 | 13 | 507.0 | 637.0 | unverified |
| line-3-0336-0362-s009190 | line-3 | 13 | 507.0 | 637.0 | unverified |
| line-4-0181-0377-s000000 | line-4 | 9 | 351.0 | 441.0 | unverified |
| line-4-0287-0162-s006669 | line-4 | 8 | 312.0 | 392.0 | unverified |
| line-5-0352-0403-s000000 | line-5 | 9 | 351.0 | 441.0 | unverified |
| line-5-0512-0714-s007545 | line-5 | 9 | 351.0 | 441.0 | unverified |
| line-6-0463-0386-s000000 | line-6 | 5 | 195.0 | 245.0 | unverified |
| line-6-0388-0382-s002796 | line-6 | 4 | 156.0 | 196.0 | unverified |
| line-7-0181-0377-s000000 | line-7 | 8 | 312.0 | 392.0 | unverified |
| line-7-0052-0213-s005816 | line-7 | 7 | 273.0 | 343.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
