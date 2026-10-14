# Shared engineering definitions and demonstrators

These research packages link proposed manufacturing geometry, analytical reductions and civil coordination by physical part identity, revision and geometry hash. FreeCAD is the native geometry authority; IFC carries the civil arrangement and an explicitly scoped analytical deck model. They are not issued manufacturing designs or qualified infrastructure.

| Demonstrator | Implemented package | Evidence still required |
|---|---|---|
| Clipped side bay | Trimmed ply/bond/core/solid-land regions, bored potted inserts, drilled rails, clips, brackets, fasteners and aperture frame | Local pressure/contact/peel response, joint stiffness, trim details, retention, complete-stack fire and prototype correlation |
| Curved roof bay | Exact circular layered solids, oriented support rails, brackets, clips and fasteners | Curved contact lands and insert arrangement; 85°C roof case fails the selected foam grades' 70°C continuous-temperature datum |
| Bogie–underframe interface | Hollow manufactured sills/carriers, drilled plates, dimensional bolt shanks/heads/nuts, preload/slip/separation screen, actual assembly mass/CG/inertia and reduced modes | Threads/fits, local contact/prying/weld fatigue, supplier suspension laws, equipment/fluids and measured modes; this is not a whole-train modal basis |
| Viaduct bay and construction front | Deck, longitudinal reinforcement, two pier/cap/bearing sets, eight piles with explicit embedded bars, tendon reservations, full LM3 twelve-axle two-track elastic sweep, lifting/jacking cases and one-mould resource calendar | Transverse cages, anchorage, prestress history/losses, cracking/shear/torsion/cyclic resistance, calibrated ground layers, lifting/local stability, crane charts and quoted costs |

[Generated definitions and correspondence](examples/manifest.json) bind SI dimensions and material regions to each representation. Native audits independently integrate occupied solids for mass, CG and inertia, reject material overlaps, reopen each FCStd, check inspection projections and reimport STEP exports. Inspection drawings remain unissued. IFC exports exact civil extrusions, verifies tessellated volumes against material quantities and defines a deck member, pin/roller connections and a dead-load activity. Its deck idealisation excludes the uncalibrated pier/bearing/ground compliance.

[Actual CalculiX/Gmsh section benchmarks](examples/solver/verification.json) compare B32R BOX hollow-beam bending with independently meshed C3D10 solids at two resolutions. The outer dimensions and walls drive both models. Thin-wall torsion is labelled separately from the polar area moment; this bending benchmark does not qualify torsion or a joint. The legacy static FEA generator now also emits explicit hollow study geometry and matching BOX sections, using proposed 8 mm research walls. Historical solid-envelope results are retained in Git history; they are not evidence for the revised sections.

[Interface modes](examples/interface-modes.json) transfer each physical part's mass, CG and inertia into a kinetic matrix. A rigid-motion check independently reconciles total assembly mass/inertia, and exported modes are mass normalised. Gross-section stiffness, plate reductions, rigid equipment mounts and suspension springs are explicit assumptions. No complete vehicle basis is adopted.

[Joint screen](examples/interface-joint-screen.json) calculates bolt/member elastic stiffness, retained clamping, slip resistance, separating load and a fatigue stress range. Assumed friction and prying cannot establish bolt, weld or fatigue qualification. [Civil stages](examples/civil-stages.json) retain failed deflection checks and unknown detailed resistance. [Construction front](examples/construction-front.json) counts installed deck reinforcement/tendon mass, checks transport/lift limits and rejects conflicting resource assignments. The 20 m arrangement exceeds the declared truck payload; its calendar is blocked and its quoted installed cost is unknown.

[Mixed search](examples/mixed-search.json) uses real core depths, integer support counts, categorical supplier grades and binary roof geometry. Installed mass and attachment-count complexity are separate objectives. Three seeds each receive an equal-budget random benchmark and a 3.5 kPa holdout. Failed mandatory checks exclude a candidate; unknown fire, fatigue, joint, manufacturing and batch data remain unknown. The conditional frontier is not a verified frontier or a global optimum. Quoted cost, lifecycle cost, repair time and controlled carbon stay unresolved.

Foam grades select coupled density, compressive modulus, shear modulus/strength, conductivity and temperature records from the [DIAB May 2026 datasheet](https://diab-media.azureedge.net/eyajkrhd/diab-divinycell-h-may-2026-rev26-si.pdf). Public nominal/minimum values do not substitute for project batches, hot/wet ageing, fire tests or supplier quotes. Normal and shear properties are independent; an isotropic constitutive fit is not implied. Roof processing-temperature limits are not continuous service allowables.

Regenerate the Python/IFC/search/solver package:

```sh
.venv/bin/python tools/automation/design-consistency-study.py --ifc --search --solvers
flatpak run --filesystem="$PWD" --command=FreeCADCmd org.freecad.FreeCAD tools/automation/verify-design-consistency-cad.py
.venv/bin/python tools/automation/design-consistency-study.py --check
.venv/bin/python -m pytest -q engineering/analysis/tests/test_design_consistency.py
```

Install the isolated analysis dependencies from [requirements.txt](requirements.txt). Native verification requires FreeCAD with Part and TechDraw; solver benchmarks require CalculiX. The recorded tool versions describe executed research evidence, not approved toolchains. The IFC model uses [IfcOpenShell's structural API](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/structural/index.html); search uses [pymoo's mixed-variable support](https://pymoo.org/customization/mixed.html). Code_Aster, MBDyn and topology optimisation remain follow-on integrations and are not reported as executed.

The [clipped-panel response refinement](../panel_response/README.md) now adds a trimmed plate, discrete attachments, actual rail bending, all single-clip-loss locations and combined pressure/fault checks, with five native manufactured arrangements. The first delivery establishes shared definitions and bounded numerical/native checks. Remaining engineering work is deliberately concentrated in these arrangements: mesh/contact response for the trimmed laminate, calibrated joints and equipment inventory, an assembled full-vehicle modal/contact/service envelope, detailed reinforced/prestressed civil resistance and construction stability, then measured prototype correlation. Every physical-release field remains false.
