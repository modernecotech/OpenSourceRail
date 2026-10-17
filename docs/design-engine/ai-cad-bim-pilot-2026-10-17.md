# Executed CAD and BIM workflow pilot

17 October 2026. The [AI CAD/BIM review and operating guide](ai-cad-bim-workflow-2026-10-17.md) is accompanied by **ten executed candidates: eight research passes and two retained rejections**. The controller preserves 63 work packages, 345 allocated source items and 1,219 open requests. Completed railway specifications and physical/manufacturing releases remain zero.

The run used nine explicit benchmark seeds followed by **one new interactive assistant-authored proposal in response to measured failure**. No external AI provider or commercial CAD service was invoked. A separately configured provider can use the same proposal/feedback protocol; its subprocess protocol was tested with a fixture, not represented as an LLM experiment.

## Native part feedback

FreeCAD 1.1.4, OpenCASCADE through FreeCAD, Gmsh 4.14.1 and CalculiX 2.23 were actually executed. Every solid candidate used native correspondence, two mesh sizes, reaction balance and an independent elastic cantilever control. The table reports the loaded-face displacement used by the declared research screen, not a certified structural limit.

| Candidate | Defined mass kg | Displacement mm | Declared limit mm | Research result |
| --- | ---: | ---: | ---: | --- |
| Cleat, 12 mm solid web | 0.9367 | 0.8955 | 1 | Pass |
| Cleat, 16 mm lightened web | 1.2236 | 0.3913 | 1 | Pass; heavier and stiffer in this case |
| Beam, 6 mm RHS | 32.2164 | 7.2591 | 8 | Pass |
| Beam, 6 mm I-section | 23.1732 | 8.5515 | 8 | **Reject: displacement exceeds limit** |
| Feedback revision, 8 mm I-section | 30.5208 | 6.6629 | 8 | Pass |

After inspecting the failed 6 mm I-section result, the assistant proposed the registered 8 mm thickness while preserving its envelope, 10 kN end load and 8 mm displacement threshold. The revised beam is **5.3% lighter than the RHS reference** and has **8.2% lower displacement** for this bending case. It is a useful new candidate, not a whole-system optimum: torsion, local buckling, fatigue, connection/contact behaviour, corrosion, process capability and physical evidence remain open. The independent control is an unperforated cantilever benchmark, not a strength qualification for these components.

## Assemblies and civil BIM

| Assembly | Physical part records | Defined mass kg | Executed correspondence |
| --- | ---: | ---: | --- |
| Vehicle interface research assembly | 14 | 378.025 | Native solids/placements, mass/CG/inertia, collision checks, reopen, STEP volume and nonempty TechDraw projection |
| Revised battery-carrier assembly | 14 | 382.396 | Same checks after carrier RHS wall changes from 3 to 4 mm and exact properties are regenerated |
| 20 m research civil bay, including foundations | 77 | 273,683.643 | Same native checks, IFC4X3 export, physical volume correspondence and full EXPRESS/schema validation |

These are partial design assemblies. Simplified fasteners, incomplete reinforcement/anchorage, supplier equipment, joining details, accepted tolerances and issued drawings remain open. The civil mass includes all represented bay/foundation parts; it is not the beam mass or a proven foundation design.

The new schema check exposed **four analytical IFC defects** in the retained research exporter: missing placements on one structural member and two supports, and a bare topological edge inside a shape representation. The new adapter adds explicit identity placements and a geometry-backed edge curve. Validation then reports **zero schema issues**. The regression check confirms unchanged physical product identities, placements and representation records. The civil model's maximum tessellated physical-volume error is **0.001664%**, within the declared 0.05% tolerance.

The IFC retains one gross elastic analysis member, two idealised supports and one self-weight load. **The civil analysis model was not solved by this adapter.** Schema and geometry correspondence do not establish civil capacity, foundation response, load combinations or physical validity. The failed initial attempt remains in the local historical workspace; the published final archive retains the before/after schema issues and corrections.

## Software checks

The same 19 healthy/adverse cases were applied to both existing precharge policies. The ratio-only policy fails **13 cases** and is rejected; the guarded policy has **zero failures** in this suite. This demonstrates an executable policy comparison, not complete train software, target-code generation, real-time acceptance or HIL.

## Verification and retained evidence

**153 regression tests passed; 6 optional native integration tests were skipped** because `OSR_RUN_NATIVE_PARTS` was not enabled. The native executions described above were run separately through the new controller and retained. Regression coverage includes stale-input rejection, duplicate/no-progress termination, atomic submission, provider timeout, immutable output checks, adverse controls and real IFC schema corrections. The inherited federated twin remains verified against its current sources.

The final workspace passed `verify` with current source hashes and retained artifact hashes. Its baseline is `b88de20de9a7229d12f1e3181e83b7bf5096483c07ff3f422bf09443f6d26bcc`. It stopped with `needs-new-proposals-or-evidence`, with no queued designs. Repeating the same run does not launch new native work.

Published files:

- [Machine-readable results](ai-cad-bim-pilot-2026-10-17/results.json), including actual metrics, checks, toolchain and source digests.
- [Complete final-workspace archive](ai-cad-bim-pilot-2026-10-17/evidence.tar.gz), including editable recipes, native FCStd and STEP models, IFC, TechDraw records, mesh/solver inputs/results, logs, work orders and receipts.
- [Publication manifest](ai-cad-bim-pilot-2026-10-17/manifest.json), binding the result and archive bytes.

To inspect the retained workspace without running new solvers:

```bash
mkdir -p build/cad-bim-pilot-2026-10-17
tar -xzf docs/design-engine/ai-cad-bim-pilot-2026-10-17/evidence.tar.gz \
  -C build/cad-bim-pilot-2026-10-17
tools/automation/osr-python tools/automation/twin-completion.py verify \
  --workspace build/cad-bim-pilot-2026-10-17
```

After an engineering source change use `verify --historical` only to check retained integrity. A current design requires a fresh baseline and affected evaluations. The archive is bounded local evidence; no repository clone, CAD account, GPU stack or external upload is required.

The next completion work is the programme in the [review](ai-cad-bim-workflow-2026-10-17.md#expanding-the-adapters-to-complete-the-railway): exhaustive BOM decomposition, additional discipline/assembly adapters, dimensioned manufacturing packages, integrated executable software and HIL, calibrated physical evidence and accountable acceptance. The controller cannot close those requirements by assigning a pass to these examples.
