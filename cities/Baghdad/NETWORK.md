# Baghdad metropolitan rail network

This is one connected planning network for Baghdad, with 37 lines and 656 station points. It includes the Airport terminal approach and the routes through central Baghdad, alongside the links to the outer districts. The passenger graph has 109 proposed interchanges. A station belongs to an ordered rail line, and transfers use explicit interchange records.

![One connected map of Baghdad’s proposed railway and its walking coverage](maps/baghdad-network.png)

[Open the full map](maps/baghdad-network.png) · [Rail lines, stations and transfers in GeoJSON](maps/baghdad-network.geojson) · [Engineering input, coverage and gap data](baghdad-network.json)

## Walk to a station

The primary planning measure is a 1,200 m walk along the mapped street network. The 800 m result shows shorter access.

| Source and area | Estimated residents | Previous map within 1,200 m | Retained routes with infill | Revised network within 1,200 m | Revised network within 800 m |
|---|---:|---:|---:|---:|---:|
| worldpop-2026 · metropolitan | 8,597,980 | 72.38% | 58.22% | 74.88% | 51.4% |
| worldpop-2026 · central | 543,876 | 84.92% | 71.3% | 86.16% | 63.69% |
| ghsl-2025 · metropolitan | 7,347,247 | 73.4% | 59.81% | 75.18% | 50.47% |
| ghsl-2025 · central | 834,484 | 82.53% | 69.81% | 83.55% | 59.31% |

The metropolitan denominator covers the retained study window from 44.20° to 44.75° E and 33.05° to 33.50° N, including outlying settlements. The central denominator uses the earlier walking study window. The two population grids estimate residents independently. Street snaps up to 100 m are included in the walking distance. 26 mapped station points have no street snap in that range. Land access, crossing safety and station entrance positions still require local verification.

The orange population layer shows where the rail plan still leaves walks longer than 1,200 m or where the retained street data cannot establish a path. The geographic record provides the estimated remaining population by 1 km cell.

## Largest remaining walking gaps

The numbered areas on the map rank 4 × 4 km areas by the number of WorldPop residents beyond a 1,200 m walk. Nearby rail links are shown by straight-line proximity for alignment review.

| Map rank | Approximate gap centre | Residents beyond 1,200 m | Nearest rail alignments |
|---:|---|---:|---|
| 1 | 33.3249° N, 44.4398° E | 55,739 | M05 (398 m), G09 (566 m) |
| 2 | 33.4391° N, 44.4391° E | 42,706 | D-1033-930-50 (1,024 m), M11 (1,111 m) |
| 3 | 33.3665° N, 44.2560° E | 41,417 | M08 (1,061 m), M02 (1,840 m) |
| 4 | 33.2535° N, 44.5154° E | 40,851 | T19 (1,582 m), M02 (2,030 m) |
| 5 | 33.3651° N, 44.5203° E | 40,357 | M06 (506 m), M03 (753 m) |
| 6 | 33.3695° N, 44.4736° E | 37,163 | T23 (254 m), T13 (1,233 m) |

## Redesigning the trunks, stops and dense gaps

The study starts with alternatives for the cross-city trunks and outer branches. It tests changes to those layouts and reallocates route length to neighbourhoods with the largest shortfalls in street-walk access. It joins stations only at a mapped shared platform site or through an explicit measured two-way street link between separate platforms.

Parallel length sums overlapping runs for each line pair, for routes separated by up to 1 km over at least 2 km with similar bearings. The station column counts pairs of distinct sites closer than 280 m. The selection also checks total route length, access to each named centre, two-change reach and travel time.

| Measure | Published housing network | Revised network |
|---|---:|---:|
| Close parallel length, pair-km | 53.16 | 40.85 |
| Station site pairs within 280 m | 20 | 18 |
| Route-km | 743.32 | 740.29 |
| Physical station sites | 651 | 656 |

**Selected layout — Metropolitan cross-city trunks with the eastern interchange link with dense-gap routes and revised stations.** The fixed priority areas gain walking access for an estimated **236,545 residents**. The station review combines or removes 3 close calls and models 8 two-way street links between separate sites.

| New route on map | Planning ID | First and last interchange | Route km |
|---|---|---|---:|
| D1 | `D-1035-927-09` | New station · km 11.75 → M03–M05 interchange | 5.63 |
| D2 | `D-1034-929-80` | M09 infill · km 20.1 → New station · km 1.25 | 4.63 |
| D3 | `D-1033-929-34` | M09 infill · km 10.8 → New station · km 4 | 4.76 |
| D4 | `D-1033-930-50` | Mahmoudiya–Bob al-Sham · M-015 → Northern cross-city · M-218 | 7.25 |
| D5 | `D-1031-924-02` | M07 infill · km 36.6 → M09 infill · km 65.1 | 4.72 |

