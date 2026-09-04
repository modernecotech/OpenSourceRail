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
| Mechanical interface package | `mechanical-interface-package` | True | True | 1072 | 37298470307 | 18490 x 3076 x 3984 |  |
| Window cassettes and glazing installation | `window-installations` | True | True | 72 | 1562806176 | 15560 x 2954 x 1197 |  |
| Door leaf design package | `door-design` | True | True | 13 | 208207248 | 1382 x 168 x 2203 |  |
| Door portal and mount package | `door-mounts` | True | True | 44 | 229984266 | 7700 x 2875 x 2365 |  |
| Door installation package | `door-installations` | True | True | 28 | 2649559564 | 8020 x 3076 x 2520 |  |
| Door-to-body seal and interlock package | `door-to-body-installations` | True | True | 56 | 153756033 | 7660 x 2780 x 2584 |  |
| Low-floor centre cabin flooring | `cabin-flooring` | True | True | 30 | 1715407200 | 15080 x 2830 x 523 |  |
| Passenger bench and battery-strake mounts | `bench-on-battery-installations` | True | True | 48 | 2074585760 | 15180 x 2508 x 1435 |  |
| HVAC roof ducting and supply plenums | `hvac-roof-ducting-installation` | True | True | 38 | 3873196842 | 13780 x 2150 x 1144 |  |
| Interior lighting and emergency luminaires | `internal-lighting-installation` | True | True | 96 | 120455279 | 13182 x 2124 x 543 |  |
| Universal ceiling, waist, and fixture rails | `universal-service-rail-installation` | True | True | 112 | 84279200 | 13500 x 2590 x 2378 |  |
| Standard seat, handrail, and equipment adapters | `standard-fixture-adapters` | True | True | 52 | 73716075 | 11780 x 2568 x 1955 |  |
| Simplified door and window cassette hardware | `door-window-cassette-hardware` | True | True | 114 | 152148312 | 15558 x 2808 x 2110 |  |
| Passenger information screens and speakers | `screen-speaker-mountings` | True | True | 39 | 220555641 | 13410 x 2542 x 506 |  |
| External lighting, lidar, radar, and cameras | `external-lighting-lidar-system` | True | True | 32 | 399423624 | 17512 x 1310 x 1518 |  |
| Battery installation and contactor interfaces | `battery-installations` | True | True | 58 | 617259840 | 13830 x 2856 x 476 |  |
| Side body frame and fixture attachments | `side-body-frame-attachments` | True | True | 52 | 1603635840 | 15720 x 2836 x 2620 |  |
| Composite body and roof fixture attachments | `composite-body-roof-attachments` | True | True | 33 | 3381460370 | 15350 x 3018 x 2441 |  |

## LM3 Manufacturing Tooling

