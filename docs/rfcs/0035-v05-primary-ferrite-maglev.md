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
`osr-maglev-control` is the first, allocation-free `no_std` core, with an offline
SBC replay example. It implements a single-module upward-attraction current
hypothesis and a separate traction-permission/support-response policy. Fresh
support control continues during a commanded stop. Invalid sensing requests a
separately engineered local fallback; holding an old PWM value is not a fallback
controller. Saturation inhibits traction. Fault reset requires fresh healthy
inputs and reported stopped/secured conditions. Every output has physical
actuation disabled. Its gains are synthetic, and this is not a six-degree-of-
freedom controller or a validated plant. Arrays, force allocation, physical
feedback, power stages, I/O, watchdog independence, timing and target acceptance
remain development work.

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

## Migration contract

| Surface | v0.5 behaviour | Remaining work |
|---|---|---|
| Version and policy | `VERSION` 0.5; Rust/frontend 0.5.0; primary family selected | Configuration-specific deployment acceptance |
| `./osr`, `./osr design`, `./osr build` | Primary status, study publication and Rust package | Broader native magnetic CAD and qualified solvers |
| `./osr design legacy …`, `./osr sim legacy …`, `./osr city legacy …`, `./osr build legacy` | Explicit wheel/rail comparator access | No acceptance transfer |
| Ordinary `./osr city …` and `./osr sim …` | Hold with migration explanation | Maglev route, formation, energy/fleet, terminals, depot, costs and recovery adapters |
| Existing catalogue, CAD, videos, book and brochure | Retained v0.4 physical comparators | Generate separate maglev assets from complete configuration; never relabel old geometry |
| Platform GUI, ERP and supervision | Retained owner/operator tools | Maglev asset/interface mapping and observation bindings; no live control authority |
| Background design | Source-bound primary study refresh; finite screens and open capabilities visible | Native electromagnetic, structural and multimodule control evaluators |

## Progressive completion

1. Close geometry, support/module placement, magnet allocation, force directions,
   vertical curves, twist, tolerance budget and switched-free terminal topology.
2. Build dimensioned magnetic/coil/rail CAD and independently benchmark nonlinear
   2D/3D force and loss solvers, retaining finite ends and joint/temperature cases.
3. Derive thermal/current/voltage envelopes, force redistribution, 6-DOF control,
   flexible-body/guideway dynamics and physically independent protection.
4. Run matched 80/90 km/h, hot/grade/wind, full-SOC/no-regen, low-voltage,
   missing-charge and failed-channel duty. Rebuild equal-capacity city fleets,
   platforms, depots, charging and switch-free recovery.
5. Derive EBOM/MBOM, local/import origin, complete BoQ, processes, fixtures,
   yield, labour, QA, spare modules and lifecycle repair evidence.
6. Execute G0–G5 with predetermined acceptance limits and authenticated evidence.

The adapter executes the available finite calculations and reports absent
capabilities. Source or requirements changes trigger a new result. Repeating
unchanged arithmetic cannot manufacture missing field maps, measurements or
accepted designs. All physical/manufacturing release flags remain false.
