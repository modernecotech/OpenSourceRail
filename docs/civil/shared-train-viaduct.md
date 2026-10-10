# Shared trainset and viaduct engineering model

[Retained numerical review](../../engineering/civil_exploration/examples/shared-train-viaduct-review.json)
· [comparison figure](../../engineering/civil_exploration/examples/shared-train-viaduct-comparison.png)
· [spatial numerical review](../../engineering/civil_exploration/examples/shared-spatial-engineering-review.json)
· [spatial comparison figure](../../engineering/civil_exploration/examples/shared-spatial-engineering-comparison.png)
· [OpenSourceRail standard OSR-ENG-001](../standards/OSR-ENG-001.md)
· [native car-pair assembly](../../design/component-catalogue/models/cad/shared-car-pair.FCStd)
· [native joint/drawing receipt](../../design/component-catalogue/models/cad/shared-car-pair.native.json).

The [automated reference-parts compiler](automated-reference-parts.md) now adds a
separate complete-family variant with 192 reference instances, 191 joints and all
24 six-car wheelsets. Its parameterised battery architecture, coverage register,
typed interfaces and manufacturing/QA outputs extend this foundation. The retained
two-car demonstrations below continue to describe their original configurations.

The first demonstrator connects a representative articulated car pair to a
three-span viaduct, flexible rail, finite bearings, axial piers and foundation
springs. Component mass, CG and full inertia tensors feed carbody/bogie heave and
pitch, individual wheelsets, suspension and articulation. Wheel forces deform
the rail and bridge; their displacement changes the vehicle contact forces.
The same instance definition supplies native FreeCAD Assembly joints, an
unissued TechDraw view, cost quantities and the verification dependency register.

This is a **synthetic numerical verification model**. Its mass allocations,
inertias, stiffnesses and track properties are declared research inputs. It is
not a supplier train, a production drawing package or Baghdad qualification.
The two represented cars use the six-car operational family's planning module
dimensions; they do not represent all 24 axles of the complete Baghdad train.

## One family definition

[`lib/templates/rolling-stock.toml`](../../lib/templates/rolling-stock.toml)
owns family counts and overall lengths. Both catalogue CAD and the FreeCAD
review generator consume the
[`family definition`](../../design/component-catalogue/src/osr_mech/family_definition.py).
Their planning car modules are 21 m, 19.5 m, 16.5 m, 18.75 m and 18.5 m for the
one-, two-, three-, four- and six-car families. The six-car length is **111 m**,
with 12 bogies and 24 axle positions. The detailed bogie and family placement
share their 2.1 m wheelbase datum.

Equal car modules, two bogies per car and the reference inset are planning
assumptions. Supplier-defined lengths, articulation arrangements and installation
geometry remain required before these datums can become railway load evidence.

## Instance and evidence contract

The [published schema](../../design/component-catalogue/schemas/shared-engineering-model.json)
and [instance implementation](../../design/component-catalogue/src/osr_mech/engineering_definition.py)
extend the existing product and assembly IDs. The normal buildable-trainset
generator emits `engineering-instance-definition.json` alongside the existing
manifest. The unfilled slots retain quantities and parent assemblies; kits and
area allocations still need splitting into production parts. Their mass fields
remain null until data is supplied.

The retained [instance allocation](../../design/component-catalogue/catalog/buildable-trainset/engineering-instance-definition.json)
contains 737 open slots for existing active product rows, including explicit
non-counted kit/area allocations. It adds no invented closed mass records.

Each instance identifies its part/revision, parent, serial or material batch,
geometry classification, material regions, thickness/process slots, named
datums, rigid transform, attachment and physical mass scope. Design, supplier and
measured properties occupy separate slots with an explicit selected source.
Supplier declarations and measurements require retained files and SHA-256
bindings. Released/supplier installation solids require a retained geometry
source; the initial native adapter reads BREP solids. A supplier envelope's
enclosing volume never creates a material mass estimate.

The model embeds the family definition used for that configuration. A new
as-designed model must match the current authoritative profile. As-built and
as-maintained records retain their frozen family geometry when the master profile
changes. Their own serial/batch and revision identities still apply; changing the
master profile does not rewrite an already manufactured vehicle.