| Item | Source | Valid | OCC check | Solids | Volume mm^3 | Bounding box mm | Issue |
|---|---|---:|---:|---:|---:|---|---|
| LM3-TOOL-STEEL-FIXTURE — Locally fabricated steel body, bogie and interface structures | `manufacturing-tool:LM3-TOOL-STEEL-FIXTURE` | True | True | 22 | 13914104529 | 17000 x 3600 x 1350 |  |
| LM3-TOOL-DATUM-GAUGE — Locally fabricated steel body, bogie and interface structures | `manufacturing-tool:LM3-TOOL-DATUM-GAUGE` | True | True | 4 | 75812028 | 3400 x 2744 x 620 |  |
| LM3-TOOL-SIDE-MOULD — Reusable GFRP body, roof, end-cowl and interior panel mould families | `manufacturing-tool:LM3-TOOL-SIDE-MOULD` | True | True | 6 | 684647041 | 1300 x 3600 x 245 |  |
| LM3-TOOL-SIDE-VARIANT-NEST — Reusable GFRP body, roof, end-cowl and interior panel mould families | `manufacturing-tool:LM3-TOOL-SIDE-VARIANT-NEST` | True | True | 15 | 584009957 | 1350 x 3550 x 225 |  |
| LM3-TOOL-ROOF-MOULD — Reusable GFRP body, roof, end-cowl and interior panel mould families | `manufacturing-tool:LM3-TOOL-ROOF-MOULD` | True | True | 9 | 767202000 | 1300 x 3200 x 504 |  |
| LM3-TOOL-ROOF-FAIRING-MOULD — Reusable GFRP body, roof, end-cowl and interior panel mould families | `manufacturing-tool:LM3-TOOL-ROOF-FAIRING-MOULD` | True | True | 7 | 2612115000 | 3600 x 2900 x 780 |  |
| LM3-TOOL-COWL-MOULD — Reusable GFRP body, roof, end-cowl and interior panel mould families | `manufacturing-tool:LM3-TOOL-COWL-MOULD` | True | True | 8 | 4136400000 | 3300 x 3400 x 2410 |  |
| LM3-TOOL-TRIM-DRILL — Reusable GFRP body, roof, end-cowl and interior panel mould families | `manufacturing-tool:LM3-TOOL-TRIM-DRILL` | True | True | 15 | 852438541 | 1400 x 3800 x 270 |  |
| LM3-TOOL-INT-CEILING-MOULD — Reusable GFRP body, roof, end-cowl and interior panel mould families | `manufacturing-tool:LM3-TOOL-INT-CEILING-MOULD` | True | True | 7 | 641700000 | 1350 x 2950 x 550 |  |
| LM3-TOOL-INT-SIDE-MOULD — Reusable GFRP body, roof, end-cowl and interior panel mould families | `manufacturing-tool:LM3-TOOL-INT-SIDE-MOULD` | True | True | 3 | 594627500 | 1350 x 2450 x 275 |  |
| LM3-TOOL-INT-STRAKE-MOULD — Reusable GFRP body, roof, end-cowl and interior panel mould families | `manufacturing-tool:LM3-TOOL-INT-STRAKE-MOULD` | True | True | 3 | 2909400000 | 5200 x 1050 x 850 |  |
| LM3-TOOL-INT-DOOR-PRM-MOULD — Reusable GFRP body, roof, end-cowl and interior panel mould families | `manufacturing-tool:LM3-TOOL-INT-DOOR-PRM-MOULD` | True | True | 4 | 2014730000 | 2800 x 1600 x 1920 |  |
| LM3-TOOL-COATING-RACK — In-mould base finish, applied livery film, and qualified radiative roof-coating route | `manufacturing-tool:LM3-TOOL-COATING-RACK` | True | True | 7 | 899840000 | 4000 x 3160 x 2690 |  |
| LM3-TOOL-COATING-COUPON — In-mould base finish, applied livery film, and qualified radiative roof-coating route | `manufacturing-tool:LM3-TOOL-COATING-COUPON` | True | True | 3 | 540000 | 960 x 200 x 3 |  |
| LM3-TOOL-FILM-TEMPLATE — In-mould base finish, applied livery film, and qualified radiative roof-coating route | `manufacturing-tool:LM3-TOOL-FILM-TEMPLATE` | True | True | 18 | 828225189 | 8500 x 1800 x 150 |  |
| LM3-TOOL-RADIATIVE-COUPON — In-mould base finish, applied livery film, and qualified radiative roof-coating route | `manufacturing-tool:LM3-TOOL-RADIATIVE-COUPON` | True | True | 4 | 35040000 | 1100 x 520 x 67 |  |
| LM3-TOOL-WINDOW-GAUGE — Replaceable side-window cassette, pressure frame, seal and drain installation | `manufacturing-tool:LM3-TOOL-WINDOW-GAUGE` | True | True | 8 | 265830881 | 2150 x 240 x 1590 |  |
| LM3-TOOL-GLASS-CARRIER-NEST — Replaceable side-window cassette, pressure frame, seal and drain installation | `manufacturing-tool:LM3-TOOL-GLASS-CARRIER-NEST` | True | True | 14 | 379900828 | 2800 x 240 x 2120 |  |
| LM3-TOOL-WATER-TEST — Replaceable side-window cassette, pressure frame, seal and drain installation | `manufacturing-tool:LM3-TOOL-WATER-TEST` | True | True | 12 | 314015660 | 2400 x 640 x 1940 |  |
| LM3-TOOL-DOOR-GAUGE — Supplier door cassette on locally made four-point adjustable carrier | `manufacturing-tool:LM3-TOOL-DOOR-GAUGE` | True | True | 8 | 315030881 | 2000 x 240 x 2390 |  |
| LM3-TOOL-SEAL-GAUGE — Supplier door cassette on locally made four-point adjustable carrier | `manufacturing-tool:LM3-TOOL-SEAL-GAUGE` | True | True | 6 | 1152000 | 1480 x 80 x 1530 |  |
| LM3-TOOL-FLOOR-TEMPLATE — Removable floor panels, transport flooring and common passenger-fixture rail | `manufacturing-tool:LM3-TOOL-FLOOR-TEMPLATE` | True | True | 31 | 1465835734 | 15500 x 2700 x 112 |  |
| LM3-TOOL-FIXTURE-PROOF — Removable floor panels, transport flooring and common passenger-fixture rail | `manufacturing-tool:LM3-TOOL-FIXTURE-PROOF` | True | True | 3 | 178685574 | 1200 x 900 x 2360 |  |
| LM3-TOOL-BOGIE-STAND — Supplier traction motor/gearbox integration into locally fabricated powered bogie | `manufacturing-tool:LM3-TOOL-BOGIE-STAND` | True | True | 6 | 847392000 | 4200 x 2620 x 740 |  |
| LM3-TOOL-MOTOR-ALIGN — Supplier traction motor/gearbox integration into locally fabricated powered bogie | `manufacturing-tool:LM3-TOOL-MOTOR-ALIGN` | True | True | 4 | 794542273 | 2200 x 1300 x 1220 |  |
| LM3-TOOL-SERVICE-RAIL — Lighting, HVAC, HV/LV services and keyed replaceable modules | `manufacturing-tool:LM3-TOOL-SERVICE-RAIL` | True | True | 16 | 192471239 | 4000 x 600 x 180 |  |
| LM3-TOOL-HARNESS-BOARD — Lighting, HVAC, HV/LV services and keyed replaceable modules | `manufacturing-tool:LM3-TOOL-HARNESS-BOARD` | True | True | 46 | 1155619115 | 8000 x 2400 x 160 |  |
| LM3-TOOL-LAMP-AIM — Lighting, HVAC, HV/LV services and keyed replaceable modules | `manufacturing-tool:LM3-TOOL-LAMP-AIM` | True | True | 5 | 497259710 | 2200 x 1100 x 1680 |  |
| LM3-TOOL-LIFT-COLUMNS — Three-car final assembly, static test and manufacturing release | `manufacturing-tool:LM3-TOOL-LIFT-COLUMNS` | True | True | 16 | 11160960000 | 14900 x 4900 x 4800 |  |
| LM3-TOOL-FINAL-DATUM — Three-car final assembly, static test and manufacturing release | `manufacturing-tool:LM3-TOOL-FINAL-DATUM` | True | True | 18 | 485191168 | 50000 x 120 x 380 |  |

## Geometry Issues

- No invalid source shapes or zero-size bounding boxes detected.
