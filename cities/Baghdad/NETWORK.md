# Baghdad metropolitan rail network

This is one connected planning network for Baghdad, with 32 lines and 705 station points. It includes the Airport terminal approach and the routes through central Baghdad, alongside the links to the outer districts. The passenger graph has 108 proposed interchanges. A station belongs to an ordered rail line, and transfers use explicit interchange records.

![One connected map of Baghdad’s proposed railway and its walking coverage](maps/baghdad-network.png)

[Open the full map](maps/baghdad-network.png) · [Rail lines, stations and transfers in GeoJSON](maps/baghdad-network.geojson) · [Engineering input, coverage and gap data](baghdad-network.json)

## Walk to a station

The primary planning measure is a 1,200 m walk along the mapped street network. The 800 m result shows shorter access.

| Source and area | Estimated residents | Previous map within 1,200 m | Retained routes with infill | Revised network within 1,200 m | Revised network within 800 m |
|---|---:|---:|---:|---:|---:|
| worldpop-2026 · metropolitan | 8,597,980 | 72.41% | 58.22% | 73.09% | 49.44% |
| worldpop-2026 · central | 543,876 | 83.52% | 71.3% | 83.82% | 59.04% |
| ghsl-2025 · metropolitan | 7,347,247 | 72.52% | 59.81% | 73.89% | 49.59% |
| ghsl-2025 · central | 834,484 | 81.89% | 69.81% | 81.86% | 56.59% |

The metropolitan denominator covers the retained study window from 44.20° to 44.75° E and 33.05° to 33.50° N, including outlying settlements. The central denominator uses the earlier walking study window. The two population grids estimate residents independently. Street snaps up to 100 m are included in the walking distance. 36 mapped station points have no street snap in that range. Land access, crossing safety and station entrance positions still require local verification.

The orange population layer shows where the rail plan still leaves walks longer than 1,200 m or where the retained street data cannot establish a path. The geographic record provides the estimated remaining population by 1 km cell.

## Largest remaining walking gaps

The numbered areas on the map rank 4 × 4 km areas by the number of WorldPop residents beyond a 1,200 m walk. Nearby rail links are shown by straight-line proximity for alignment review.

| Map rank | Approximate gap centre | Residents beyond 1,200 m | Nearest rail alignments |
|---:|---|---:|---|
| 1 | 33.4344° N, 44.4361° E | 71,490 | M11 (1,297 m), M14 (1,604 m) |
| 2 | 33.3262° N, 44.5185° E | 65,445 | T23 (1,356 m), M03 (1,692 m) |
| 3 | 33.4022° N, 44.4833° E | 63,545 | T05 (1,043 m), M09 (1,165 m) |
| 4 | 33.3264° N, 44.4383° E | 62,931 | M05 (208 m), C1 (964 m) |
| 5 | 33.2215° N, 44.3427° E | 58,717 | M07 (1,634 m), M09 (2,018 m) |
| 6 | 33.3996° N, 44.4350° E | 55,500 | M09 (242 m), T40 (972 m) |

## Network patterns and point-to-point trips

The earlier short-link map, the east–west and north–south grid, and the inner-ring alternative use the same synthetic origin–destination demand. The first grid trials use the earlier map’s added route length as a ceiling. The mixed grids keep selected short links to recover access where the longer routes leave gaps.

| Pattern | Spines / local links / rings | Added route-km | Within 1.2 km | All OD served | All OD with zero or one transfer | P90 elapsed (min) | Busiest line share | Busiest directed segment share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Previous short-link map | 0 / 16 / 1 | 152.0 | 72.41% | 62.45% | 28.10% | 78.8 | 10.04% | 4.73% |
| Grid with outer ring | 8 / 0 / 1 | 140.8 | 63.45% | 45.13% | 21.37% | 86.4 | 17.66% | 11.64% |
| Grid with two rings | 6 / 0 / 2 | 141.7 | 62.84% | 44.70% | 21.47% | 86.6 | 17.49% | 12.10% |
| Grid and local links with outer ring | 8 / 7 / 1 | 207.9 | 72.58% | 66.14% | 28.96% | 79.3 | 11.32% | 6.70% |
| Grid and local links with two rings | 6 / 8 / 2 | 220.9 | 72.00% | 65.83% | 30.44% | 81.4 | 11.05% | 7.65% |
| Inner ring added to the same mixed grid | 8 / 7 / 2 | 249.0 | 72.90% | 66.14% | 30.78% | 79.0 | 10.74% | 6.63% |
| **Grid with targeted relief link** | 8 / 8 / 1 | 218.6 | 73.09% | 66.14% | 29.66% | 78.4 | 10.27% | 5.15% |

