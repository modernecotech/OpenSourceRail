# SolidCraft / FieldCraft backend pilot

The retained backend pilot constructed source-bound component geometry in
SolidCraft and matched mechanical method controls in FieldCraft. The current
release pair has a CAD-to-FEA handoff hold described below. This is an **opt-in
backend comparison**, integrated with the existing candidate and delivery records.
FreeCAD, CalculiX, Gmsh/GetDP, IFC/Bonsai, Chrono and SUMO remain available.

```bash
./osr design backends refresh solidcraft fieldcraft
./osr design backends install solidcraft fieldcraft
./osr design backends plan
./osr design backends run --output /path/to/private/fresh-run
./osr design backends verify --output /path/to/private/fresh-run
```

The local selected-reference packet is currently held because its manifest is
missing. The pilot cannot plan or run that selected case until a source-matched
packet is regenerated. Refresh and installation can be done separately; plan,
run and verify above describe the workflow after that hold is resolved.

Linux requires bubblewrap, GNU time, CalculiX (`ccx`), and the existing
`org.freecad.FreeCAD` Flatpak. Explicit refresh resolves the latest stable
upstream releases; installation verifies archive and executable digests and
retains licence notices. There is no automatic unconfined execution fallback.

## What is compared

| Case | Source occurrences | Scope |
|---|---:|---|
| Selected 20 m beam | 6 | Concrete walls/flanges and two end diaphragms; reinforcement, tendons and anchorage excluded |
| Selected 17 m side sill | 4 | Aluminium material walls in installed coordinates; no exploded-display translation |
| Research launch shuttle | 14 | Separate research layout, with unknown equipment/rubber mass retained |
| Asymmetric unit control | 1 | Unequal dimensions and nonzero translations expose mm/m and placement errors |

Each occurrence retains its source ID, physical candidate and component geometry
identity. Changing a provider changes the evaluation context, not the physical
candidate. The selected geometry subsets refer to their existing BOM,
manufacturing, procurement, cost and IFC packages; their costs are not added a
second time. The shuttle does not inherit the selected train's costs or approval.

SolidCraft scripts convert metres to millimetres explicitly. Each occurrence is
a separate solid, with explicit material-density hypotheses where available.
The provider's default material and mass are never installed-mass evidence.
Generated, reopened native, reopened STEP and independently imported STEP solids
are compared by per-part volume, centroid and tight bounds. Curved tessellation
measurements are diagnostics; FreeCAD/OpenCASCADE supplies the independent exact
B-rep comparison. No Boolean-union volume or complete equipment CG is claimed.

The mechanics controls are a one-metre isotropic cantilever on two hex20 meshes,
and an axial rod. FieldCraft receives explicit `m-kg-s-N-Pa` model units. Named
supports/loads survive remeshing; a named geometry face set is also checked on
design reopening. Independently generated CalculiX decks and analytical theory
provide comparisons. These are method controls, **not complete beam, vehicle or
arrestor structural analyses**. The next admission tasks remain full assembly
loads/connections, torsion, buckling, contact, fatigue and applicable material
models. GetDP remains the electromagnetic route and IFC remains the BIM route.

## Verified compatibility boundaries

- The current releases are **SolidCraft 0.42.0 / FieldCraft 0.7.5**. SolidCraft
  primitives passed the bounded current CLI probe. FieldCraft's native reader
  does not accept this SolidCraft version. A one-box SolidCraft v0.42 STEP export
  succeeded, but FieldCraft v0.7.5 rejected both its `open` and `geometry.open`
  routes. The active adapter records the STEP hash and explicit FEA hold. A
  compatible same-candidate geometry/load/mesh/material handoff remains open.
  The earlier 0.30.1 and 0.40.0-rc.2 probes remain
  [historical results](pilot-results.json), not active installation choices.
- SolidCraft native/STEP reopening retains body names. FreeCAD's STEP importer
  exposes product labels instead. The pilot reports this name-retention hold.
  An unambiguous volume/centroid/bounds bijection verifies geometry separately;
  it does not pretend the importer preserved source IDs.
- SolidCraft density assignments do not create FieldCraft structural materials.
  Analysis materials, loads and constraints must be declared independently.