| Trunk change | Disposition | Reason |
|---|---|---|
| G08 | withdraw line | Use M08, M04 and G13 for west-bank crossings. Replace the T20 central approach with C2 and keep T20 between M05 and M06 for eastern transfers. Keep both approaches to M01 and Sadr. |
| T20 | trim | Use C2 for the central approach and run the independent eastern T20 link between M05 and M06. |

| Combined station or retained stop | Source station IDs | Disposition |
|---|---|---|
| G02–G09 interchange | G02-S12, G09-S06 | shared site |
| G20–M02 interchange | X-G20-M02-a8f3b7b198, M02-infill-51000 | retired close call |
| G02–M09 interchange | X-G02-M09-81b67738bd, M09-infill-72600 | retired close call |

### Population still outside a 1.2 km walk in the priority areas

The same 4 km areas and their WorldPop pixels are used before and after, so gains in one district do not hide a worse gap in another.

| Area centre | Before | Revised | Change |
|---|---:|---:|---:|
| 33.4351° N, 44.4315° E | 71,492 | 42,706 | -28,786 |
| 33.3273° N, 44.5175° E | 68,990 | 29,236 | -39,754 |
| 33.3992° N, 44.4745° E | 63,547 | 12,296 | -51,251 |
| 33.3273° N, 44.4315° E | 59,641 | 55,740 | -3,901 |
| 33.2195° N, 44.3455° E | 58,716 | 22,860 | -35,856 |
| 33.3992° N, 44.4315° E | 55,500 | 12,372 | -43,128 |
| 33.3992° N, 44.5175° E | 48,390 | 33,895 | -14,495 |
| 33.2555° N, 44.5175° E | 45,965 | 40,851 | -5,114 |
| 33.3633° N, 44.4315° E | 43,906 | 30,640 | -13,266 |
| 33.3633° N, 44.2595° E | 42,410 | 41,415 | -995 |

### Tested layouts

| Trunk layout and subsequent gap routes | Route km | Close pair-km | Gap gain | Walking gain | Decision |
|---|---:|---:|---:|---:|---|
| Metropolitan cross-city trunks with the eastern interchange link | 740.29 | 40.85 | +236,545 | +2.50 pp | Selected |
| Metropolitan cross-city trunks with fewer feeders | 735.38 | 38.45 | +234,156 | +2.34 pp | Eligible |
| Metropolitan routes with fewer parallel feeders | 715.37 | 24.38 | +198,415 | +1.52 pp | p90 increase min |
| One eastern approach and fewer west-bank routes | 737.96 | 41.54 | +228,972 | +2.12 pp | Eligible |

The GIS and machine record retain the pedestrian walks and tested route geometry. Curve design, land and utility access, street crossing safety, rail junctions and step-free interchange layouts are open engineering tasks.

## Housing-to-centre journeys

The model tests 651 populated housing tiles against 6 named central destinations. WorldPop residential population represents origins outside the selected central box. Each destination has equal weight in this trial. Both walks follow mapped streets and must be within 1.2 km. Rail paths allow zero, one or two changes. A constrained search still finds a valid two-change route when a faster route would take three changes.

**Selected layout — Trunks, shared stations and dense-gap routes**. Every comparison uses the same six-minute directional service. The earlier layouts show how the published housing network was reached. The same journeys test the new trunk and station layouts.

| Layout | Route km removed | Direct available | Within one change | Within two changes | P90 elapsed (min) | Access screen |
|---|---:|---:|---:|---:|---:|---|
| Earlier grid | 0.00 | 4.68% | 41.39% | 68.45% | 86.0 | Within bands |
| Low-impact terminal trims | 20.46 | 4.68% | 41.39% | 68.45% | 86.0 | Within bands |
| Western and outer tail trims | 36.59 | 4.68% | 41.28% | 68.45% | 86.0 | Within bands |
| Extended feeder trims | 47.02 | 4.68% | 41.28% | 68.00% | 86.0 | destination loss |
| Shorter open orbital | 37.18 | 4.68% | 41.38% | 68.43% | 85.9 | Within bands |
| East-facing orbital arc | 49.12 | 4.68% | 41.28% | 68.40% | 86.5 | Within bands |
| Western bypass withdrawal | 40.73 | 4.68% | 41.39% | 68.01% | 86.0 | walking loss |
| East-facing orbital arc with G09 | 31.69 | 4.79% | 45.85% | 72.33% | 84.9 | Within bands |
| Consolidated housing routes | 73.56 | 4.79% | 45.12% | 71.86% | 84.8 | Within bands |
| **Trunks, shared stations and dense-gap routes** | 76.59 | 4.79% | 46.86% | 73.95% | 83.4 | Within bands |

