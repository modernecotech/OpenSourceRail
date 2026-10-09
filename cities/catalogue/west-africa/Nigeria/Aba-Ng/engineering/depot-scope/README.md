# aba-ng depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0615-0713-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0575-0330-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-0541-0610-s010192 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0703-0351-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0753-0420-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-0597-0393-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-0575-0330-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-0586-0569-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-9-0852-0331-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0615-0713-s000000 | line-1 | 18 | 891.0 | 1,071.0 | unverified |
| line-1-0723-0266-s009882 | line-1 | 17 | 841.5 | 1,011.5 | unverified |
| line-2-0575-0330-s000000 | line-2 | 13 | 643.5 | 773.5 | unverified |
| line-2-0657-0561-s005358 | line-2 | 12 | 594.0 | 714.0 | unverified |
| line-3-0879-0306-s000000 | line-3 | 18 | 891.0 | 1,071.0 | unverified |
| line-3-0541-0610-s010192 | line-3 | 18 | 891.0 | 1,071.0 | unverified |
| line-4-0703-0351-s000000 | line-4 | 7 | 346.5 | 416.5 | unverified |
| line-4-0814-0387-s002518 | line-4 | 6 | 297.0 | 357.0 | unverified |
| line-5-0753-0420-s000000 | line-5 | 6 | 297.0 | 357.0 | unverified |
| line-5-0762-0538-s002849 | line-5 | 5 | 247.5 | 297.5 | unverified |
| line-6-0597-0393-s000000 | line-6 | 7 | 346.5 | 416.5 | unverified |
| line-6-0462-0387-s003081 | line-6 | 7 | 346.5 | 416.5 | unverified |
| line-7-0575-0330-s000000 | line-7 | 15 | 742.5 | 892.5 | unverified |
| line-7-0962-0262-s008303 | line-7 | 14 | 693.0 | 833.0 | unverified |
| line-8-0586-0569-s000000 | line-8 | 9 | 445.5 | 535.5 | unverified |
| line-8-0662-0384-s005108 | line-8 | 9 | 445.5 | 535.5 | unverified |
| line-9-0852-0331-s000000 | line-9 | 6 | 297.0 | 357.0 | unverified |
| line-9-0862-0463-s003160 | line-9 | 6 | 297.0 | 357.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
