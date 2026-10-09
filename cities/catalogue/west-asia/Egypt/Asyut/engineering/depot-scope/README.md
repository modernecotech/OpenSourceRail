# asyut depot scope reconciliation

Depot energy quantities reconciled: **yes**. Physical/cost/stabling closure: **open**.

The adopted planning requirement stores the full line fleet in one line-local depot, with storage slots separate from workshop bays. See the [current line-depot requirements](../line-depots/README.md). The station/distributed-stabling candidate below remains an unaccepted diagnostic, not capacity credited to the adopted depot plan.

| Depot station | PV kWp | Storage modules / kWh | Required / reference PV area m² | Additional equipment reference USD |
|---|---:|---:|---:|---:|
| line-1-0660-0667-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-2-0565-0462-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-3-0480-0214-s021053 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-4-0461-0504-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-5-0435-0662-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-6-0399-0720-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-7-0508-0256-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-8-0415-0467-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-9-0457-0630-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |
| line-10-0415-0467-s000000 | 5,000 | 80 / 40,000 | 33,333.3 / 4,000 | 5,930,000 |

Full depot PV/storage equipment is priced once in the adopted line-depot capital using repository reference rates. The incremental comparison above is diagnostic, not a second capital addition. Installed scope and quotations remain unverified.

| Initial dispatch station | Line | Trainsets | Train-body length m | Slot length with clearance m | Physical slots |
|---|---|---:|---:|---:|---|
| line-1-0660-0667-s000000 | line-1 | 12 | 594.0 | 714.0 | unverified |
| line-1-0415-0467-s007049 | line-1 | 12 | 594.0 | 714.0 | unverified |
| line-2-0565-0462-s000000 | line-2 | 31 | 1,534.5 | 1,844.5 | unverified |
| line-2-0070-1066-s017868 | line-2 | 31 | 1,534.5 | 1,844.5 | unverified |
| line-3-1023-1006-s000000 | line-3 | 37 | 1,831.5 | 2,201.5 | unverified |
| line-3-0480-0214-s021053 | line-3 | 37 | 1,831.5 | 2,201.5 | unverified |
| line-4-0461-0504-s000000 | line-4 | 9 | 445.5 | 535.5 | unverified |
| line-4-0612-0515-s005191 | line-4 | 9 | 445.5 | 535.5 | unverified |
| line-5-0435-0662-s000000 | line-5 | 20 | 990.0 | 1,190.0 | unverified |
| line-5-0062-0386-s010297 | line-5 | 19 | 940.5 | 1,130.5 | unverified |
| line-6-0399-0720-s000000 | line-6 | 6 | 297.0 | 357.0 | unverified |
| line-6-0536-0761-s003080 | line-6 | 6 | 297.0 | 357.0 | unverified |
| line-7-0508-0256-s000000 | line-7 | 8 | 396.0 | 476.0 | unverified |
| line-7-0439-0140-s004003 | line-7 | 8 | 396.0 | 476.0 | unverified |
| line-8-0415-0467-s000000 | line-8 | 11 | 544.5 | 654.5 | unverified |
| line-8-0210-0487-s005976 | line-8 | 10 | 495.0 | 595.0 | unverified |
| line-9-0457-0630-s000000 | line-9 | 20 | 990.0 | 1,190.0 | unverified |
| line-9-0937-0812-s011489 | line-9 | 20 | 990.0 | 1,190.0 | unverified |
| line-10-0415-0467-s000000 | line-10 | 8 | 396.0 | 476.0 | unverified |
| line-10-0521-0392-s003919 | line-10 | 7 | 346.5 | 416.5 | unverified |

- Operating PV/storage capacities are retained assumptions, not validated depot sizing. Reassess depot and station energy duties after distributed overnight placement and charging are represented.
- PV area is module area at the catalogue 0.15 kWp/m2, not gross land area; setbacks, access and packing require layout.
- Battery footprint and separation require supplier/fire-engineering data; no area or approval is invented.
- Dispatch queues are initial simulator placements, not an overnight operating plan. Slot lengths use one train plus 5 m at each end from RFC 0014.
- Workshop bays and passenger platforms are not credited as verified overnight stabling slots.

Required closure records: a supplier equipment/footprint schedule; located PV and battery layout; itemised budget with explicit baseline inclusions; a station-by-station healthy-fleet allocation with track IDs, usable lengths, assigned trainsets, charger sharing, security/isolation and access; and coordinated morning departures with conflict-aware evening/morning repositioning evidence.