The [mass calculation](../../design/component-catalogue/src/osr_mech/vehicle_mass_properties.py)
rotates component tensors and applies the parallel-axis theorem about the
combined CG. It calculates asymmetric static wheel reactions while conserving
weight and longitudinal/lateral moments. Independent mass and position bounds
produce conservative wheel-load, CG and inertia intervals. Position uncertainty
encloses the combined CG/datum location error; transforms are otherwise exact.
Inertia uncertainty is an absolute spectral bound. Correlation losses are stated.
Missing quantities or tensors remain open and cannot start the coupled solver.

Joint instances reference actual instance datums and retain revision, permitted
motion, mechanical properties, friction/stops, definition fields and inspection
IDs. Native fixed, slider and revolute joints establish placement/motion. Their
mechanical stiffness is a separate record, not a consequence of CAD solving.
Detailed bolt stacks, weld procedures, laminate/bond data, fits, preload and
nonlinear suspension curves still require actual design or supplier evidence.

## Run and verify

From the repository root, using the engineering environment:

```sh
PYTHONPATH=design/component-catalogue/src tools/automation/osr-python \
  tools/automation/shared-train-viaduct.py \
  --output build/engineering/shared-train-viaduct \
  --speeds 15,20,25 --dt .0025 --mesh 8

PYTHONPATH=design/component-catalogue/src tools/automation/osr-python \
  tools/automation/shared-train-viaduct.py \
  --verify build/engineering/shared-train-viaduct
```

The component catalogue's `analysis` optional dependencies provide NumPy,
SciPy, JSON Schema checks and OpenSeesPy. Use a new output directory for each
campaign. The supplied example changes one battery mass by 10%, secondary
stiffness by −20%, articulation stiffness by a factor of two, and deck modulus
by −10%. `--model` accepts a filled definition; it requires `--baseline-only`
because the named variants are specific to the synthetic example.

Outputs retain every axle contact-force history, axle unloading, body acceleration,
joint force/displacement, rail displacement, deck acceleration, bearing and
foundation reaction. Independent temporal and spatial refinements use a declared
5% numerical screening tolerance. That tolerance is an implementation check,
not a railway acceptance limit. Native OpenSees independently replays the deck
and finite-support equations. Force, moment and instantaneous work mapping are
checked separately. Source, numerical library and output hashes bind the receipt.
Contact tension or exceeding a joint stop fails the linear adapter's domain.

The first adapter resolves straight-track vertical heave/pitch and linear
compressive contact. Its rail mesh resolves the rail-on-pad bending length
independently of the deck mesh, and elastic approach track removes moving-support
force jumps. The spatial adapter described below adds lateral/roll/yaw motion,
curves/cant, separate wheel contacts and both tracks. The retained vertical
comparison remains a distinct benchmark with its own scope and refinements.
Project acceptance limits remain external required inputs.

Generate the native assembly through the installed FreeCADCmd/Flatpak runtime:

```sh
tools/automation/shared-engineering-freecad.sh \
  --model build/engineering/shared-train-viaduct/baseline/definition.json \
  --output build/engineering/shared-car-pair.FCStd
```

The retained native receipt checks solver return,
named-datum position/orientation residuals and geometry source hashes. Drawing
generation leaves `DrawingIssued=false`. Inspection evidence must be performed
and reviewed separately.

Export the compact review and standalone figure after a verified campaign:

```sh
PYTHONPATH=design/component-catalogue/src tools/automation/osr-python \
  tools/automation/export-shared-engineering-review.py \
  build/engineering/shared-train-viaduct \
  --native design/component-catalogue/models/cad/shared-car-pair.native.json \
  --output engineering/civil_exploration/examples/shared-train-viaduct-review.json \
  --plot engineering/civil_exploration/examples/shared-train-viaduct-comparison.png
```

The figure exporter additionally requires Matplotlib. It verifies retained
source/output hashes and native datum/geometry bindings before publishing.

## Changes and manufacturing identity

The verification register binds instance/joint inputs to mass properties,
vehicle assembly, coupled vehicle response, bridge demand, cost, drawings and
inspection characteristics. A deck change invalidates vehicle response through
feedback. Unaffected instance drawings retain their dependency fingerprints.
Old results are preserved; a new fingerprint never reaccepts an old inspection.

