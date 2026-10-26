# Current comfort-first development design

OpenSourceRail develops simple, affordable, locally maintainable urban transport. All permanent magnets and fast suspension controls stay on the train. Ordinary guideway is a concrete beam with passive steel facings; station winding groups launch and receive trains. Repeated lightweight vehicles and civil components aim to reduce total cost while providing frequent comfortable service.

**This is the repository development default, not a physical or operating release.** The selector is [engineering/development-baseline.toml](../../../engineering/development-baseline.toml). Every current city, control setting and delivery export carries the same selection, vehicle, body and magnet identities. Historical packets retain their original scope and source revision.

| Item | Selected basis |
|---|---|
| Formation | Six 17 m cars, 104.5 m train including gaps |
| Comfort and payload | 44 fixed seats + two wheelchair places/car, zero planned standing; 276/train |
| Layout | Four abreast where structural posts permit, wall seating at the doors; two passenger doors on one side |
| Structure | Aluminium extrusion frame, retained GFRP sides, aluminium-skin sandwich floor and revised roof |
| Windows | Retained laminated glass; plastic alternatives are not qualified |
| PM assembly | Selected onboard NdFeB Halbach component; active multiaxis stabilization remains open |
| Accounted tare / capped loaded mass | 17.357 / 20.807 t/car |
| Complete installed mass / CG / inertia | Unknown; retained allocations and supplier references are not located material |
| Service target | 120 s, 30 trains/hour, 8,280 normal passengers/hour/direction |
| Retained-stop proposal | 72 km/h launch cap, 35 s dwell; actual coast/brake legs and bounded station library |

The lower passenger count is a comfort and normal-load choice. The former 14,400 pphpd comparison is not achieved by this seating capacity. Enforceable admission, crowd loading, accessible boarding, one-sided platform compatibility and evacuation remain design requirements.

## Recalculated service and cities

All **266 city packages** use this default and retain their existing route geography and stops. Baghdad requires **906 trainsets (791 active, 101 spare, 14 cold reserve), 5,436 cars and 390,500 m of directional station winding** under the declared flat-route and drag hypotheses. No additional passenger stops are imposed. Its four motor-interval overlaps and 36.743% mainline powered coverage require physical resource/handoff design; they are not qualified infrastructure.

The 2 km prototype has an analytical runtime of **151.930 s**, with 20 m/s launch and approximately 14.266 m/s arrival before braking. A station shares **800 m** of winding across launch and receipt, divided into 64 addresses/direction at 12.5 m, with at least two simultaneous train phase/current branches per direction. The nominal resource interval is **79.504 s**, not a safe headway determination. The earlier 54 km/h, 450 m prototype is a named comparison.

Mass, propulsion energy requirements, service cycles, fleet and station quantities are recalculated; unavailable actual thrust, control, HVAC power, unit prices, site quantities, crew duty and finance totals remain unknown. Historical fleet and CAPEX/OPEX figures do not apply automatically.

[All-city index](cities.json) · [Baghdad current package](../../../cities/catalogue/west-asia/Iraq/Baghdad/engineering/current/README.md) · [Coasting profile](service-profile.svg) · [Workbench](../../workbench/current/index.html)

## Native evidence and consistent delivery records

The selected-profile native package contains **6 actual Rust control executions**. They test nominal, journal and fault protection protocols using virtual healthy gaps and assumed braking. They do not establish a physical operating gap, stable hover or a physical two-minute headway. The exact unchanged native car material geometry is independently reverified; complete installed geometry and structure remain open.

[Native controls archive](native-controls.tar.gz) · [Engineering BOM](exports/engineering-bom.json.gz) · [Manufacturing](exports/manufacturing.json) · [Procurement](exports/procurement.json.gz) · [Assembly/construction](exports/assembly.json) · [Civil interface](exports/civil.json) · [Controls](exports/controls.json) · [CAD reference receipt](exports/cad.json) · [Selected civil IFC](exports/selected-interface.ifc). The IFC contains the declared civil shell, facings and equipment contexts; it is not a complete vehicle or civil model.

[Native car](../ferrite-maglev/comfort-design/vehicle.FCStd) · [STEP](../ferrite-maglev/comfort-design/vehicle.step.gz) · [Material overview](vehicle-overview.svg) · [Guideway section](interface-section.svg) · [Complete current evaluation](evaluation.json.gz)

## Physical gates

| Gate | Screen | Remaining evidence |
|---|---|---|
| mass | **unknown** | Equipped mass, CG and inertia retain unlocated allocations/references and unresolved installation stock. |
| suspension | **unknown** | Zero-current component samples have unresolved contour disagreement; no installed3D multiaxis current map, equilibrium or damping proof. |
| control | **unknown** | Actual current authority, supply bandwidth, gap/tolerance envelope and essential-power fault response are unqualified. |
| HVAC-electrical | **unknown** | Actual50C capacity/COP/fresh air, compressor phases and complete bus/charging duty remain unqualified. |
| roof-hot-core | **fail** | The retained0.5solar-absorptivity/900Wm2/50C unshaded hypothesis exceeds the H60 continuous70C limit; measured finish/shading or material revision is required. |
| body-clearance | **unknown** | Revised roof on retained ribs,61mm doors, floor inserts, seat restraints and magnetic attachments need native swept fit and joined-body analysis. |
| civil | **unknown** | New2.26m steel-facing envelope and spreaders need anchors, concrete/rebar, prestress, moving loads, magnetic shadow and site evidence. |
| capture-energy | **fail** | The retained eight-shoe undamped linear source model exceeds the source force/compression bounds in the required drop cases; alternatives need counted geometry and measured force/stroke. |
| onboard-braking | **unknown** | Retained clamp stock has declared force/friction/thermal sensitivities, but actual wet/hot friction, independent deployment and guideway load paths are unqualified. |
| recovery | **unknown** | A stopped off-zone train needs located powered or winch recovery and essential energy. Contact-supported towing can exceed the retained rope bound; time shift is not restart thrust. |
| operations | **unknown** | A nominal120s resource screen cannot establish support, guaranteed braking, receiving-power-loss protection or actual dwell distribution. |
| economics | **unknown** | Trainset unit price, priced BOM coverage, labour, tooling, station power, fleet and whole-life costs are incomplete. |

The 12 mm section pose is a magnetic coupon reference, not an accepted operating gap. The lighter car has excess upward force at that sample; equilibrium, current authority, lateral/rotational response, damping, temperature and boarding datum must be resolved together. EPM load trimming and new Halbach families remain research alternatives rather than replacements for fast control.

The counted civil interface is conservative and heavy: approximately 865 t steel/directional km before remaining reinforcement, prestress, bearings, piers and foundations. It is an optimization input, not a low-cost viaduct claim. Unknown stock and prices never become zero.

## Reproduce and verify

```bash
./osr build
./osr verify
./osr test
./osr book --check
./osr legacy verify
```

[Summary](summary.json) · [Source/payload receipt](manifest.json) · [README coverage](readme-coverage.md) · [Roadmap](../../ROADMAP.md) · [Historical archive](../../archives/pre-comfort-default/README.md) · [Project ethos](../../../README.md)

Selection `c76af04990ab43d9644b884eb1a7d103851aa53fcc963505bdb0b7580ae74e77`

Vehicle `957f7e4e2e0e98b575810fb0c568554968fc1eb0715fb673827a16bcf63d400b`

Body `1eca1897b983bf62ec315cdc39aca2e2387f93ad6ab0c195bc278e14c8fb120b`

Magnet `397ddf033ab98afaea053acaa3047249a3329f542f1f5e52a6eb1b466b9662e0`
