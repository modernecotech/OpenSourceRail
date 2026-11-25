# Baghdad metropolitan rail network

This is one connected planning network for Baghdad, with 33 lines and 651 station points. It includes the Airport terminal approach and the routes through central Baghdad, alongside the links to the outer districts. The passenger graph has 107 proposed interchanges. A station belongs to an ordered rail line, and transfers use explicit interchange records.

![One connected map of Baghdad’s proposed railway and its walking coverage](maps/baghdad-network.png)

[Open the full map](maps/baghdad-network.png) · [Rail lines, stations and transfers in GeoJSON](maps/baghdad-network.geojson) · [Engineering input, coverage and gap data](baghdad-network.json)

## Walk to a station

The primary planning measure is a 1,200 m walk along the mapped street network. The 800 m result shows shorter access.

| Source and area | Estimated residents | Previous map within 1,200 m | Retained routes with infill | Revised network within 1,200 m | Revised network within 800 m |
|---|---:|---:|---:|---:|---:|
| worldpop-2026 · metropolitan | 8,597,980 | 72.87% | 58.22% | 72.38% | 48.54% |
| worldpop-2026 · central | 543,876 | 84.92% | 71.3% | 84.92% | 63.14% |
| ghsl-2025 · metropolitan | 7,347,247 | 73.86% | 59.81% | 73.4% | 48.85% |
| ghsl-2025 · central | 834,484 | 82.53% | 69.81% | 82.53% | 58.82% |

The metropolitan denominator covers the retained study window from 44.20° to 44.75° E and 33.05° to 33.50° N, including outlying settlements. The central denominator uses the earlier walking study window. The two population grids estimate residents independently. Street snaps up to 100 m are included in the walking distance. 26 mapped station points have no street snap in that range. Land access, crossing safety and station entrance positions still require local verification.

The orange population layer shows where the rail plan still leaves walks longer than 1,200 m or where the retained street data cannot establish a path. The geographic record provides the estimated remaining population by 1 km cell.

## Largest remaining walking gaps

The numbered areas on the map rank 4 × 4 km areas by the number of WorldPop residents beyond a 1,200 m walk. Nearby rail links are shown by straight-line proximity for alignment review.

| Map rank | Approximate gap centre | Residents beyond 1,200 m | Nearest rail alignments |
|---:|---|---:|---|
| 1 | 33.4344° N, 44.4361° E | 71,490 | M11 (1,297 m), M14 (1,604 m) |
| 2 | 33.3256° N, 44.5179° E | 68,989 | T23 (1,279 m), M03 (1,656 m) |
| 3 | 33.4022° N, 44.4833° E | 63,545 | T05 (1,043 m), M09 (1,165 m) |
| 4 | 33.3259° N, 44.4391° E | 59,640 | M05 (273 m), G09 (453 m) |
| 5 | 33.2215° N, 44.3427° E | 58,717 | M07 (1,634 m), M09 (2,018 m) |
| 6 | 33.3996° N, 44.4350° E | 55,500 | M09 (242 m), T40 (972 m) |

## Removing overlapping suburban routes

The earlier alignment shortlist measured proximity against the network used to generate it. Later additions could run alongside lines chosen in the meantime. G05 and G09, for example, left the same M02 terminus on the same mapped approach.

The new screen compares every pair of lines in the assembled map. It measures runs of at least 2 km, within 1 km and 25° of parallel in either direction. It counts approaches departing the same terminal cluster within 1 km and reports alignments within 10 m separately. Pair-km count each line pair, so three lines can count the same corridor more than once. The walking model tests changes independently using streets and station entrances in the planning data.

| Geometry check | Previous housing map | Revised map |
|---|---:|---:|
| Close parallel corridor pairs, km | 82.37 | 53.16 |
| Near-identical alignment pairs, km | 8.90 | 0.00 |
| Line pairs leaving nearby termini in parallel | 6 | 0 |

