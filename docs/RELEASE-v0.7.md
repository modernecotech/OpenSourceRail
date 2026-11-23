# OpenSourceRail v0.7 digital engineering release

**Scope:** one reproducible, costed digital railway design and its planning tools. The [selected candidate](reference-v07/digital/selected.toml) is a six-car powered-wheel train on two conventional rail tracks, carried by thirteen-strand 10 m precast beams with 1.5 kV DC overhead. The synthetic 30 km reference has twelve stations, **US$1,025.2272m** installed capital, **US$1,667.647m** 30-year present cost and a **43-month** construction programme. [Baghdad](../cities/Baghdad/PROPOSAL.md) and Samawah remain separate city studies.

The [v0.7.0 release](https://github.com/modernecotech/OpenSourceRail/releases/tag/v0.7.0) was published from commit `aba573e747c1`. **v0.7.1** carries the subsequent Baghdad city-background maps, two independent network alternatives, elevated offwire cost comparison, installed control-electronics schedule, powered-wheel control adapters and documentation cleanup. The selected 30 km digital reference remains a separate candidate. The release provides digital geometry, analysis, quantities, cost assumptions, production planning and an editable Workbench journey. It does not issue fabrication drawings, record a physical prototype, approve a site foundation, post ERPNext production transactions or authorize passenger operation. Those are later project and qualification decisions.

## v0.7.2 Baghdad opening integration

The [v0.7.2 release notes](releases/v0.7.2/README.md) describe the connected six-stop Airport service, site-outage voltage calculations, engineering quantities and supplier dossier. Run `./osr design railway airport --check` in the source installation. Use `./osr design railway airport --packet build/airport-supplier.zip` for the planning and quotation package. The original [21-set Airport budget](../cities/Baghdad/AIRPORT-OPENING.md) remains a comparison with its own service and power assumptions.

The local installation verifier exports one Git revision, checks the Airport and the synthetic reference calculations in a clean Python environment, and records checksums for the archive and supplier packet. Tagged publication and hosted checks belong to the exact delivered commit. Bench measurements, supplier ratings and operating acceptance remain with the engineering and railway authorities.

## v0.7.1 release acceptance

| ID | Deliverable | Evidence | State |
|---|---|---|---|
| V07-01 | Version and current CI | `VERSION`, npm and Cargo metadata at the v0.7.1 tag say 0.7.1; the tagged v0.7.1 commit passed its fast checks | Passed for v0.7.1 |
| V07-02 | One selected digital candidate | [Selection](reference-v07/digital/selected.toml) carries parent, revised beam, evaluation and selection IDs; source hashes bind vehicle and civil results | Passed locally |
| V07-03 | Propulsion and braking basis | [Vehicle](reference-v07/vehicle/README.md) sizes continuous powered bogies at the 2% grade case; [independent brake](design-engine/v07-independent-brake/README.md) states force and energy requests | Passed as digital sizing |
| V07-04 | Representative car | [Digital car](reference-v07/digital/vehicle/README.md) reconciles CAD occurrences, mass bounds, CG, axle reactions and fixed interfaces | Passed as digital model |
| V07-05 | Civil span and station | [Native beam result](reference-v07/digital/civil/README.md) screens the joined CG load; [civil package](reference-v07/civil/README.md) gives section, quantities, station interface and erection sequence | Passed as digital model |
| V07-06 | Local production plan | [Handoff](reference-v07/digital/production/README.md) maps 52 BOM rows, 23 routes, make/buy, electronics and QA planning to the selected candidate | Digital draft and electronics allowances published in v0.7.1. Detailed wiring and power interfaces are on main. |
| V07-07 | One cost and delivery plan | [Fourteen scopes](reference-v07/cost/README.md), annual O&M, renewals, 30-year present cost and 43-month programme reconcile | Passed locally |
| V07-08 | Incremental change | `./osr reference v07 --stations 13` changes fleet, energy allowance, civil and production quantities, capital and whole-life cost with a new candidate ID | Passed locally |
| V07-09 | Workbench journey | Browser edit shows the same joined change and links car, beam, production and cost outputs; Samawah remains a separate case | Browser test passed locally |
| V07-10 | Publication | Clean sparse install, exact-tag checks, source archive, acceptance notes and GitHub release | Published as v0.7.1 |

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
