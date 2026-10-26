# v0.6 station-powered freewheeling rail

OpenSourceRail aims for simple, affordable urban transport, repeated precast civil components and local manufacture and repair. Six lightweight comfort cars run on passive steel-wheel bogies and conventional rails. Station LIMs act on passive onboard aluminium secondaries; no onboard traction motor, traction battery or levitation magnet is fitted. Independent service power, braking and the existing station-led GoA4 architecture remain.

**Selected for reference engineering and prototype investigation. No physical, manufacturing or operating release.** The [selector](../../../engineering/development-baseline.toml) binds the same vehicle, body, support and propulsion identities through this packet, delivery records, Workbench and reader. [v0.5 maglev evidence](../../archives/v0.5-maglev/README.md) remains independently pinned.

| Item | Recalculated basis |
|---|---|
| Formation and comfort | Six 17 m cars; 104.5 m overall; 44 seats + two wheelchair places/car; zero planned standing |
| Running gear | 12 unpowered bogies, 24 axles, 48 wheels; independent friction/WSP/parking brake requirements |
| Body/platform | Retained lightweight aluminium/GFRP stock with revised bogie load paths; 1.0 m reference floor above rail |
| Accounted tare / normal load | 19.222 / 22.672 t/car at 75 kg/person |
| Located material / remaining reference accounts | 9.132 / 10.090 t/car |
| Complete installed mass, CG and inertia | Unknown; inherited service allocations may overlap new equipment and must be disaggregated |
| Service-only battery | 82.8 kWh, 1345 kg/car reference account; cooled installation and rail approval open |
| Service targets | 72 km/h, 0.4 m/s² acceleration, 0.6 m/s² braking, 35 s dwell, 120 s headway; 8,280 pphpd arithmetic |

## Reference journey and power

The 2 km, normal-load point-mass requirement takes **147.920 s**, reaching 20 m/s and arriving at **16.266 m/s** before braking. Required peak launch force is **10.395 kN/car**, mechanical power **207.9 kW/car**. Actual available thrust, current, voltage and full motor efficiency remain unknown.

Full-train engagement requires **817.0 m** of shared launch/receiving winding; the library chooses **900 m**, **72 sections/direction** at 12.5 m and at least two independently controlled train branches. The **84.97 s** nominal berth interval is a necessary resource screen, not verified two-minute operation.

Reference profiles cover empty, 46-person and 160-person structural-control loads at 1.5 and 2 km, with grade/wind, charge and independent wet/downhill stopping bounds. A 0.05 adhesion hypothesis on a 2% downgrade gives approximately 700 m stopping from 20 m/s including one second response. Supplier brakes, WSP, uncertainties and actual routes must establish the protection envelope. Receiving motor recovery receives no safety credit.

The 82.8 kWh service reference uses 75 industrial Type3-20 modules plus explicit enclosure/cooling/conversion accounts. The 200 kW charging target passes a catalogue voltage/current necessary bound; available charge power versus SOC/temperature remains unknown. A 50°C environment exceeds the module ambient catalogue range. Normal 35 kW/car hotel duty balances in the prototype calculation; 50 kW/car adverse duty needs more charging. Solar yield is not guaranteed or credited to make the balance pass.

The actual GetDP conductive-slab benchmark converges against its exact imposed-field solution. It has no real primary winding, steel/end geometry, current-to-force map or finite-height return currents. Its conditional thrust is not available station thrust. Active-plate-only and all-aluminium heat-capacity bounds expose the dependence on thermal connection; actual temperatures remain unknown.

[Prototype/fault test plan](prototype-test-plan.json) · [Full evaluation](evaluation.json.gz) · [Motor method evidence](native-drive.tar.gz) · [Speed requirement](service-profile.svg) · [Equal-service comparison](comparison.json)

## Vehicle and civil design

New bogie hardpoints, deep side sills and retained roof longitudinal members replace the magnetic carrier arrangement. The isolated side sills fail their declared stiffness screen; ideal whole-body chord coupling is an upper stiffness bound, with shear transfer, openings and joints unqualified. Native CAD is counted material geometry, not a complete installed or collision-free certified vehicle. Split battery cassettes, brakes, suspension, couplers, frame joints and maintenance paths still need detailed installation.

The roof proposal uses HP60 core and a counted white finish; long-term loaded hot strength, durable reflectance and HVAC performance remain open. Unchanged door, glass, floor and seat stock retains its source ancestry; the revised vehicle receives a new identity. Plastic glazing remains an unqualified alternative.

Three conventional guideway families are compared across 15/20/25/30 m spans. The crowd-sized 20 m box reference counts **22.282 m³ concrete**, **2.408 t running rail**, **70 fastener sets** and **6.448 t total preliminary steel including rail, fasteners, reinforcement, tendons and anchorages. Its **62.15 t** span account still excludes complete bearings, piers, foundations, access/containment and station equipment.

New rails and fasteners are much lighter than the old magnetic interface stock, while concrete and remaining structural quantities have different boundaries. Lower installed cost is unproven. Each longitudinal section gets its own moving-load envelope; torsion, fatigue, unequal rail loads, prestress losses, erection and sites remain open. Twin and U sections retain their failures.