The planning map retains **T13** as a relief link. Adding it to the best initial grid lowered the peak demand per departure and improved the combined journey and load comparison. The two-ring overlay tests the same initial grid with the inner ring added.

The map shows **Grid with targeted relief link**. The selection rule first seeks to restore the previous 1.2 km access. It then compares each grid’s one-transfer journey share, 90th-percentile time on matched journeys and busiest segment share with the earlier map, choosing the grid with the smallest worst relative change. If none restore coverage, the rule minimises the walking-access shortfall first.

For journeys served in both the selected and earlier networks, the weighted mean elapsed-time change is **+0.50 minutes**. The assignment holds daily train-km equal to the previous map’s service scenario. It includes walking, in-vehicle time, stops, waiting and a transfer penalty. The busiest-line share is a share of boardings. The busiest-segment share is a share of served journeys. These loads screen transfer pressure. Passenger counts, timetables and train capacities remain open.

Illustrative synthetic origin–destination demand. Population-weighted centroids represented by a retained pixel in each metric tile. Ordered OD weights use origin population × destination population × exponential distance decay.

The inner orbital trial follows the retained road corridors across the Tigris at Al-A’imma and Al-Jadriya. Its stations and interchanges support a planning comparison. Rail curves, bridge structures and grades require design.

### Managing the busiest line at equal service effort

The sensitivity redistributes departures toward busy sections within the same daily train-km. Both networks start with uniform headways and may vary each line’s frequency between half and twice that starting value. The assignment recalculates journeys after each frequency change. The peak index scales the maximum share of all sampled trips on a directed segment by its headway relative to six minutes. It compares expected demand per departure under the same synthetic trip volume.

| Layout and frequency trial | M09 headway (min) | One-transfer-or-better share | Peak demand per departure index |
|---|---:|---:|---:|
| Previous short-link map, uniform | 6.00 | 28.10% | 2.952 |
| Previous short-link map, load-based | 3.33 | 28.30% | 1.867 |
| Grid with targeted relief link, uniform | 6.53 | 29.66% | 3.710 |
| Grid with targeted relief link, load-based | 3.37 | 29.17% | 2.088 |

## Cross-city additions

The generator compared 61 screened alignments. The selected layout adds 16 through routes totalling 218.6 route-km, before any inner orbital. Every through route has an interchange at both termini. Intermediate interchanges are included where the geometry and station screens allow them. The coverage gain in each row is measured after the routes above it are added.

