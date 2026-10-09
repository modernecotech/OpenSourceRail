# khouribga depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0341-0544-s006847 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0302-0386-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-0310-0321-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0418-0314-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0415-0470-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0558-0329-s000000 | line-1 | 8 | 312.0 | 392.0 | unverified |
| line-1-0341-0544-s006847 | line-1 | 8 | 312.0 | 392.0 | unverified |
| line-2-0302-0386-s000000 | line-2 | 7 | 273.0 | 343.0 | unverified |
| line-2-0494-0268-s005028 | line-2 | 7 | 273.0 | 343.0 | unverified |
| line-3-0310-0321-s000000 | line-3 | 7 | 273.0 | 343.0 | unverified |
| line-3-0463-0383-s003667 | line-3 | 6 | 234.0 | 294.0 | unverified |
| line-4-0418-0314-s000000 | line-4 | 6 | 234.0 | 294.0 | unverified |
| line-4-0316-0238-s002916 | line-4 | 5 | 195.0 | 245.0 | unverified |
| line-5-0415-0470-s000000 | line-5 | 5 | 195.0 | 245.0 | unverified |
| line-5-0410-0362-s002665 | line-5 | 4 | 156.0 | 196.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
