# colombo depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-1104-0254-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0308-0299-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-1474-0859-s034934 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0566-1078-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0665-0155-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-0155-1049-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-0760-0156-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-0608-0181-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-9-0459-0246-s003017 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-1104-0254-s000000 | line-1 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-1-0325-1220-s028531 | line-1 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-2-0308-0299-s000000 | line-2 | 23 | 2,553.0 | 2,783.0 | unverified |
| line-2-1296-0647-s023507 | line-2 | 22 | 2,442.0 | 2,662.0 | unverified |
| line-3-0048-0462-s000000 | line-3 | 33 | 3,663.0 | 3,993.0 | unverified |
| line-3-1474-0859-s034934 | line-3 | 32 | 3,552.0 | 3,872.0 | unverified |
| line-4-0566-1078-s000000 | line-4 | 22 | 2,442.0 | 2,662.0 | unverified |
| line-4-1215-0316-s022474 | line-4 | 21 | 2,331.0 | 2,541.0 | unverified |
| line-5-0665-0155-s000000 | line-5 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-5-1132-1228-s029219 | line-5 | 26 | 2,886.0 | 3,146.0 | unverified |
| line-6-0155-1049-s000000 | line-6 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-6-0871-0175-s027404 | line-6 | 27 | 2,997.0 | 3,267.0 | unverified |
| line-7-0760-0156-s000000 | line-7 | 23 | 2,553.0 | 2,783.0 | unverified |
| line-7-1339-0954-s024585 | line-7 | 23 | 2,553.0 | 2,783.0 | unverified |
| line-8-0608-0181-s000000 | line-8 | 19 | 2,109.0 | 2,299.0 | unverified |
| line-8-1402-0446-s020434 | line-8 | 18 | 1,998.0 | 2,178.0 | unverified |
| line-9-0459-0246-s003017 | line-9 | 16 | 1,776.0 | 1,936.0 | unverified |
| line-9-0608-0181-s066009 | line-9 | 16 | 1,776.0 | 1,936.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
