# Baghdad metropolitan rail network

This is one connected planning network for Baghdad, with 32 lines and 651 station points. It includes the Airport terminal approach and the routes through central Baghdad, alongside the links to the outer districts. The passenger graph has 95 proposed interchanges. A station belongs to an ordered rail line, and transfers use explicit interchange records.

![One connected map of Baghdad’s proposed railway and its walking coverage](maps/baghdad-network.png)

[Open the full map](maps/baghdad-network.png) · [Rail lines, stations and transfers in GeoJSON](maps/baghdad-network.geojson) · [Engineering input, coverage and gap data](baghdad-network.json)

## Walk to a station

The primary planning measure is a 1,200 m walk along the mapped street network. The 800 m result shows shorter access.

| Source and area | Estimated residents | Previous map within 1,200 m | Infill reprioritised to 1,200 m | Revised network within 1,200 m | Revised network within 800 m |
|---|---:|---:|---:|---:|---:|
| worldpop-2026 · metropolitan | 8,597,980 | 57.92% | 58.22% | 72.41% | 49.01% |
| worldpop-2026 · central | 543,876 | 70.03% | 71.3% | 83.52% | 54.41% |
| ghsl-2025 · metropolitan | 7,347,247 | 59.41% | 59.81% | 72.52% | 47.73% |
| ghsl-2025 · central | 834,484 | 68.9% | 69.81% | 81.89% | 53.83% |

The metropolitan denominator covers the retained study window from 44.20° to 44.75° E and 33.05° to 33.50° N, including outlying settlements. The central denominator uses the earlier walking study window. The two population grids estimate residents independently. Street snaps up to 100 m are included in the walking distance. 36 mapped station points have no street snap in that range. Land access, crossing safety and station entrance positions still require local verification.

The orange population layer shows where the rail plan still leaves walks longer than 1,200 m or where the retained street data cannot establish a path. The geographic record provides the estimated remaining population by 1 km cell.

## Largest remaining walking gaps

The numbered areas on the map rank 4 × 4 km areas by the number of WorldPop residents beyond a 1,200 m walk. Nearby rail links are shown by straight-line proximity for alignment review.

| Map rank | Approximate gap centre | Residents beyond 1,200 m | Nearest rail alignments |
|---:|---|---:|---|
| 1 | 33.4355° N, 44.4360° E | 66,073 | M11 (1,305 m), M14 (1,722 m) |
| 2 | 33.3262° N, 44.5185° E | 65,445 | T23 (1,356 m), M03 (1,692 m) |
| 3 | 33.4022° N, 44.4836° E | 62,890 | T05 (1,061 m), M09 (1,158 m) |
| 4 | 33.2548° N, 44.5090° E | 54,564 | M02 (1,784 m), M09 (2,197 m) |
| 5 | 33.3668° N, 44.2588° E | 48,908 | M08 (966 m), T12 (966 m) |
| 6 | 33.3987° N, 44.5113° E | 48,391 | M03 (1,000 m), M10 (1,083 m) |

## Direct cross-city routes

The generator compared 40 screened alignments. This 16-route planning trial adds 16 routes totalling 152.0 route-km. Every added route has an interchange at both termini. Intermediate interchanges are included where the geometry and station screens allow them. The coverage gain in each row is measured after the routes above it are added.

| Line | First interchange | Last interchange | Length | Interchanges | Additional residents within 1,200 m |
|---|---|---|---:|---:|---:|
| T01 | C1 infill · km 31.2 | Sadr north–south · M-172 | 6.42 km | 4 | 148,958 |
| T05 | Northern cross-city · M-218 | M05 infill · km 23.7 | 10.24 km | 3 | 174,183 |
| T23 | Baghdad orbital · M-138 | M04 infill · km 39 | 12.93 km | 3 | 208,266 |
| T02 | M09 infill · km 7.8 | M11 infill · km 0.9 | 8.29 km | 4 | 79,726 |
| T40 | Sadr north–south · M-173 | M14 infill · km 5.7 | 7.90 km | 3 | 75,491 |
| T27 | C1 infill · km 3.9 | M07 infill · km 34.2 | 8.27 km | 3 | 68,863 |
| T08 | M02 infill · km 42.3 | M14 infill · km 9.3 | 10.88 km | 5 | 69,058 |
| T20 | C2 infill · km 1.2 | M06 infill · km 31.8 | 8.50 km | 3 | 51,748 |
| T17 | M03 infill · km 26.1 | M09 infill · km 2.1 | 18.74 km | 5 | 103,091 |
| T03 | Karkh / Haifa Street | جامعة النهرين مستشفى التعليمي | 7.94 km | 5 | 39,565 |
| T16 | Near Hay Tabuk · M-154 | M06 infill · km 16.2 | 9.31 km | 3 | 40,072 |
| T35 | M01 infill · km 24 | C1–M09 interchange | 9.36 km | 3 | 40,124 |
| T13 | M04 infill · km 39 | M11 infill · km 2.4 | 10.76 km | 3 | 44,049 |
| T12 | مركز صحي | Near Al Kadhimiyah · M-197 | 7.34 km | 4 | 29,194 |
| T07 | Near الاورفلي · M-165 | M14 infill · km 10.8 | 6.21 km | 2 | 19,572 |
| T31 | Al-Madain–Dhat al-Salasil · M-044 | Al Mansour | 8.89 km | 4 | 27,838 |