| Line | Role | First interchange | Last interchange | Length | Interchanges | Additional residents within 1,200 m |
|---|---|---|---|---:|---:|---:|
| G02 | north–south | Karkh north–south · M-187 | M09 infill · km 5.4 | 20.28 km | 5 | 125,357 |
| G07 | east–west | C1 infill · km 3.9 | M06–M07 interchange | 13.69 km | 4 | 66,532 |
| G05 | east–west | M02 infill · km 51.9 | Near حي الادريسي · M-068 | 15.72 km | 6 | 54,911 |
| G04 | north–south | M05–M08 interchange | M14 infill · km 7.5 | 15.27 km | 7 | 36,301 |
| G11 | east–west | C1 infill · km 2.7 | M08 infill · km 24.6 | 15.45 km | 6 | 43,654 |
| G20 | north–south | M05 infill · km 0.9 | الحي العسكري | 20.19 km | 5 | 46,135 |
| G13 | east–west | M08 infill · km 47.1 | M04 infill · km 24.9 | 14.19 km | 5 | 34,375 |
| G08 | north–south | M13 infill · km 7.2 | M04 infill · km 0.9 | 26.01 km | 7 | 42,033 |
| T01 | Local gap link | C1 infill · km 31.2 | Sadr north–south · M-172 | 6.42 km | 4 | 148,958 |
| T05 | Local gap link | Northern cross-city · M-218 | M05 infill · km 23.7 | 10.24 km | 3 | 174,183 |
| T23 | Local gap link | Baghdad orbital · M-138 | M04 infill · km 39 | 12.93 km | 3 | 208,266 |
| T02 | Local gap link | M09 infill · km 7.8 | M11 infill · km 0.9 | 8.29 km | 4 | 79,726 |
| T40 | Local gap link | Sadr north–south · M-173 | M14 infill · km 5.7 | 7.90 km | 4 | 63,471 |
| T20 | Local gap link | C2 infill · km 1.2 | M06 infill · km 31.8 | 8.50 km | 3 | 51,748 |
| T19 | Local gap link | M02 infill · km 20.4 | M04 infill · km 28.5 | 12.79 km | 4 | 57,567 |
| T13 | Local gap link | M04 infill · km 39 | M11 infill · km 2.4 | 10.76 km | 3 | 44,049 |

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
| M02 | كلية المدائن الجامعة | ذات السلاسل | 52.88 | 55 |
| M03 | قرية الثوار ( قرية شيخ محمد كشكول ) | مركز صحي الشاعورة | 49.56 | 44 |
| M04 | الحي العسكري | Near Husain al Latif · M-073 | 41.96 | 43 |
| M05 | Al Amiriya | Near Nahrawan · M-089 | 43.50 | 42 |
| M06 | اليوسفية | صيد ديالى | 52.55 | 52 |
| M07 | مجمع الأنوار الطبي | Ishan Abu Khalifah | 39.96 | 37 |
| M08 | المدائن | مركز صحي | 48.17 | 45 |
| M09 | مستوصف الكريعات | Returns to first stop | 97.75 | 98 |
| M10 | Near Hay alBinouk · M-160 | Near حي النصر · M-168 | 12.12 | 14 |
| M11 | Sadr north–south · M-169 | Near سبع قصور · M-175 | 10.08 | 11 |
| M12 | Karkh north–south · M-187 | Karkh north–south · M-200 | 21.63 | 29 |
| M13 | Southwest cross-city · M-201 | Southwest cross-city · M-209 | 12.75 | 18 |
| M14 | Northern cross-city · M-210 | Northern cross-city · M-220 | 16.75 | 19 |
| C1 | Baghdad Airport terminal | Zayouna / Palestine Street | 34.34 | 38 |
| C2 | Al Mustansiriya / Turkmen Club Square | University of Baghdad approach | 15.13 | 19 |
| G02 | Karkh north–south · M-187 | M09 infill · km 5.4 | 20.28 | 19 |
| G07 | C1 infill · km 3.9 | M06–M07 interchange | 13.69 | 12 |
| G05 | M02 infill · km 51.9 | Near حي الادريسي · M-068 | 15.72 | 15 |
| G04 | M05–M08 interchange | M14 infill · km 7.5 | 15.27 | 15 |
| G11 | C1 infill · km 2.7 | M08 infill · km 24.6 | 15.45 | 13 |
| G20 | M05 infill · km 0.9 | الحي العسكري | 20.19 | 17 |
| G13 | M08 infill · km 47.1 | M04 infill · km 24.9 | 14.19 | 14 |
| G08 | M13 infill · km 7.2 | M04 infill · km 0.9 | 26.01 | 24 |
| T01 | C1 infill · km 31.2 | Sadr north–south · M-172 | 6.42 | 7 |
| T05 | Northern cross-city · M-218 | M05 infill · km 23.7 | 10.24 | 9 |
| T23 | Baghdad orbital · M-138 | M04 infill · km 39 | 12.93 | 12 |
| T02 | M09 infill · km 7.8 | M11 infill · km 0.9 | 8.29 | 9 |
| T40 | Sadr north–south · M-173 | M14 infill · km 5.7 | 7.90 | 9 |
| T20 | C2 infill · km 1.2 | M06 infill · km 31.8 | 8.50 | 8 |
| T19 | M02 infill · km 20.4 | M04 infill · km 28.5 | 12.79 | 11 |
| T13 | M04 infill · km 39 | M11 infill · km 2.4 | 10.76 | 9 |

The revised routes and stops need their own running times, depot and turnback design, protection, fleet and cost evaluation. The earlier budgets and timetables belong to their original studies.

Run `./osr design railway baghdad-network --check` to reproduce the published map and coverage. Use `--output build/baghdad-network-trial --max-through-routes 0` to compare revised station siting on the earlier routes.

Publication `72f51d3802771d41da10ec05b5297713c930409ea80d5d66e5a44acbd54ab218`.