The consolidation compares the same six-minute service and housing trips with the previous map. A change must reduce the measured duplication, retain a connected passenger graph and stay within the declared limits for walking access, transfers, each destination, travel time and load concentration.

| Edited line | Revised extent | Route km removed | Reason |
|---|---|---:|---|
| G05 | G05–M01 interchange → Near حي الادريسي · M-068 | 10.81 | Keep G09 from M02 to C2 and start the distinct eastern G05 branch at its M01 interchange. |
| T13 | T13–M06 interchange → M11 infill · km 2.4 | 6.46 | Use T23 out of the shared M04 terminus and turn T13 back at its existing M06 interchange. |
| G20 | M05 infill · km 0.9 → G09–G20 interchange | 10.23 | Use M04 out of M-062 and end G20 at its existing interchange with the M02 trunk routes. |
| M13 | G11–M13 interchange → Southwest cross-city · M-209 | 5.28 | Use M07 for the southwestern departure and start M13 at its G11 interchange. |
| M12 | M09–M12 interchange → M04–M12 interchange | 4.04 | Shorten M12 at an existing transfer along the screened run with G02. |
| G07 | C1 infill · km 3.9 → G07–M13 interchange | 4.12 | Keep the C1 and M09 connections and remove the tail that parallels M07. |
| T40 | Sadr north–south · M-173 → T40–M01 interchange | 0.93 | Keep the Sadr–M01 link and test removing the short leg towards the M14 parallel section. |

The longest remaining alignments flagged for review are shown below. The machine record includes locations, all variants tested and any access penalties that stopped a proposed cut.

| Remaining pair | Approximate parallel length | Median separation |
|---|---:|---:|
| G04 / M01 | 9.17 km | 518 m |
| M03 / M06 | 5.63 km | 494 m |
| M14 / T40 | 3.68 km | 593 m |
| C2 / T20 | 3.67 km | 681 m |
| C1 / M05 | 3.20 km | 281 m |

For example, turning G04 back at M04 reduced its parallel section with M01, but took away two-change access on 1.47 percentage points of all weighted journeys. At the worst affected centre the loss was 4.31 points. The revised layout keeps that section.

The geometry screen identifies where to test sharing, shortening or rerouting. Separate catchments, turnbacks, track junctions and service capacity need explicit evidence before construction.

## Housing-to-centre journeys

The model tests 651 populated housing tiles against 6 named central destinations. WorldPop residential population represents origins outside the selected central box. Each destination has equal weight in this trial. Both walks follow mapped streets and must be within 1.2 km. Rail paths allow zero, one or two changes. A constrained search still finds a valid two-change route when a faster route would take three changes.

**Selected layout — Consolidated housing routes**. Every test uses the same six-minute directional service offer. First choose the shortest perimeter layout that stays within the trial’s access and journey-time bands. Then test central links on that layout and retain the best gain in two-change reach if one-change reach holds and the network remains shorter than the earlier grid. The consolidation then checks those journeys again after removing parallel sections.

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
| **Consolidated housing routes** | 73.56 | 4.79% | 45.12% | 71.86% | 84.8 | Within bands |

The access stage assigned journeys on 27 compatible additional links. It retained **G09** for the improvement in trips to the named centres. The machine record holds the results and reasons for rejected alignments.

In the selected layout, **27.30%** of weighted pairs miss the walking limit at one or both ends. Another **0.84%** have eligible walks but lack a rail path within two changes. The assignment chooses the fastest generalised journey among those admitted. Its transfer mix can differ from availability by transfer limit.

| Destination | Previous housing map within two changes | Revised map within two changes | Revised P90 (min) |
|---|---:|---:|---:|
| Tahrir Square | 73.17% | 72.70% | 85.5 |
| Al-Shorja market | 73.17% | 72.70% | 95.9 |
| Medical City area | 73.17% | 72.70% | 73.2 |
| Karkh / Haifa Street | 68.15% | 67.67% | 107.4 |
| Al Mansour | 73.17% | 72.70% | 80.7 |
| University of Baghdad approach | 73.17% | 72.70% | 82.4 |

