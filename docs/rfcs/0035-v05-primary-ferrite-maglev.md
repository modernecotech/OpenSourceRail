# RFC 0035 — v0.5 primary ferrite-maglev infrastructure

Status: selected development architecture; engineering acceptance remains open.
Decision date: 20 October 2026. Supersedes v0.4 wheel/rail physical defaults for new development.

The user selected a broadened ferrite permanent-magnet maglev system as the
primary OpenSourceRail infrastructure. The machine-readable decision is
[the infrastructure policy](../../lib/templates/infrastructure.toml). Its input
is [revision B of the maglev profile](../../ferrite-maglev-study.toml).
The supplied [revision-A specification](../../OpenSourceRail_Ferrite_Maglev_Rework_Specification.md)
and [cost workbook](../../OpenSourceRail_Ferrite_Maglev_Cost_Model.xlsx) remain the
reference handoff. Statements in specification A that describe the TOML as an
unimplemented scaffold describe its original handoff; the dedicated v0.5 adapter
now accepts revision B. The wheel/rail generators still do not accept it.

The primary design combines fixed onboard ferrite modules, PM-biased active
upward attraction, separate active guidance, onboard windings and electronics,
passive guidebeams, battery/station charging and switch-free mainline topology.
Shaped-pole vertical restoring suspension and linear induction propulsion remain
alternatives requiring their own model adapters. Three 17 m cars, matched
675 kWh gross storage and unchanged AW2/AW3 payloads are initial study values.
Baghdad's six-car comparator cannot be replaced one for one by this formation.

The system objective is locally owned design, fabrication, integration and
repair. Minimise imported finished running-gear packages; develop retained
magnet cartridges, carriers, winding/impregnation, module assembly/calibration,
guidebeams and replaceable passive reaction surfaces locally. Optimise complete
manufactured and erected function: foundations, supports, beam, magnetic
interfaces, evacuation, services, transport, tooling and construction stages.
Compare cost, installed mass, maximum lift, labour, throughput, alignment,
maintainability and external payment obligations together.

Rust implements the portable control algorithms and SBC host integration.
`osr-maglev-control` now includes an allocation-free `no_std` core, a 24-module
force allocator, virtual plant/replays, I/O contracts and a support-aware
traction-permission/fault policy. Fresh support control continues during a
commanded stop. Invalid sensing requests a separately engineered local fallback;
holding an old PWM value is not a fallback controller. Saturation inhibits
traction. Fault reset requires fresh healthy inputs and reported stopped/secured
conditions. Physical actuation remains disabled. Synthetic gains, ideal force
channels and logical protection do not establish the actual magnetic plant,
independent hardware channels or measured SBC deadlines.

The [two-way numerical demonstrator](../../engineering/ferrite_maglev/coupled.py)
connects the Rust 24-module controller to a 50-element, six-vertical-mode flexible
beam. Returned support forces load the beam; local beam displacement changes the
next controller gap readings. A three-second virtual replay and independent
static beam checks are implemented. The car is rigid and stationary; torsion,
lateral/soil/joint/moving-load dynamics, actual force/current/thermal maps and
physical timing remain open. This subset does not close full six-degree-of-
freedom stability, ride or failure acceptance.