The access stage assigned journeys on 27 compatible additional links. It retained **G09** for the improvement in trips to the named centres. The machine record holds the results and reasons for rejected alignments.

In the selected layout, **25.34%** of weighted pairs miss the walking limit at one or both ends. Another **0.71%** have eligible walks but lack a rail path within two changes. The assignment chooses the fastest generalised journey among those admitted. Its transfer mix can differ from availability by transfer limit.

| Destination | Previous housing map within two changes | Revised map within two changes | Revised P90 (min) |
|---|---:|---:|---:|
| Tahrir Square | 72.70% | 74.66% | 75.7 |
| Al-Shorja market | 72.70% | 74.66% | 96.0 |
| Medical City area | 72.70% | 74.66% | 74.2 |
| Karkh / Haifa Street | 67.67% | 71.16% | 96.2 |
| Al Mansour | 72.70% | 74.66% | 82.8 |
| University of Baghdad approach | 72.70% | 73.90% | 83.4 |

At the previous housing map’s daily train-km, the selected layout could use a provisional 5.98-minute interval in each direction. The two-change reach is 73.95%; the served P90 elapsed time is 83.4 minutes. The estimate below prices the common six-minute offer.

### Example paths

| Changes | Housing tile | Destination | Rail legs | Elapsed (min) |
|---:|---|---|---|---:|
| 0 | housing-2065-1859 | Al Mansour | G04 New station · km 14 → New station · km 2.5 | 56.5 |
| 1 | housing-2068-1858 | Karkh / Haifa Street | T01 Sadr north–south · M-172 → C1 infill · km 31.2 / C1 C1 infill · km 31.2 → Karkh / Haifa Street | 46.0 |
| 2 | housing-2068-1858 | University of Baghdad approach | T01 Sadr north–south · M-172 → C1 infill · km 31.2 / C1 C1 infill · km 31.2 → Tahrir Square / C2 Tahrir Square → University of Baghdad approach | 60.8 |

### Perimeter changes retained from the housing study

| Line | Revised extent | Route km removed | Reason |
|---|---|---:|---|
| M02 | كلية المدائن الجامعة → M02 infill · km 51.9 | 0.98 | End at the retained G05 transfer before the final Dhat al-Salasil stop. |
| M03 | عركوب الحجي الشرقي interchange → مركز صحي الشاعورة | 13.02 | End the southern branch at the M08 transfer near Arkoob al-Haji al-Sharqi. |
| M04 | الحي العسكري → M04 infill · km 39 | 2.96 | End the southeastern branch at the existing T13 and T23 transfer. |
| M12 | Karkh north–south · M-187 → M04–M12 interchange | 0.69 | End the northern branch at M04. |
| M14 | M04–M14 interchange → Northern cross-city · M-220 | 2.81 | End the western branch at M04 while retaining the northern cross-city trunk. |
| M09 | M03–M09 interchange → الولداية interchange | 28.67 | Open a longer outer arc between M06 and M03, with east-side transfers on the remaining arc. |

Compared with the original grid, an estimated 38,443 residents lose their 1.2 km walk to rail. The machine record identifies the largest affected cells and every withdrawn station call. Land access, turning facilities and local housing demand need the next planning review.

### Applying the method in another city

The pathway solver accepts a station and line graph, directed street distances, explicit weighted housing origins and central destinations. Keep those inputs fixed while comparing network edits. Supply each city’s own metric street projection, geometry validator, centre weights and service case. The [Baghdad input file](residential-access.toml) records the present choices. [Reusable pathway function](holistic_pathways.py)

## Quantities and delivery on the revised map

The previous housing map and revised network below use the same rates, train service and construction resources. The separate 148 km and 605 km cost studies retain their original scope.

| Measure | Previous housing map | Revised layout |
|---|---:|---:|
| Passenger service route-km | 743.32 | 740.29 |
| Unique mapped guideway km | 743.28 | 740.25 |
| Permanent double-track km, both tracks counted | 1,486.55 | 1,480.50 |
| Passenger station sites / transfers | 651 / 107 | 656 / 109 |
| Standard girders / support locations | 74,288 / 37,177 | 73,980 / 37,027 |
| Casting, haul and erection paid hours | 6,499,808 | 6,427,544 |
| Standard-deck handover, relative day | 3,361 | 3,384 |
| Trainsets, including reserve | 564 | 573 |
| Base installed planning allowance, $bn | 41.58 | 41.90 |
| Annual operating allowance, $bn | 1.14 | 1.14 |

