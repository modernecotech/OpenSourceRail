# erbil depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0065-0241-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0027-1326-s029912 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-0615-0487-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0001-1021-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0828-0463-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0065-0241-s000000 | line-1 | 25 | 1,875.0 | 2,125.0 | unverified |
| line-1-1113-0956-s028707 | line-1 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-2-1138-0526-s000000 | line-2 | 24 | 1,800.0 | 2,040.0 | unverified |
| line-2-0027-1326-s029912 | line-2 | 23 | 1,725.0 | 1,955.0 | unverified |
| line-3-0615-0487-s000000 | line-3 | 19 | 1,425.0 | 1,615.0 | unverified |
| line-3-0605-1416-s019203 | line-3 | 18 | 1,350.0 | 1,530.0 | unverified |
| line-4-0001-1021-s000000 | line-4 | 21 | 1,575.0 | 1,785.0 | unverified |
| line-4-1072-0734-s023734 | line-4 | 21 | 1,575.0 | 1,785.0 | unverified |
| line-5-0828-0463-s000000 | line-5 | 18 | 1,350.0 | 1,530.0 | unverified |
| line-5-0925-1287-s017620 | line-5 | 18 | 1,350.0 | 1,530.0 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