The [ERP characteristic adapter](../../deployment/erpnext/apps/osr_erpnext/osr_erpnext/engineering_identity.py)
and [engineering proposal compiler](../../services/integration/osr_integration/engineering.py)
bind the exact instance-definition artifact, design/part revision, asset,
serial/batch, joint IDs and inspection units. Native work-order, quality
inspection, material batch, calibration and nonconformance references accompany
a measured result. The existing execution preview validates and preserves that
map; feedback exposes it under native read permissions. Comparison with defined
limits remains separate from engineering acceptance. No live ERP records are
written by the demonstrator.

Civil quantities use the existing equal-scope double-track bill, explicitly
labelled separately from the single-track dynamic benchmark. Vehicle component
counts and mass update with the instance definition. Installed cost remains null
without rates, quotations and full scope: a mass change does not invent a saving.

## Spatial, material, joint and correlation workflows

The second adapter uses six translations/rotations per rigid body, bogie and
wheelset, full component inertia tensors, two individually flexible rails per
track, shear-flexible 3D decks, transverse caps, piers and six-direction
foundation springs. It solves the full sparse coupled equations; its diagnostic
modes do not truncate the transient calculation. The route supplies circular
horizontal and vertical alignment, grade and a cant ramp. Passenger counts come
from the frozen family profile; asymmetric payloads update CG and inertia.

The [spatial solver](../../engineering/civil_exploration/spatial_vehicle.py)
uses supplied wheel/rail profiles to locate one nonconformal contact patch,
elliptical Hertz normal contact and passive stick/slip traction. Contact can open
and reclose. It retains wheel spin, gyroscopic terms, reference alignment
acceleration, braking/traction demand, articulation loads, wheel forces, unloading,
lateral/vertical ratios, carbody acceleration, rail/deck response, foundation
reactions and all six structural member resultants. Primary wheel spin is a free
joint coordinate. Nonlinear supplied force/displacement and damping curves and
unilateral bump stops have separate tangents in the implicit solve.

Straight, curved/canted/braking/uneven, two-track crush/defect, and degraded
suspension/adhesion cases run from explicitly synthetic inputs. Simple spans,
continuous idealised members and finite six-direction link-slab connectors are
available. The mixed search includes native planar pile-group condensation in
both directions, retaining horizontal/rotation coupling. Its torsional spring is
separately declared, rather than claimed as a planar solver result. Site soil,
cyclic degradation and actual connection resistance remain required inputs.

```sh
tools/automation/osr-python tools/automation/shared-engineering-campaign.py \
  spatial --output build/engineering/spatial-campaign

tools/automation/osr-python tools/automation/shared-engineering-campaign.py \
  search --output build/engineering/shared-mixed-search --seeds 11,23

tools/automation/osr-python tools/automation/shared-engineering-campaign.py \
  joint --output build/engineering/shared-joint \
  --model build/engineering/spatial-campaign/definition.json \
  --dynamic-result build/engineering/spatial-campaign/straight-empty/dynamics.json

tools/automation/osr-python tools/automation/shared-engineering-campaign.py \
  verify --output build/engineering/spatial-campaign
```

Each campaign freezes source, solver environment, inputs, outputs and protocols.
Verification rejects changed outputs, sources, configuration evidence or
calibration records. Failed runs keep their partial evidence. A supplied hardware
model requires its own spatial configuration; it receives no synthetic material
strengths. Optional `--material-laws` supplies the actual region records.

The [material adapter](../../engineering/civil_exploration/assembled_materials.py)
uses the actual candidate regions and simultaneous member demands. Supplied
age/temperature curves, effective creep modulus, shrinkage/thermal eigenstrain,
compressive softening and energy-regularised tensile cracking enter fiber
section equilibrium. Steel has a plastic return law; composite layups retain
ABD coupling and local ply-face stress checks. The separate cohesive law uses
mixed-mode fracture energy and irreversible damage, retaining compression after
debonding. Supplied tendon losses alter section axial force and moment. Signed
member histories feed rainflow spectra and supplied S-N curves. Missing strengths,
interfaces or S-N coverage stay open. Section equilibrium does not certify shear,
torsion, local buckling, anchorage or history-dependent crack redistribution.

The [physical joint register](../../design/component-catalogue/src/osr_mech/joint_design.py)
keeps explicit fields for bolt patterns/stacks/preload, weld procedures, bonds,
bearing fits, suspension curves and articulation features. Unspecified production
fields remain null. Native TechDraw now includes elevation, plan, a powered-bogie
view, a section, named datums and inspection/joint references; generation checks
that every projection has visible geometry. Drawing issue remains separate.

