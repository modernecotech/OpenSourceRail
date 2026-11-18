# OpenSourceRail v0.7 digital engineering release

**Scope:** one reproducible, costed digital railway design and its planning tools. The [selected candidate](reference-v07/digital/selected.toml) is a six-car powered-wheel train on two conventional rail tracks, carried by thirteen-strand 10 m precast beams with 1.5 kV DC overhead. The synthetic 30 km reference has twelve stations, **US$1,025.2272m** installed capital, **US$1,667.647m** 30-year present cost and a **43-month** construction programme. [Baghdad](../cities/Baghdad/PROPOSAL.md) and Samawah remain separate city studies.

The [v0.7.0 release](https://github.com/modernecotech/OpenSourceRail/releases/tag/v0.7.0) was published from commit `aba573e747c1`. It releases digital geometry, analysis, quantities, cost assumptions, production planning and an editable Workbench journey. Changes on `main` after that tag are subsequent corrections identified by their own commits. It does not issue fabrication drawings, record a physical prototype, approve a site foundation, post ERPNext production transactions or authorize passenger operation. Those are later project and qualification decisions.

## Release acceptance

| ID | Deliverable | Evidence | State |
|---|---|---|---|
| V07-01 | Version and current CI | `VERSION`, npm and Cargo metadata say 0.7.0; the release commit passed current fast checks | Passed at v0.7.0 tag |
| V07-02 | One selected digital candidate | [Selection](reference-v07/digital/selected.toml) carries parent, revised beam, evaluation and selection IDs; source hashes bind vehicle and civil results | Passed locally |
| V07-03 | Propulsion and braking basis | [Vehicle](reference-v07/vehicle/README.md) sizes continuous powered bogies at the 2% grade case; [independent brake](design-engine/v07-independent-brake/README.md) states force and energy requests | Passed as digital sizing |
| V07-04 | Representative car | [Digital car](reference-v07/digital/vehicle/README.md) reconciles CAD occurrences, mass bounds, CG, axle reactions and fixed interfaces | Passed as digital model |
| V07-05 | Civil span and station | [Native beam result](reference-v07/digital/civil/README.md) screens the joined CG load; [civil package](reference-v07/civil/README.md) gives section, quantities, station interface and erection sequence | Passed as digital model |
| V07-06 | Local production plan | [Handoff](reference-v07/digital/production/README.md) maps 52 BOM rows, 23 routes, make/buy, electronics and QA planning to the selected candidate | Passed as digital draft; electronics added after tag |
| V07-07 | One cost and delivery plan | [Fourteen scopes](reference-v07/cost/README.md), annual O&M, renewals, 30-year present cost and 43-month programme reconcile | Passed locally |
| V07-08 | Incremental change | `./osr reference v07 --stations 13` changes fleet, energy allowance, civil and production quantities, capital and whole-life cost with a new candidate ID | Passed locally |
| V07-09 | Workbench journey | Browser edit shows the same joined change and links car, beam, production and cost outputs; Samawah remains a separate case | Browser test passed locally |
| V07-10 | Publication | Clean sparse install, exact-tag checks, source archive, acceptance notes and GitHub release | Passed at v0.7.0 tag |

The previously published [v0.6.1 release](releases/v0.6.1/README.md) and historical source-bound packets remain intact. Research results are not silently transferred into the selected child. The parent nine-strand beam and its earlier price are retained as ancestry; the active thirteen-strand beam, mass and cost are in the selected v0.7 package.

## Reproduce the compact digital package

```sh
./osr reference v07
./osr reference v07 --stations 13
python3 -m engineering.vehicle_parts.joined_digital_car check --output docs/reference-v07/digital/vehicle/result.json
python3 -m engineering.design_search.v07_joined_civil_fem check --output docs/reference-v07/digital/civil
python3 docs/reference-v07/digital/production/generate.py --check
python3 -m unittest engineering.tests.test_v07_reference_journey
./osr book --check
```

The native civil check requires the recorded CalculiX backend. The rest of this compact path uses the repository's Python launcher and published data. Historical campaign replay and the 266-city rebuild are outside the routine v0.7 development path. Large native runs retain the 20 GiB free-disk reserve.

The digital design uses explicit route, load, material, foundation, equipment and unit-rate assumptions. An actual project must replace them with approved drawings, supplier ratings and prices, route and ground data, measured performance and independent engineering review before manufacturing or passenger service. The release does not set those unknowns to zero or claim those later approvals.