Off-the-shelf SBCs are the preferred hosts. Host choice does not remove the
cost of power semiconductors, isolated sensing, current control, switching I/O,
protection energy, cooling and physical qualification. Real-time scheduling and
local control must be demonstrated on the selected board with production I/O.
[Linux PREEMPT_RT](https://docs.kernel.org/core-api/real-time/theory.html) reduces
scheduling latency; it does not supply a measured application deadline.
The [published coupled motor/levitation study](https://www.jstage.jst.go.jp/article/mej/4/5/4_17-00084/_article)
supports the research architecture, with no transfer of its results to this car.

Cost model changes retain the supplied low/base/high allowances, including the
exact conventional removal scope, replacement support/brakes and separate NRE.
Two additional $90k/$60k magnetic-bundle targets retain all other base costs.
They are optimisation hypotheses. Localisation is costed local value added,
with imported inputs retaining their origin. No percentage is asserted until
an origin-traced priced MBOM is available. No catenary-removal credit or citywide
saving is inherited. Civil component quantities and gross stiffness screens do
not establish strength, gap control, support savings or a finished shipment mass.

## Implemented development scope

The [transition register](../../engineering/ferrite_maglev/transition.py)
preserves 345 canonical identities plus 69 additional Baghdad records. Its 414
explicit dispositions cover 202 redesigns, 17 replacements, 151 shared items
requiring interface revalidation and 44 wheel-specific retirements. It maps all
63 legacy work packages and 72 ferrite requirements to the 11 primary packages.
Every allocation carries deliverables and open evidence actions; **inventory
coverage is not engineering completion or acceptance**. Wheel retirement keeps
replacement support, capture, braking, parking and recovery obligations visible.

The [geometry adapter](../../engineering/ferrite_maglev/geometry.py) now defines
a partial 624-solid 17 m frame/24-cartridge lift interface and a two-direction
25 m civil bay. The native adapter constructs actual FreeCAD solids and exports
FCStd/STEP with reopening and selected identity/interference checks. The exact
export receipt identifies the checked variant. The default recessed-retainer
geometry models an 8 mm nominal fastener-head gap; its earlier 576-solid flat
variant has 2 mm. Ferrite edge grinding, retention, fasteners, full error budget,
complete vehicle equipment, structural joints, reinforcement and foundations
remain engineering/manufacturing holds.

The [field backend](../../engineering/ferrite_maglev/field.py) solves a 2D
variable-reluctivity equation and verifies a manufactured sine solution with
second-order refinement controls. An artificial nonlinear iron law, air Maxwell
contours and gap/temperature/current coupon sensitivities are available. **Coupon
force is not mesh-converged**; the equation control does not establish magnetic
force accuracy. Actual material grades, 3D geometry/ends, speed-dependent losses,
demagnetisation and vehicle lift capacity require qualified models and rig data.

The [city compiler](../../engineering/ferrite_maglev/cities.py) has generated
[separate provisional packages for 266 cities and 1,565 lines](../../engineering/ferrite_maglev/city-index.md).
It retains geography/demand while recomputing passenger-matched formation,
duty/fleet/charging/depot quantities and partial cost scenarios. Ordinary city
and simulation launchers now invoke this compiler and an offline representative-
train SOC replay. Located loops/ring closure, actual route and charging limits,
platforms, berth conflicts, depot access/recovery and complete programme costs
remain open. Baghdad's old six-car fleet count and cost total do not transfer.

The register also supplies 22 planned EBOM objects, 436 industrial obligations,
ERP/lifecycle and observation-only FUXA contracts, traveller prerequisites and
supplier questions separating manufacturing origin from supply/distribution
location. Its G0–G5 protocols retain 27 unresolved acceptance thresholds; limits
must be approved before tests and physical evidence must be authenticated.
No supplied material origin, quote, local-content percentage or physical result
is asserted. **Accepted engineering/physical releases: zero.**

## Migration contract

| Surface | v0.5 behaviour | Remaining work |
|---|---|---|
| Version and policy | `VERSION` 0.5; Rust/frontend 0.5.0; primary family selected | Configuration-specific deployment acceptance |
| `./osr`, `./osr design`, `./osr build` | Primary status, source-bound study publication and Rust examples | Complete engineered CAD and material/force/loss-qualified solvers |
| `./osr design legacy …`, `./osr sim legacy …`, `./osr city legacy …`, `./osr build legacy` | Explicit wheel/rail comparator access | No acceptance transfer |
| Ordinary `./osr city …` and `./osr sim …` | Provisional maglev city compilation and representative-train energy/charging replay | Located topology, route/berth/charging/recovery acceptance and complete programme costs |
| Existing wheel/rail catalogue, CAD, videos, book and brochure | Retained v0.4 physical comparators; maglev city packages and partial native models have distinct identities | Complete maglev configuration and qualified manufacturing outputs |
| Platform GUI, ERP and supervision | Retained tools plus planned maglev item/lifecycle/tag contracts | Released priced MBOM, actual entity/serial records and commissioned observation bindings; no live control authority |
| Background design | Source-bound primary study refresh; native geometry, 2D field and two-way beam/control subsets available | Broader validated electromagnetic/structural models, target hardware and physical evidence |

## Progressive completion

1. Close geometry, support/module placement, magnet allocation, force directions,
   vertical curves, twist, tolerance budget and switched-free terminal topology.
2. Complete magnetic/coil/rail production geometry from the partial native model;
   converge coupon force and qualify actual material, 3D, loss, finite-end and
   joint/temperature models against independent and physical evidence.
3. Derive thermal/current/voltage envelopes, force redistribution, 6-DOF control,
   flexible-body/guideway dynamics and physically independent protection.
4. Extend provisional city compilation/replay to matched 80/90 km/h, actual
   hot/grade/curve/wind, full-SOC/no-regen, low-voltage, missing-charge and
   failed-channel duty. Validate fleets, platforms, berths, depots, charging
   and switch-free recovery against the accepted service and physical route.
5. Derive EBOM/MBOM, local/import origin, complete BoQ, processes, fixtures,
   yield, labour, QA, spare modules and lifecycle repair evidence.
6. Execute G0–G5 with predetermined acceptance limits and authenticated evidence.

The adapter executes available finite calculations and distinguishes implemented
subsets from missing engineering and acceptance evidence. Source or requirements changes trigger a new result. Repeating
unchanged arithmetic cannot manufacture missing field maps, measurements or
accepted designs. All physical/manufacturing release flags remain false.
