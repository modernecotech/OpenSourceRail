# Station and civil drawing-definition seeds

Generated with the station catalogue. Each seed is a bounded drafting brief
that connects product families, affordable defaults, unresolved site/supplier
inputs, tools, outputs and verification without inventing construction release.

- Drawing seeds: **18**
- Controlled product families represented: **45**
- Open products with reference defaults: **29**
- Issue state: **all definition seeds; none issued for fabrication or construction**

| Drawing | Scope | Owner | Package | Products | JSON |
|---|---|---|---|---:|---|
| [`STN-ACC-400`](STN-ACC-400.md) — at-grade pedestrian approach and protected route | `deployment-interface-definition` | deployment civil/accessibility engineer | `STN-FRP-050` | 1 | [`json`](STN-ACC-400.json) |
| [`STN-ACC-410`](STN-ACC-410.md) — lift, stair and pedestrian overbridge coordination | `deployment-led-supplier-interface` | structural/accessibility engineer + lift supplier | `STN-FRP-050` | 2 | [`json`](STN-ACC-410.json) |
| [`STN-CIV-100`](STN-CIV-100.md) — precast platform and guideway product definition | `reusable-fabrication-definition` | civil structures + precast fabricator | `STN-FRP-010` | 4 | [`json`](STN-CIV-100.json) |
| [`STN-CIV-110`](STN-CIV-110.md) — site set-out, levelling, drainage and closure coordination | `deployment-interface-definition` | deployment civil engineer | `STN-FRP-010` | 3 | [`json`](STN-CIV-110.json) |
| [`STN-CNP-200`](STN-CNP-200.md) — platform canopy steel, footing and roof assembly | `hybrid-fabrication-definition` | structural engineer + steel fabricator | `STN-FRP-020` | 3 | [`json`](STN-CNP-200.json) |
| [`STN-CNP-210`](STN-CNP-210.md) — platform canopy PV strings, bonding and drainage interfaces | `supplier-interface-definition` | electrical engineer + PV integrator | `STN-FRP-020` | 2 | [`json`](STN-CNP-210.json) |
| [`STN-CNP-220`](STN-CNP-220.md) — auxiliary canopy truss, roof bay and foundation interface | `deployment-led-fabrication-definition` | structural engineer + steel fabricator | `STN-FRP-030` | 3 | [`json`](STN-CNP-220.json) |
| [`STN-CNP-230`](STN-CNP-230.md) — auxiliary canopy PV, drainage, lightning and safe access | `deployment-interface-definition` | electrical/civil integration | `STN-FRP-030` | 3 | [`json`](STN-CNP-230.json) |
| [`STN-DEP-700`](STN-DEP-700.md) — depot site, formation, drainage and service-road layout | `deployment-definition` | deployment civil engineer | `STN-FRP-080` | 2 | [`json`](STN-DEP-700.json) |
| [`STN-DEP-710`](STN-DEP-710.md) — depot throat turnout, routes and track geometry | `deployment-interface-definition` | permanent-way + signalling integration | `STN-FRP-080` | 1 | [`json`](STN-DEP-710.json) |
| [`STN-DEP-720`](STN-DEP-720.md) — depot charging, PV, stationary storage and isolation | `deployment-led-supplier-interface` | depot energy integrator + fire engineer | `STN-FRP-090` | 2 | [`json`](STN-DEP-720.json) |
| [`STN-DEP-730`](STN-DEP-730.md) — depot workshop, vehicle lift and building-services integration | `deployment-led-supplier-interface` | depot equipment + building services integration | `STN-FRP-090` | 2 | [`json`](STN-DEP-730.json) |
| [`STN-PWR-500`](STN-PWR-500.md) — wayside charger cabinet and vehicle docking interface | `supplier-interface-definition` | traction power + vehicle integration | `STN-FRP-060` | 1 | [`json`](STN-PWR-500.json) |
| [`STN-PWR-510`](STN-PWR-510.md) — traction substation utility and DC distribution interface | `deployment-led-supplier-interface` | traction power + utility | `STN-FRP-060` | 1 | [`json`](STN-PWR-510.json) |
| [`STN-SYS-300`](STN-SYS-300.md) — station LV, UPS, fire and services cabinet integration | `supplier-interface-definition` | station MEP engineer | `STN-FRP-040` | 4 | [`json`](STN-SYS-300.json) |
| [`STN-SYS-310`](STN-SYS-310.md) — passenger systems, fare equipment and plinth coordination | `supplier-interface-definition` | passenger systems integrator | `STN-FRP-040` | 8 | [`json`](STN-SYS-310.json) |
| [`STN-TRK-600`](STN-TRK-600.md) — 1:9 turnout rail, crossing, bearer and track-end definition | `hybrid-fabrication-definition` | permanent-way engineer + turnout supplier | `STN-FRP-070` | 4 | [`json`](STN-TRK-600.json) |
| [`STN-TRK-610`](STN-TRK-610.md) — point operation, lock, detection, heating and harness | `supplier-interface-definition` | signalling/track integration | `STN-FRP-070` | 3 | [`json`](STN-TRK-610.json) |

Package issue and evidence state remains controlled by the
[`factory-release-readiness.md`](../factory-release-readiness.md) register.