[Native vehicle material package](native-vehicle.tar.gz) · [Vehicle drawing](vehicle-overview.svg) · [Reference section](interface-section.svg) · [Civil alternatives](exports/civil.json) · [Partial native IFC](exports/selected-interface.ifc) · [IFC scope](exports/bim.json) · [BOM](exports/engineering-bom.json.gz) · [Processes](exports/manufacturing.json) · [Procurement](exports/procurement.json.gz) · [Assembly](exports/assembly.json) · [Controls](exports/controls.json)

## Automation, comparison and cities

Station-led GoA4, onboard ATP, OCC, TCMS, door control, interlocking and communications remain. New actual Rust wheel-interface fixtures check configuration/readiness and independent brake demands; existing ATP regressions remain software evidence. They use assumed readiness and have no physical brake plant or hardware outputs. Loss of propulsion leaves wheel support intact. Off-zone restart requires protected rescue/towing; mainline switches remain excluded, with depot exceptions only.

v0.6 is chosen for prototype investigation to remove the unproven levitation system and repeated magnetic-facing assemblies. It is heavier than the v0.5 accounted car and lighter than the optimistic stripped-v0.4 mass proxy. No same-service supplier-priced whole-life superiority is established. See the explicit comparison and open price coverage.

All **266 city geographies and maps are preserved**; **zero city performance packages are regenerated**. A metadata scan of 17,268 adjacent operating-stop gaps finds a longest retained gap of approximately 3 km in Faisalabad. Reference adverse cases test that distance; uphill unreachable cases and downhill speed-cap violations are retained. Historical city fleet, windings and finance figures are not v0.6 results.

[Geographic catalogue and holds](cities.json) · [Workbench](../../workbench/current/index.html) · [Native controls](native-controls.tar.gz)

## Readiness and reproduction

| Gate | State | Evidence still needed |
|---|---|---|
| installed-vehicle | **unknown** | Locate and weigh all residual stock, joinery, bogie and service assemblies; obtain complete CG and inertia. |
| isolated-underframe-stiffness | **fail** | The isolated hollow side-sill fixtures exceed the declared deflection limit. Whole-body load sharing through retained longitudinal members, posts and joints must be demonstrated or redesigned. |
| body-and-bogie-structure | **unknown** | Concentrated bogie support changes the body load path. Local/frame fixtures do not establish joined-body stress, buckling, fatigue, crash, modes or bogie qualification. |
| wheel-rail-dynamics | **unknown** | Qualify wheel profiles, hunting, curves, suspension, ride, flange forces and derailment containment. |
| station-LIM-force-map | **unknown** | No accepted thrust/current/frequency/gap/temperature map for the complete station drive and moving secondary; targets are required forces. |
| station-electrical-thermal | **unknown** | Qualify inverters, section handoff, supply, slip/secondary heat, unwanted normal forces and 120-second repeated duty. |
| independent-braking | **unknown** | Validate supplier brake/WSP/adhesion/thermal curves, channel failures, parking, receiving-power loss and degraded gradients. |
| hot-weather-services | **unknown** | HVAC delivered capacity and COP at 50 C, roof long-term structural temperature and actively cooled service pack remain unqualified. |
| coupled-journey | **unknown** | Reference motion is analytical. Required physical drive/brake maps, wheel dynamics and flexible-body model are not available for a qualified six-car trip. |
| GoA4-protection | **unknown** | Existing Rust ATP/interlocking and new wheel interface predicates require candidate-correlated braking, sensing, timing, communications and fault evidence. |
| civil-and-site | **unknown** | Alternative sections are necessary screens. Prestress, fatigue, torsion, lateral/derailment loads, foundations, survey, erection and independent review remain open. |
| rescue-and-evacuation | **unknown** | Motorless off-zone restart needs a protected rescue/tow system, emergency access and an acceptable high-viaduct evacuation plan. |
| whole-system-economics | **unknown** | No same-service supplier quotes or complete CAPEX/OPEX/renewal comparison; lower installed cost has not been established. |
| city-regeneration | **hold** | Preserve 266 geographic inputs. Numerical city publication is held pending reference propulsion, braking, route and economic evidence. |

```bash
./osr status
./osr build
./osr verify
./osr test
./osr book --check
./osr sim baghdad  # explicit city evaluation hold
./osr legacy verify
```

[Source/payload receipt](manifest.json) · [README context](readme-coverage.md) · [Roadmap](../../ROADMAP.md) · [Project ethos](../../../README.md)

Selection id `8e5905bc7c81d6177bbaafde81ab3a5f8cc54947c4923eb4493949566ac85cdc`

Candidate id `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`

Body candidate id `9489e4f2666fd3b3c73232c86df3f12adf42a5531eb27373834cf3fecb1a3117`

Support component id `3e9aef846e6ec55bac013512163394618b37cf8c74b1100d6f8e5450ae5479d7`

Propulsion component id `67e2bfc4ef429a6c49e6d07095bc298c4eb76b8386e4ee316c440ff128c30fa9`
