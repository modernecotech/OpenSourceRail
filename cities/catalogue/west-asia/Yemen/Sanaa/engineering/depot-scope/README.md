# sanaa depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-1395-1093-s044566 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0467-0820-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-0547-0553-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-1250-0793-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0646-1512-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-0722-0039-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-0291-0960-s002889 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-0937-0731-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-9-0291-0962-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-10-1145-0728-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-11-0742-0126-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0008-0203-s000000 | line-1 | 59 | 6,549.0 | 7,139.0 | unverified |
| line-1-1395-1093-s044566 | line-1 | 58 | 6,438.0 | 7,018.0 | unverified |
| line-2-0467-0820-s000000 | line-2 | 35 | 3,885.0 | 4,235.0 | unverified |
| line-2-1220-1138-s022928 | line-2 | 34 | 3,774.0 | 4,114.0 | unverified |
| line-3-0547-0553-s000000 | line-3 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-3-1262-1632-s032603 | line-3 | 30 | 3,330.0 | 3,630.0 | unverified |
| line-4-1250-0793-s000000 | line-4 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-4-0298-1042-s022084 | line-4 | 20 | 2,220.0 | 2,420.0 | unverified |
| line-5-0646-1512-s000000 | line-5 | 34 | 3,774.0 | 4,114.0 | unverified |
| line-5-0890-0164-s034649 | line-5 | 34 | 3,774.0 | 4,114.0 | unverified |
| line-6-0722-0039-s000000 | line-6 | 28 | 3,108.0 | 3,388.0 | unverified |
| line-6-0955-0906-s023479 | line-6 | 28 | 3,108.0 | 3,388.0 | unverified |
| line-7-0291-0960-s002889 | line-7 | 18 | 1,998.0 | 2,178.0 | unverified |
| line-7-0386-0761-s060227 | line-7 | 18 | 1,998.0 | 2,178.0 | unverified |
| line-8-0937-0731-s000000 | line-8 | 6 | 666.0 | 726.0 | unverified |
| line-8-1014-0712-s005129 | line-8 | 5 | 555.0 | 605.0 | unverified |
| line-9-0291-0962-s000000 | line-9 | 7 | 777.0 | 847.0 | unverified |
| line-9-0065-0965-s004999 | line-9 | 7 | 777.0 | 847.0 | unverified |
| line-10-1145-0728-s000000 | line-10 | 18 | 1,998.0 | 2,178.0 | unverified |
| line-10-1441-0516-s014952 | line-10 | 17 | 1,887.0 | 2,057.0 | unverified |
| line-11-0742-0126-s000000 | line-11 | 29 | 3,219.0 | 3,509.0 | unverified |
| line-11-0742-0735-s020946 | line-11 | 29 | 3,219.0 | 3,509.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