At the previous housing map’s daily train-km, the selected layout could use a provisional 5.68-minute interval in each direction. The two-change reach is 71.86%; the served P90 elapsed time is 84.3 minutes. The estimate below prices the common six-minute offer.

### Example paths

| Changes | Housing tile | Destination | Rail legs | Elapsed (min) |
|---:|---|---|---|---:|
| 0 | housing-2065-1859 | Al Mansour | G04 New station · km 14 → New station · km 2.5 | 56.5 |
| 1 | housing-2068-1858 | Karkh / Haifa Street | T01 Sadr north–south · M-172 → C1 infill · km 31.2 / C1 C1 infill · km 31.2 → Karkh / Haifa Street | 45.0 |
| 2 | housing-2068-1858 | University of Baghdad approach | T01 Sadr north–south · M-172 → C1 infill · km 31.2 / C1 C1 infill · km 31.2 → Tahrir Square / C2 Tahrir Square → University of Baghdad approach | 59.8 |

### Perimeter changes retained from the housing study

| Line | Revised extent | Route km removed | Reason |
|---|---|---:|---|
| M02 | كلية المدائن الجامعة → M02 infill · km 51.9 | 0.98 | End at the retained G05 transfer before the final Dhat al-Salasil stop. |
| M03 | عركوب الحجي الشرقي interchange → مركز صحي الشاعورة | 13.02 | End the southern branch at the M08 transfer near Arkoob al-Haji al-Sharqi. |
| M04 | الحي العسكري → M04 infill · km 39 | 2.96 | End the southeastern branch at the existing T13 and T23 transfer. |
| M12 | Karkh north–south · M-187 → M04–M12 interchange | 0.69 | End the northern branch at M04. |
| M14 | M04–M14 interchange → Northern cross-city · M-220 | 2.81 | End the western branch at M04 while retaining the northern cross-city trunk. |
| M09 | M03–M09 interchange → الولداية interchange | 28.67 | Open a longer outer arc between M06 and M03, with east-side transfers on the remaining arc. |

Compared with the original grid, an estimated 67,824 residents lose their 1.2 km walk to rail. The machine record identifies the largest affected cells and every withdrawn station call. Land access, turning facilities and local housing demand need the next planning review.

### Applying the method in another city

The pathway solver accepts a station and line graph, directed street distances, explicit weighted housing origins and central destinations. Keep those inputs fixed while comparing network edits. Supply each city’s own metric street projection, geometry validator, centre weights and service case. The [Baghdad input file](residential-access.toml) records the present choices. [Reusable pathway function](holistic_pathways.py)

## Quantities and delivery on the revised map

The previous housing map and revised network below use the same rates, train service and construction resources. The separate 148 km and 605 km cost studies retain their original scope.

| Measure | Previous housing map | Revised layout |
|---|---:|---:|
| Passenger service route-km | 785.19 | 743.32 |
| Unique mapped guideway km | 776.31 | 743.28 |
| Permanent double-track km, both tracks counted | 1,552.62 | 1,486.55 |
| Passenger station sites / transfers | 681 / 110 | 651 / 107 |
| Standard girders / support locations | 77,594 / 38,830 | 74,288 / 37,177 |
| Casting, haul and erection paid hours | 6,762,712 | 6,499,808 |
| Standard-deck handover, relative day | 3,470 | 3,361 |
| Trainsets, including reserve | 592 | 564 |
| Base installed planning allowance, $bn | 43.45 | 41.58 |
| Annual operating allowance, $bn | 1.20 | 1.14 |

The deck schedule covers standard deck handover. Station, special structures, system installation and commissioning still need an integrated opening programme. [Construction work orders, labour and full estimate](NETWORK-DELIVERY.md)