The centre lines are direct planning alignments. Detailed vertical profiles, curve design, property access, bridge clearances and platform layouts still need engineering. The GeoJSON and JSON retain the tested geometry and source evidence.

## How the network is generated

1. Assemble the timed alignments into ordered passenger lines. Incorporate the corrected geographic Airport approach and retain the central station calls as part of the same network. Show only lines with a complete route.
2. Establish explicit transfer locations. A crossing on the map alone carries no transfer. Check that every line and station can be reached through a single passenger graph.
3. Test station locations along the rail lines every 300 m. Screen new stops within 650 m of another stop on the same line, over mapped water or beyond the street snap. The spacing and sampling interval are editable planning settings.
4. Repeatedly choose the location that reaches the most additional WorldPop residents within 1,200 m over the street graph. Break ties by 800 m gain, then line and chainage.
5. Generate direct routes anchored at stations on the retained network. Check dry street-accessible stations, mapped water crossings and intermediate interchange geometry. Rank tested routes by marginal residents within 1,200 m per added route-km. Recalculate coverage after each addition so overlapping catchments receive credit once.
6. Recalculate both walking thresholds against WorldPop and GHS-POP for the final stations. Verify the connected passenger graph, all route termini and intermediate transfer locations.

## End-to-end routes

| Line | First stop | Last stop | Route km | Station points |
|---|---|---|---:|---:|
| M01 | محطة قطار المحمودية | كراج بوب الشام | 49.14 | 49 |
| M02 | كلية المدائن الجامعة | ذات السلاسل | 52.88 | 53 |
| M03 | قرية الثوار ( قرية شيخ محمد كشكول ) | مركز صحي الشاعورة | 49.56 | 44 |
| M04 | الحي العسكري | Near Husain al Latif · M-073 | 41.96 | 42 |
| M05 | Al Amiriya | Near Nahrawan · M-089 | 43.50 | 40 |
| M06 | اليوسفية | صيد ديالى | 52.55 | 51 |
| M07 | مجمع الأنوار الطبي | Ishan Abu Khalifah | 39.96 | 37 |
| M08 | المدائن | مركز صحي | 48.17 | 44 |
| M09 | مستوصف الكريعات | Returns to first stop | 97.75 | 96 |
| M10 | Near Hay alBinouk · M-160 | Near حي النصر · M-168 | 12.12 | 14 |
| M11 | Sadr north–south · M-169 | Near سبع قصور · M-175 | 10.08 | 11 |
| M12 | Karkh north–south · M-187 | Karkh north–south · M-200 | 21.63 | 30 |
| M13 | Southwest cross-city · M-201 | Southwest cross-city · M-209 | 12.75 | 16 |
| M14 | Northern cross-city · M-210 | Northern cross-city · M-220 | 16.75 | 19 |
| C1 | Baghdad Airport terminal | Zayouna / Palestine Street | 34.34 | 37 |
| C2 | Al Mustansiriya / Turkmen Club Square | University of Baghdad approach | 15.13 | 18 |
| T01 | C1 infill · km 31.2 | Sadr north–south · M-172 | 6.42 | 7 |
| T05 | Northern cross-city · M-218 | M05 infill · km 23.7 | 10.24 | 9 |
| T23 | Baghdad orbital · M-138 | M04 infill · km 39 | 12.93 | 12 |
| T02 | M09 infill · km 7.8 | M11 infill · km 0.9 | 8.29 | 9 |
| T40 | Sadr north–south · M-173 | M14 infill · km 5.7 | 7.90 | 8 |
| T27 | C1 infill · km 3.9 | M07 infill · km 34.2 | 8.27 | 8 |
| T08 | M02 infill · km 42.3 | M14 infill · km 9.3 | 10.88 | 12 |
| T20 | C2 infill · km 1.2 | M06 infill · km 31.8 | 8.50 | 8 |
| T17 | M03 infill · km 26.1 | M09 infill · km 2.1 | 18.74 | 17 |
| T03 | Karkh / Haifa Street | جامعة النهرين مستشفى التعليمي | 7.94 | 9 |
| T16 | Near Hay Tabuk · M-154 | M06 infill · km 16.2 | 9.31 | 9 |
| T35 | M01 infill · km 24 | C1–M09 interchange | 9.36 | 8 |
| T13 | M04 infill · km 39 | M11 infill · km 2.4 | 10.76 | 9 |
| T12 | مركز صحي | Near Al Kadhimiyah · M-197 | 7.34 | 8 |
| T07 | Near الاورفلي · M-165 | M14 infill · km 10.8 | 6.21 | 6 |
| T31 | Al-Madain–Dhat al-Salasil · M-044 | Al Mansour | 8.89 | 8 |

The revised routes and stops need their own running times, depot and turnback design, protection, fleet and cost evaluation. The earlier budgets and timetables belong to their original studies.

Run `./osr design railway baghdad-network --check` to reproduce the published map and coverage. Use `--output build/baghdad-network-trial --max-through-routes 0` to compare revised station siting on the earlier routes.

Publication `a9ff8ae101935d45fa85f3bc781fdd37986a6605c1cd2f1a9c7f0fb7f10caabc`.