The deck schedule covers standard deck handover. Station, special structures, system installation and commissioning still need an integrated opening programme. [Construction work orders, labour and full estimate](NETWORK-DELIVERY.md)

## End-to-end routes

| Line | First stop | Last stop | Route km | Station points |
|---|---|---|---:|---:|
| M01 | محطة قطار المحمودية | كراج بوب الشام | 49.14 | 50 |
| M02 | كلية المدائن الجامعة | M02 infill · km 51.9 | 51.90 | 53 |
| M03 | عركوب الحجي الشرقي interchange | مركز صحي الشاعورة | 36.53 | 38 |
| M04 | الحي العسكري | M04 infill · km 39 | 39.00 | 40 |
| M05 | Al Amiriya | Near Nahrawan · M-089 | 43.50 | 42 |
| M06 | اليوسفية | صيد ديالى | 52.55 | 52 |
| M07 | مجمع الأنوار الطبي | Ishan Abu Khalifah | 39.96 | 37 |
| M08 | المدائن | مركز صحي | 48.17 | 45 |
| M09 | M03–M09 interchange | الولداية interchange | 69.09 | 74 |
| M10 | Near Hay alBinouk · M-160 | Near حي النصر · M-168 | 12.12 | 15 |
| M11 | Sadr north–south · M-169 | Near سبع قصور · M-175 | 10.08 | 11 |
| M12 | M09–M12 interchange | M04–M12 interchange | 16.91 | 23 |
| M13 | G11–M13 interchange | Southwest cross-city · M-209 | 7.47 | 11 |
| M14 | M04–M14 interchange | Northern cross-city · M-220 | 13.94 | 18 |
| C1 | Baghdad Airport terminal | Zayouna / Palestine Street | 34.34 | 38 |
| C2 | Al Mustansiriya / Turkmen Club Square | University of Baghdad approach | 15.13 | 20 |
| G02 | Karkh north–south · M-187 | M09 infill · km 5.4 | 20.28 | 19 |
| G07 | C1 infill · km 3.9 | G07–M13 interchange | 9.57 | 9 |
| G05 | G05–M01 interchange | Near حي الادريسي · M-068 | 4.91 | 6 |
| G04 | M05–M08 interchange | M14 infill · km 7.5 | 15.27 | 16 |
| G11 | C1 infill · km 2.7 | M08 infill · km 24.6 | 15.45 | 14 |
| G20 | M05 infill · km 0.9 | G09–G20 interchange | 9.96 | 10 |
| G13 | M08 infill · km 47.1 | M04 infill · km 24.9 | 14.19 | 14 |
| T01 | C1 infill · km 31.2 | Sadr north–south · M-172 | 6.42 | 8 |
| T05 | Northern cross-city · M-218 | M05 infill · km 23.7 | 10.24 | 9 |
| T23 | Baghdad orbital · M-138 | M04 infill · km 39 | 12.93 | 12 |
| T02 | M09 infill · km 7.8 | M11 infill · km 0.9 | 8.29 | 9 |
| T40 | Sadr north–south · M-173 | T40–M01 interchange | 6.97 | 8 |
| T20 | M05 infill · km 13.5 | M06 infill · km 31.8 | 4.50 | 5 |
| T19 | M02 infill · km 20.4 | M04 infill · km 28.5 | 12.79 | 12 |
| T13 | T13–M06 interchange | M11 infill · km 2.4 | 4.30 | 4 |
| G09 | M02 infill · km 51.9 | M05 infill · km 15 | 17.43 | 18 |
| D-1035-927-09 | New station · km 11.75 | M03–M05 interchange | 5.63 | 6 |
| D-1034-929-80 | M09 infill · km 20.1 | New station · km 1.25 | 4.63 | 5 |
| D-1033-929-34 | M09 infill · km 10.8 | New station · km 4 | 4.76 | 5 |
| D-1033-930-50 | Mahmoudiya–Bob al-Sham · M-015 | Northern cross-city · M-218 | 7.25 | 7 |
| D-1031-924-02 | M07 infill · km 36.6 | M09 infill · km 65.1 | 4.72 | 5 |

The route and service allowances need a timetable, turnback, depot, protection and operating verification. The earlier published budgets and timetables belong to their original studies.

Run `./osr design railway baghdad-network --check` to reproduce the published map and coverage. Use `--output build/baghdad-network-trial --max-through-routes 0` to compare revised station siting on the earlier routes.

Publication `948f9d04227cf0b2d54db400ab863feb9b0f11d9d35f1d4d18b7acdce43f5a0a`.
