# damascus depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0370-1314-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0478-0099-s024567 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-1005-0695-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0314-0227-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0400-1008-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-0521-0412-s003215 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0370-1314-s000000 | line-1 | 20 | 1,500.0 | 1,700.0 | unverified |
| line-1-0853-0388-s024065 | line-1 | 20 | 1,500.0 | 1,700.0 | unverified |
| line-2-0993-0946-s000000 | line-2 | 20 | 1,500.0 | 1,700.0 | unverified |
| line-2-0478-0099-s024567 | line-2 | 19 | 1,425.0 | 1,615.0 | unverified |
| line-3-1005-0695-s000000 | line-3 | 19 | 1,425.0 | 1,615.0 | unverified |
| line-3-0042-0682-s021874 | line-3 | 18 | 1,350.0 | 1,530.0 | unverified |
| line-4-0314-0227-s000000 | line-4 | 16 | 1,200.0 | 1,360.0 | unverified |
| line-4-0780-0898-s018800 | line-4 | 15 | 1,125.0 | 1,275.0 | unverified |
| line-5-0400-1008-s000000 | line-5 | 20 | 1,500.0 | 1,700.0 | unverified |
| line-5-1174-0240-s023388 | line-5 | 19 | 1,425.0 | 1,615.0 | unverified |
| line-6-0521-0412-s003215 | line-6 | 12 | 900.0 | 1,020.0 | unverified |
| line-6-0603-0293-s055867 | line-6 | 11 | 825.0 | 935.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
