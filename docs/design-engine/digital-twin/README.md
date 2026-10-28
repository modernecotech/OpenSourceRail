# End-to-end sparse-wayside research twin

The generator materializes the passive six-car vehicle, its **five short 20 m
wayside accelerators**, one directional 1.5/2 km interstation cell and counted
concrete/rail stock under one physical candidate identity. It generates the
geometry, disjoint located/unlocated inventory, mass properties, EBOM/MBOM,
assembly/procurement drafts, propulsion requirements, load/fault calculations,
civil quantities, construction prerequisites, controls interfaces, cost coverage
and required physical tests from the same candidate.

**A completed and consistent digital package is not a completed physical design.**
The motor force map, complete installed equipment, body/joint qualification,
braking, surveyed civil/site design and whole-life prices remain open. The
validator fails `--require-complete` and returns explicit blocker/task identities.
No train is automatically selected, manufactured, purchased or authorised to move.

The wider [OpenSourceRail project](../../../README.md) retains its planning,
local manufacturing/repair, delivery, ERPNext/Frappe HR, supervision and GoA4 remit.
This new research configuration leaves the selected reference and historical
source-bound experiments unchanged.

## Generate and validate

```bash
./osr design railway plan
./osr-twin plan
./osr-twin generate --family gfrp_semimonocoque --distance 2000 --output build/my-twin
./osr-twin verify build/my-twin
./osr-twin verify build/my-twin --require-complete
./osr-twin run --max-cases 2
./osr-twin run
./osr-twin publish
```

The strict command returns exit code 3 while engineering obligations remain open.
Other verification errors reject inconsistent, stale or modified packages.
The six-case campaign uses three structural families at 1.5/2 km; interrupted or
budget-limited invocations retain the pending matrix. Each source/input revision
gets a different evaluation request. Unrelated prior packages are not overwritten.

`generate --native` additionally writes a genuine IFC federation and actual
FreeCAD/STEP stock assembly, then independently reopens them. `run --native-jobs 1`
reserves one such job for the 2 km GFRP experiment. Missing native tools or failed
jobs retain their input/logs rather than producing substitute CAD files.
Native geometry includes only explicitly located stock. It does not fabricate
unlocated HVAC, services, join hardware, foundations or station details.

## What the validator checks

- Regenerates each semantic artifact from the source-bound physical inputs;
  resealing an altered BOM, scene, cost or nested acceptance flag does not pass.
- Reconciles every train stock occurrence and retained residual account with the
  exact mass used by the load, brake and civil calculations. Complete installed
  mass, CG and inertia stay unknown. Nominal gross stock is not a certified lower
  bound because joint cuts and overlaps remain unresolved.
- Checks actual primitive dimensions, materials, transforms, volumes and mass;
  reopens IFC/CAD/STEP and rejects equal-volume shape/placement substitutions.
- Keeps installed bank identity and stock after a bank is disabled. It does not
  multiply local thrust by the number of cars or banks or infer force from overlap.
- Binds 40-period/20 m motor stock and proposed branch registration to the new
  candidate. The older 12.5 m moving evaluator is explicitly incompatible.
- Separates demanded motion from an available-force journey. No force map enters
  this pipeline through self-asserted supported strings or hash-shaped reviews.
  Externally authenticated, source/candidate/interface-bound evidence is required
  before an operating-map import adapter can be enabled.
- Preserves independent brakes, service/essential power, ATP, accessible boarding,
  egress and protected external recovery. Unknown costs, quantities and thermal
  duty never become zero or a claimed economic winner.

## Scope of the generated railway

The physical coordinate origin is the departure train nose; the train occupies
approximately −104.5..0 m. Counted guideway extends from −120 m through the next berth
at 1500/2000 m, explicitly including its departure-berth support. The 1.5/2 km distance
is berth-to-berth travel, not the total precast quantity. It is one directional
cell, not a complete return line, city, depot, fleet or surveyed station plan.

Five double-sided banks contain 100 m of bank length and **200 m of primary-face
length**. Steel solids and equivalent-volume copper stock are counted; finished
coil ends, converters, feeders, cooling, mounts and cable protection remain
unresolved. Rail rectangles preserve reference 60E1 mass, not its true cross-
section or wheel/fastener clearance. The analytical box section includes end
diaphragms; prestress, reinforcement and fastening accounts remain unlocated.

Independent friction receiving is an explicit research hypothesis. No receiving
LIM thrust, regeneration or onboard recovery motor is credited. Required motion,
conditional brake responses and adverse-grade failures are model results only.

Sources: [campaign](../../../campaigns/end-to-end-digital-twin.toml),
[generator and validators](../../../engineering/railway_twin/),
[active accelerator study](../station-accelerators/README.md),
[current selected dossier](../current/README.md).