### Explicit Code_Aster one-box handoff control

`code_aster_control.py` is a separate, bounded fallback experiment for the
rejected FieldCraft STEP route. It imports the exact SolidCraft STEP through
Gmsh/OpenCASCADE in metres, writes a named-face tetrahedral MED mesh, checks
the volume against an independent FreeCAD/OpenCASCADE reimport, and only then
attempts a Code_Aster static solve. The control uses a 1 m × 0.3 m × 0.2 m
box, a fixed `x=0` face, 1,000 N distributed across the `x=1` face, and an
explicit isotropic material hypothesis (`E=70 GPa`, `ν=0.33`,
`ρ=2,700 kg/m³`). Its reaction, displacement and energy are checked against
equilibrium, external work and the axial analytical control. Source, STEP,
Gmsh library and container image hashes are retained with the private run.

The current Code_Aster 17.4.0 control used image digest
`sha256:d8d19ea91989eac0d38195bc5795c54c69f530f7196f53d67697ffa57c9106d5`
and completed under request
`01ece7a47c065c2659cfb9a95f92bf26e4527ab1c4c6067bdb68ff2c93f8b17c`
and native evaluation
`7a2efd69f8774d040b25fd70d2327d9e61a8d8b80ac5dcc397df1ed41d1feea2`.
Gmsh 4.15.2 generated the MED mesh. The STEP and tet10 mesh both measure
0.060000 m³; the mesh has 857 nodes and 400 elements. The fixed-face reaction
is −1,000.0000000000075 N for a 1,000 N
load, the mean loaded-face displacement is 2.355495351978692×10⁻⁷ m, and
elastic energy is 1.1777470023092778×10⁻⁴ J. Independent force and
energy/work residuals are 7.5×10⁻¹⁵ and 5.72×10⁻⁷; the displacement differs
from the axial control by 1.07%. The 24-artifact private run verifies with
physical acceptance false. Failed launch attempts and their logs remain in the
sealed run package. Rootless Docker did not enforce aggregate memory or CPU
cgroups; the execution used a 2 GiB per-process address-space limit, one MPI
worker and thread, and a 180-second timeout. Code_Aster reported 783.50 MB
peak process memory.

```bash
./osr design backends code-aster-box \
  --step /path/to/exact/assembly.step \
  --output /path/to/private/fresh-control \
  --candidate-id explicit-synthetic-box-id \
  --fieldcraft-rejection /path/to/held-readback.json \
  --image simvia/code_aster:17.4.0 \
  --python /path/to/python-with-current-gmsh
./osr design backends verify-code-aster-box \
  --output /path/to/private/fresh-control
```

