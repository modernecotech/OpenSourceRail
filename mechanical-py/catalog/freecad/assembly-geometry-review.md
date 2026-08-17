# FreeCAD Assembly Geometry Review

Generated directly from parametric source geometry. The checks below use FreeCAD/OCC
`Shape.isValid()`, `Shape.check(True)`, solid counts, volume, and bounding-box
sanity checks on each assembled-state input.

## Chassis + Bogie Assembly

| Item | Source | Valid | OCC check | Solids | Volume mm^3 | Bounding box mm | Issue |
|---|---|---:|---:|---:|---:|---|---|
| Low-floor centre chassis | `low-floor-chassis` | True | True | 41 | 13641594000 | 15940 x 2790 x 755 |  |
| Bogie-to-chassis connector package | `bogie-to-chassis-connector` | True | True | 38 | 1472149073 | 13760 x 2440 x 370 |  |
| A-end motor bogie | `motor-bogie` | True | True | 385 | 2229700152 | 3604 x 2690 x 1100 |  |
| B-end trailer bogie | `trailer-bogie` | True | True | 339 | 1591914328 | 3604 x 2644 x 1074 |  |
| A-end bogie-to-motor connector | `bogie-to-motor-connector` | True | True | 22 | 43773013 | 3354 x 817 x 327 |  |

## Full Body Assembly

| Item | Source | Valid | OCC check | Solids | Volume mm^3 | Bounding box mm | Issue |
|---|---|---:|---:|---:|---:|---|---|
| Body primary structure | `car-body-structure` | True | True | 61 | 150759318286 | 16500 x 3110 x 3630 |  |
| Body exterior layer | `car-body-exterior` | True | True | 528 | 8412698884 | 16320 x 2970 x 4396 |  |
| Body interior layer | `car-body-interior` | True | True | 44 | 5842345400 | 15880 x 2770 x 2725 |  |
| Body service layers | `car-body-services` | True | True | 38 | 3585089000 | 14630 x 2800 x 4005 |  |
| Car systems package | `car-systems` | True | True | 365 | 6919568742 | 15595 x 3212 x 4325 |  |
| Mechanical interface package | `mechanical-interface-package` | True | True | 714 | 36883116335 | 18490 x 3076 x 3984 |  |
| Window cassettes and glazing installation | `window-installations` | True | True | 72 | 1562806176 | 15560 x 2954 x 1197 |  |
| Door leaf design package | `door-design` | True | True | 13 | 208207248 | 1382 x 168 x 2203 |  |
| Door portal and mount package | `door-mounts` | True | True | 44 | 229984266 | 7700 x 2875 x 2365 |  |
| Door installation package | `door-installations` | True | True | 28 | 2649559564 | 8020 x 3076 x 2520 |  |
| Door-to-body seal and interlock package | `door-to-body-installations` | True | True | 56 | 153756033 | 7660 x 2780 x 2584 |  |
| Low-floor centre cabin flooring | `cabin-flooring` | True | True | 30 | 1715407200 | 15080 x 2830 x 523 |  |
| Passenger bench and battery-strake mounts | `bench-on-battery-installations` | True | True | 48 | 2074585760 | 15180 x 2508 x 1435 |  |
| HVAC roof ducting and supply plenums | `hvac-roof-ducting-installation` | True | True | 38 | 3873196842 | 13780 x 2150 x 1144 |  |
| Interior lighting and emergency luminaires | `internal-lighting-installation` | True | True | 36 | 185174208 | 13331 x 2154 x 572 |  |
| Passenger information screens and speakers | `screen-speaker-mountings` | True | True | 39 | 220555641 | 13410 x 2542 x 506 |  |
| External lighting, lidar, radar, and cameras | `external-lighting-lidar-system` | True | True | 32 | 399423624 | 17512 x 1310 x 1518 |  |
| Battery installation and contactor interfaces | `battery-installations` | True | True | 58 | 617259840 | 13830 x 2856 x 476 |  |
| Side body frame and fixture attachments | `side-body-frame-attachments` | True | True | 52 | 1603635840 | 15720 x 2836 x 2620 |  |
| Composite body and roof fixture attachments | `composite-body-roof-attachments` | True | True | 33 | 3381460370 | 15350 x 3018 x 2441 |  |

## Geometry Issues

- No invalid source shapes or zero-size bounding boxes detected.
