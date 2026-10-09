# sayun depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0491-0047-s013053 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0465-0310-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-0454-0403-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0412-0397-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0464-0081-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-0434-0154-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0273-0600-s000000 | line-1 | 15 | 585.0 | 735.0 | unverified |
| line-1-0491-0047-s013053 | line-1 | 15 | 585.0 | 735.0 | unverified |
| line-2-0465-0310-s000000 | line-2 | 6 | 234.0 | 294.0 | unverified |
| line-2-0283-0307-s003677 | line-2 | 5 | 195.0 | 245.0 | unverified |
| line-3-0454-0403-s000000 | line-3 | 7 | 273.0 | 343.0 | unverified |
| line-3-0258-0373-s004169 | line-3 | 7 | 273.0 | 343.0 | unverified |
| line-4-0412-0397-s000000 | line-4 | 7 | 273.0 | 343.0 | unverified |
| line-4-0260-0463-s004429 | line-4 | 7 | 273.0 | 343.0 | unverified |
| line-5-0464-0081-s000000 | line-5 | 9 | 351.0 | 441.0 | unverified |
| line-5-0337-0240-s006614 | line-5 | 9 | 351.0 | 441.0 | unverified |
| line-6-0434-0154-s000000 | line-6 | 7 | 273.0 | 343.0 | unverified |
| line-6-0547-0264-s003745 | line-6 | 6 | 234.0 | 294.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
