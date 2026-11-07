# SolidCraft / FieldCraft backend pilot

OpenSourceRail can now construct source-bound component geometry in SolidCraft
and run matched mechanical method controls in FieldCraft. This is an **opt-in
backend comparison**, integrated with the existing candidate and delivery records.
FreeCAD, CalculiX, Gmsh/GetDP, IFC/Bonsai, Chrono and SUMO remain available.

```bash
./osr design backends plan
./osr design backends install solidcraft fieldcraft
./osr design backends run --output /path/to/private/fresh-run
./osr design backends verify --output /path/to/private/fresh-run
# Optional newer-format / tagged-surface compatibility test:
./osr design backends install solidcraft-rc
./osr design backends run --include-rc --output /path/to/another/fresh-run
```

Linux requires bubblewrap, GNU time, CalculiX (`ccx`), and the existing
`org.freecad.FreeCAD` Flatpak. Installation downloads only the selected pinned
upstream release, verifies its archive and executable digests, and retains its
licence notices. There is no automatic unconfined execution fallback.

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

- The pinned compatible pair is **SolidCraft 0.30.1 / FieldCraft 0.7.5**.
  FieldCraft's convenience `open` rejects `.sc`; the adapter uses its tested
  `geometry.open` command without renaming the source file.
- **SolidCraft 0.40.0-rc.2** writes format 50, which FieldCraft 0.7.5 (format 48)
  rejects. The optional probe records this failure and tries face-tagged 3MF.
  A tagged surface is not an exact solid, editable parametric history or a
  complete transfer of analysis/material definitions.
- SolidCraft native/STEP reopening retains body names. FreeCAD's STEP importer
  exposes product labels instead. The pilot reports this name-retention hold.
  An unambiguous volume/centroid/bounds bijection verifies geometry separately;
  it does not pretend the importer preserved source IDs.
- SolidCraft density assignments do not create FieldCraft structural materials.
  Analysis materials, loads and constraints must be declared independently.

Source releases, commits, asset hashes, executable hashes and licences are in
[`tools.json`](../../../engineering/design_search/craft_backends/tools.json).
The [pilot policy](../../../campaigns/craft-backend-pilot.toml) bounds 25 parts,
one sequential worker, at most 32 native processes, 120 seconds and 2 GiB address
space per native process. The admitted full workload uses at most 29 process
slots with the optional compatibility probe. This is not an aggregate memory
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
[SolidCraft source](https://github.com/tangency-labs/solidcraft/tree/8e2b0cd60d14b4152b12b8f1fdb2bcfdcd8c52f4),
[FieldCraft source](https://github.com/tangency-labs/fieldcraft/tree/6b613217851b4c5ddf2d315930db12e9e25354dc).

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