The [solid submodel](../../engineering/civil_exploration/joint_submodel.py)
meshes two holed plates and a bolt/head/nut fixture with native Gmsh and solves
quadratic tetrahedra, face contact, friction and pretension with native CalculiX.
It first applies force pretension, then locks the retained pretension displacement
for the external-load step. Loads come from one simultaneous dynamic joint
vector; nodal allocation preserves force and moment. Reactions and shank stress
are retained for equilibrium/refinement review. The 80×60 mm coupon, 22 mm holes,
20 mm shank and cylindrical 34 mm head/nut are synthetic verification geometry,
not a released bogie connection. Actual installation solids, grip stacks,
fasteners, preload, locking, fits, procedures and limits require engineering data.

The mixed search reuses the existing civil option library for geometry, materials,
foundations, connections and construction. Random and Pareto evolution consume
equal trial budgets and identical deterministic uncertainty envelopes. Battery
mass and suspension settings also vary. It retains rejected designs, native
foundation calculations, logistics, scope quantities and finer finalist dynamics.
The initial dynamics are **short startup screens**, not complete operating or
resonance envelopes. Objective values are provisional; installed costs and the
qualified feasible Pareto set remain open without full rates, lifecycle scope,
accepted capacities and measured uncertainty distributions.

The [correlation adapter](../../engineering/civil_exploration/correlation.py)
checks exact model/revision/serial, retained measurement and calibration hashes,
timestamps, SI units and positive measurement uncertainty. Bounded inverse fitting
uses calibration specimens; different specimens form the holdout set. Results
retain sensitivity rank, local parameter covariance, holdout bias/RMSE and
measurement bands. Synthetic recovery tests cannot become physical validation.
The command-line forward evaluator calls the spatial solver for supplied contact
channels, with explicit stiffness/contact parameters:

```sh
tools/automation/osr-python tools/automation/shared-engineering-campaign.py \
  correlate --output build/engineering/prototype-correlation \
  --model path/to/definition.json --config path/to/spatial-input.json \
  --measurements path/to/measurements.json --parameters path/to/parameters.json \
  --holdout-specimens prototype-B
```

The [retained synthetic correlation inputs](../../engineering/civil_exploration/examples/shared-spatial-correlation-inputs/measurements.json)
exercise the same spatial forward solver. The planted primary stiffness factor is
0.9; the noisy calibration recovered about 0.910, with a separate specimen held
out. This remains an algorithm recovery test.

The generated four-level protocols cover parts, subassemblies, the train and
train/infrastructure passages. They require calibrated instruments, approved test
loads/routes/speeds, stop conditions, adopted project limits, specimen identities
and independent holdout/review records. No physical tests have been performed.

The [OpenSourceRail internal process standard](../standards/OSR-ENG-001.md)
now governs numerical verification and the prepared protocols, with applicable
ISO method references. Its numerical thresholds are OpenSourceRail rules.
[The retained assessment](../../engineering/civil_exploration/examples/shared-engineering-standard-assessment.json)
keeps ISO conformity and physical release open while evaluating the numerical
evidence.

## Complete-passage planning and motion histories

[Retained complete-passage review](../../engineering/civil_exploration/examples/shared-service-envelope-review.json).
The empty represented car pair completes an 8.13-second passage at 15 m/s.
Every recorded contact enters and clears the modelled track; separate time-step
and mesh checks pass the 5% numerical screen. The other planned cases are
explicitly unexecuted, and the full six-car operating envelope remains open.

The service-envelope workflow now places every represented wheel before the
modelled approach track and computes the time needed for the last wheel to clear
it. The case matrix includes empty/nominal/crush/uneven loads, operating speeds,
acceleration, service/emergency braking, rescue, maintenance, curves/cant/vertical
curves, irregularity/defects, synthetic wear, degraded suspension/ground/bearings,
and simultaneous traffic with different speeds and arrival offsets. A supplied
fine speed band adds resonance screening cases; generating a plan does not execute
or qualify those cases. Braking that stops before clearance is a stopping test.

```sh
tools/automation/osr-python tools/automation/shared-service-envelope.py \
  plan --output build/engineering/service-plan --resonance-band 14:16:.25

tools/automation/osr-python tools/automation/shared-service-envelope.py \
  run --output build/engineering/service-passages --cases empty-15mps \
  --dt .005 --mesh 2 --rail-step 2

tools/automation/osr-python tools/automation/shared-service-envelope.py \
  verify --output build/engineering/service-passages
```