The refusal receipt must identify the same candidate and exact STEP hash, and
show both FieldCraft import routes rejected. The image argument is explicit so
the adapter does not silently select an
older installation. The current stable 17.4.0 image is listed by the
[Open Simulation Center](https://open-simulation-center.org/fr/downloads/code_aster/code_aster/17.4.0)
and its use in a direct `run_aster` invocation is described on the
[Code_Aster forum](https://code-aster.org/forum/t/weird-behavior-in-docker/12303).
The adapter pins the installed image by immutable repository digest before
execution. An unavailable image, failed import, failed geometry check or
nonconverged native solve is recorded as held. A completed numerical control
does not qualify the selected beam, side sill or vehicle. Their same-candidate
loads, supports, materials, interfaces and resource requests remain separate
admission work, and the missing selected-reference manifest remains a hold.

### Candidate-bound Code_Aster component handoff

`code-aster-candidate` extends the proven handoff to an explicitly identified
single-solid SolidCraft STEP component. Its definition supplies the physical
candidate and component geometry IDs, expected exact B-rep volume and bounds,
an isotropic elastic material hypothesis, mesh size, one fully fixed end face,
the opposite loaded face and the total three-component force. Gmsh selects
faces from the imported STEP geometry and divides the force by their measured
area. Independent FreeCAD/OpenCASCADE import checks the volume, bounds and
closed solid before a native solve is admitted. A different load or material is
a different evaluation of the same physical geometry.

```bash
./osr design backends code-aster-candidate \
  --step /path/to/exact/component.step \
  --definition /path/to/candidate-fea-definition.json \
  --fieldcraft-rejection /path/to/same-candidate-held-readback.json \
  --output /path/to/private/fresh-run \
  --image simvia/code_aster:17.4.0 \
  --python /path/to/python-with-current-gmsh
./osr design backends verify-code-aster-candidate \
  --output /path/to/private/fresh-run
```

The second bounded control is an actual SolidCraft 0.42.0 STEP box with unequal
dimensions, offset origin and a 1,500 N declared axial load. FieldCraft 0.7.5
again rejected both STEP import routes for those exact bytes. Gmsh 4.15.2
produced a 0.12 m³ MED mesh with 529 tetra10 elements, 1,100 nodes and 0.1 m²
fixed and loaded faces; independent FreeCAD reimport agreed. Its 19-artifact
private packet verifies, including the generated Code_Aster material,
boundary, traction and result deck. The Code_Aster image was unavailable while
the railway campaign's disk reserve was active, so this second case is recorded
as **held before native solve**. The separate one-box control above remains the
executed native Code_Aster proof. Neither control resolves selected component
loads, joints, fatigue, buckling, material allowables or physical qualification.

Source releases, commits, asset hashes, executable hashes and licences are in
[`tools.json`](../../../engineering/design_search/craft_backends/tools.json).
The [pilot policy](../../../campaigns/craft-backend-pilot.toml) bounds 25 parts,
one sequential worker, at most 32 native processes, 120 seconds and 2 GiB address
space per native process. The planned full workload uses at most 25 process
slots but is currently held. This is not an aggregate memory
cgroup or independently authenticated physical evidence.

## Evidence, reuse and promotion

Each fresh private run retains the exact SI cases, JSON commands, source and tool
pins, input/output hashes, stdout/stderr, wall/CPU/RSS measurements, comparisons,
failed imports and delivery sidecars. Files are never overwritten. Bubblewrap
sessions hide home directories, expose designated inputs read-only, allow writes
only to the native session, and have no network or graphics devices. FreeCAD
uses its separately recorded Flatpak permissions and observed native limits.

`verify` checks the complete inventory, request context and source-bound receipts,
then recomputes comparisons from stored readbacks. It performs **no fresh solve**;
this distinction is explicit in the result. Geometry, assumptions, code, tool or
resource changes invalidate reuse. Tool path scopes supplement OS isolation;
they are not a claim that upstream path handling has no races.

`software_pilot_passed` reports these bounded comparisons only. Native naming,
material and unsupported-physics limitations remain visible. It does not select
the tools globally, admit arbitrary geometries to native evaluators, or grant
engineering, manufacturing or operating acceptance. Promotion should follow a
larger matched CAD/FEA campaign with complete interfaces and independent review.

Upstream references: [SolidCraft commands](https://docs.solidcraft.io/dev/commands.html),
[SolidCraft v0.42.0](https://github.com/tangency-labs/solidcraft/releases/tag/v0.42.0),
[FieldCraft v0.7.5](https://github.com/tangency-labs/fieldcraft/releases/tag/v0.7.5).

## Detailed launch assembly follow-on

The [R3 launch-shuttle dossier](../launch-detail/README.md) contains dimensioned parts, a counted assembly, native CAD/STEP checks, an actual clevis-ear bearing-load FEM comparison, and a bounded fabrication estimate. It preserves the earlier pin-bending failure and distinguishes local component results from full-shuttle or propulsion qualification.

## Extended same-candidate viaduct workflow

The [12-span CAD, mechanics and manufacturing comparison](../viaduct-backends/README.md)
now exercises reusable CAD, analysis and delivery interfaces. Download the actual
SolidCraft/STEP/STL models, inspect independently measured geometry, compare two
coarse/fine FieldCraft/CalculiX studies, and follow each candidate into its
quantities, scoped costs and provisional production route. Original failed
executions and the separate box memory-budget revision remain explicit.

```bash
./osr design backends providers
./osr design backends viaduct plan
./osr design backends viaduct verify-publication
```

This is an opt-in research path with bounded eligibility. It does not promote
new tools globally or establish bearing/contact, reinforced-concrete resistance,
manufacturing release or complete installed bridge cost.