## End-to-end routes

| Line | First stop | Last stop | Route km | Station points |
|---|---|---|---:|---:|
| M01 | محطة قطار المحمودية | كراج بوب الشام | 49.14 | 50 |
| M02 | كلية المدائن الجامعة | M02 infill · km 51.9 | 51.90 | 54 |
| M03 | عركوب الحجي الشرقي interchange | مركز صحي الشاعورة | 36.53 | 37 |
| M04 | الحي العسكري | M04 infill · km 39 | 39.00 | 40 |
| M05 | Al Amiriya | Near Nahrawan · M-089 | 43.50 | 42 |
| M06 | اليوسفية | صيد ديالى | 52.55 | 52 |
| M07 | مجمع الأنوار الطبي | Ishan Abu Khalifah | 39.96 | 37 |
| M08 | المدائن | مركز صحي | 48.17 | 45 |
| M09 | M03–M09 interchange | الولداية interchange | 69.09 | 73 |
| M10 | Near Hay alBinouk · M-160 | Near حي النصر · M-168 | 12.12 | 14 |
| M11 | Sadr north–south · M-169 | Near سبع قصور · M-175 | 10.08 | 11 |
| M12 | M09–M12 interchange | M04–M12 interchange | 16.91 | 23 |
| M13 | G11–M13 interchange | Southwest cross-city · M-209 | 7.47 | 11 |
| M14 | M04–M14 interchange | Northern cross-city · M-220 | 13.94 | 17 |
| C1 | Baghdad Airport terminal | Zayouna / Palestine Street | 34.34 | 38 |
| C2 | Al Mustansiriya / Turkmen Club Square | University of Baghdad approach | 15.13 | 20 |
| G02 | Karkh north–south · M-187 | M09 infill · km 5.4 | 20.28 | 19 |
| G07 | C1 infill · km 3.9 | G07–M13 interchange | 9.57 | 9 |
| G05 | G05–M01 interchange | Near حي الادريسي · M-068 | 4.91 | 6 |
| G04 | M05–M08 interchange | M14 infill · km 7.5 | 15.27 | 16 |
| G11 | C1 infill · km 2.7 | M08 infill · km 24.6 | 15.45 | 13 |
| G20 | M05 infill · km 0.9 | G09–G20 interchange | 9.96 | 9 |
| G13 | M08 infill · km 47.1 | M04 infill · km 24.9 | 14.19 | 14 |
| G08 | M13 infill · km 7.2 | M04 infill · km 0.9 | 26.01 | 24 |
| T01 | C1 infill · km 31.2 | Sadr north–south · M-172 | 6.42 | 7 |
| T05 | Northern cross-city · M-218 | M05 infill · km 23.7 | 10.24 | 9 |
| T23 | Baghdad orbital · M-138 | M04 infill · km 39 | 12.93 | 12 |
| T02 | M09 infill · km 7.8 | M11 infill · km 0.9 | 8.29 | 9 |
| T40 | Sadr north–south · M-173 | T40–M01 interchange | 6.97 | 8 |
| T20 | C2 infill · km 1.2 | M06 infill · km 31.8 | 8.50 | 8 |
| T19 | M02 infill · km 20.4 | M04 infill · km 28.5 | 12.79 | 11 |
| T13 | T13–M06 interchange | M11 infill · km 2.4 | 4.30 | 4 |
| G09 | M02 infill · km 51.9 | M05 infill · km 15 | 17.43 | 17 |

The route and service allowances need a timetable, turnback, depot, protection and operating verification. The earlier published budgets and timetables belong to their original studies.

Run `./osr design railway baghdad-network --check` to reproduce the published map and coverage. Use `--output build/baghdad-network-trial --max-through-routes 0` to compare revised station siting on the earlier routes.

Publication `b5dc645a969d824113f1af7062fb1c17ed5dc43d3cf1843fff876f77f3d5dc59`.