Coverage uses each recorded wheel contact on both sides at every timestep, its
entry into the structure and clearance of the approach. Duration metadata alone
cannot establish a passage. These are the linearised adapter's nominal contact
interpolation stations; finite contact motion and actual operational train
clearance need the appropriate geometry and validation. The demonstration still
represents two cars of the six-car planning family; it does not qualify the full
111 m train. Unexecuted cases remain explicit in the campaign report.

Motion histories retain each body's global and nominal-body-axis acceleration,
angular acceleration, velocity, rotation perturbation and reference frame at the
rigid CG. Unweighted RMS, crest factor and fourth-power VDV are computed from the
actual time series. They are not ISO frequency-weighted comfort results or
seat/body-interface measurements. Body linear/angular acceleration and vertical
wheel-force channels can now be selected by the inverse-calibration adapter.
Invalid units, invalid solver domains and relabelled specimen serials are rejected.

Every converged sample is streamed to a deterministic compressed JSONL file.
Nonconvergence and wall-budget termination preserve the converged prefix. The
normal gap now includes lateral profile movement once, and sliding traction has
tangents for displacement direction and normal-force dependence. Lateral/vertical
ratios use the vertical force component; normal force is retained separately.
Powered axles receive the equivalent positive-traction demand; braking uses all
axles. Wheel-spin reference acceleration is included. Actual motor/brake control
laws, torque limits and finite moving-patch geometry remain required for release.

Finalist confirmation now uses the same uneven payload and adverse conditions as
its search scenarios. Time and mesh refinements are separate; a failed refinement
or domain check prevents a numerical confirmation claim. Assembly/capacity and
physical acceptance remain separate.

## Published evidence versions

The earlier vertical/spatial reviews and standards assessment are retained
unchanged as research evidence produced by commit `bcb21593fb`. Their source hashes
are not rewritten to match new solver code. Verify the producing source version:

```sh
tools/automation/osr-python tools/automation/verify-shared-review-history.py \
  engineering/civil_exploration/examples/shared-spatial-engineering-review.json \
  --revision bcb21593fb
```

This checks the publication and recorded code against the immutable Git commit.
It reports whether the current implementation matches, and does not requalify the
current solver or claim to verify unavailable bulk campaign outputs. New service
campaign receipts bind their own current source/environment and retained traces.

## Numerical scope and remaining release gates

Independent tests cover spherical Hertz contact/pressure, stick/slip passivity,
crack-band/cohesive energy, concrete small-strain stiffness and creep consistency,
steel yield return, laminate coupling/ply stress, bolt-group equilibrium, section
resultants and independent OpenSees 3D shear/bending/axial/torsional response.
Campaigns separately retain time and mesh refinements; a failed observable remains
failed. The 5% screening tolerance is numerical research policy, not a project
acceptance criterion.

The contact adapter rejects flange, multiple-patch and conformal contact; finite
body rotations and detailed railway rolling-contact reference comparison still
need appropriate adapters and benchmarks. Patch geometry checks do not establish
elastic material validity or accepted wheel pressure. Structural dynamics are
linear about the declared alignment, with Euler–Bernoulli consistent bending
mass and Timoshenko stiffness; component flexibility, plastic redistribution,
soil degradation and thermal/settlement histories require verified models and
project inputs. Startup transients are explicitly identified in the outputs.

FreeCAD, Gmsh, CalculiX and OpenSees are the executed core. Chrono, CONTACT,
Code_Aster/SALOME, OpenGeoSys and FMI/preCICE remain conditional choices; no
unavailable tool is represented as executed or railway-validated. The shared
identity and retained force/work histories define the boundary for those adapters.

Production release still requires released supplier geometry and properties,
actual manufacturing/QA records, adopted project standards and limits, full
operating/erection load cases, instrumented prototypes, independent holdout
correlation and the existing authority acceptance process. Software cannot
manufacture that evidence or release the drawings by filling synthetic slots.

Native joint semantics follow the [FreeCAD Assembly documentation](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Assembly_Workbench.md).
Solid pretension follows the [CalculiX user manual](https://www.dhondt.de/ccx_2.17.pdf).
[preCICE coupling configuration](https://precice.org/configuration-acceleration.html)
describes convergence mechanisms for a future partitioned adapter; the current
prototype solves the coupled equations monolithically.
