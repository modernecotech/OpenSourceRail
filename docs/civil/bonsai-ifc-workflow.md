# Bonsai / IFC4.3 Civil Workflow

Status: implemented design-reference workflow  
Baseline: Bonsai 0.8.5, Blender 5.2, IfcOpenShell/IfcTester/BCF 0.8.5, IFC4.3

## Decision

Bonsai is better suited than FreeCAD alone for the federated civil BIM part of
OpenSourceRail: native IFC authoring, rail-domain object classification,
property and quantity inspection, drawing/coordination work, and construction
sequence review. It is not currently a better source for deterministic railway
alignment engineering. The OSR alignment engine and parametric civil catalogue
therefore remain authoritative; Bonsai receives a generated IFC4.3 model and
must not silently override its route or engineering rules.

| Information | Authority | Bonsai role |
|---|---|---|
| Horizontal/vertical alignment, transitions, cant and rule checks | OSR-ALN plus accepted survey/GIS inputs | Inspect the exported `IfcAlignment` reference and coordinate issues |
| Pier, girder, trackform, platform and canopy parameters | `mechanical-py/src/osr_mech/` | Federate, classify, inspect, annotate and develop deployment detail against stable IDs |
| Structural capacity, reinforcement, bearings, foundations and temporary works | Reviewed analysis decks and engineer-released drawings | Coordinate released results; never infer approval from visible geometry |
| IFC object hierarchy, property sets, quantities and 4D task links | Generated IFC checked by IfcOpenShell | Native GUI authoring/review environment |
| Revision identity | City Studio content hash and Git revision | Carry revision and source hashes in IFC properties and the saved Blender scene |

This boundary reflects current upstream limitations: Bonsai's road/rail guide
describes its PI CSV alignment import as a temporary stop-gap, while the
IfcOpenShell alignment API is still under development and explicitly does not
select engineering design parameters.

## Generate and review

Check the installed stack:

```bash
scripts/bonsai-civil.sh --check
```

Generate deterministic IFC and JSON evidence without opening Blender:

```bash
scripts/bonsai-civil.sh --generate
```

Generate, import through Bonsai, save a native review scene, and render it:

```bash
scripts/bonsai-civil.sh --render
```

Render the normalized construction sequence as MP4 as well:

```bash
scripts/bonsai-civil.sh --animate
```

To bind the federation to a City Studio line, use the **Generate Bonsai civil
IFC4.3** job in the engineering hub. The adapter converts the selected line to
the local engineering frame and supplies that immutable reference axis to the
same exporter.

Outputs are written beneath `build/engineering/bonsai-civil/`:

- `civil-coordination.ifc` — native IFC4.3 model;
- `civil-coordination.index.json` — object-aware browser index and authority boundary;
- `civil-construction-sequence.json` — tasks, dates, QA holds and product assignments;
- `civil-information-requirements.ids` — buildingSMART IDS 1.0 delivery requirements;
- `civil-information-requirements.report.json` — complete deterministic IDS audit evidence;
- `civil-coordination-issues.bcf` — BCF 3.0 package with object-linked release issues;
- `civil-coordination-issues.index.json` — browser-safe issue and IFC selection index;
- `civil-coordination.validation.json` — reopen, IDS, BCF-link, and exact artifact-hash checks;
- `civil-coordination.blend` — Bonsai scene retaining IFC links and the animation timeline;
- `civil-coordination.png` and optional MP4 — reproducible visual review artifacts.

## Model content

The current reference federation contains 82 stable assets organised below an
`IfcRailway` and four `IfcRailwayPart` containers: track, substructure,
above-track systems, and lineside/clearance. Civil objects use IFC4.3 types
including `IfcRail`, `IfcBeam`, `IfcColumn`, `IfcSlab`, `IfcRoof`, and an
`IfcAlignment` reference. Each object carries:

- stable OSR asset ID and class;
- canonical source and source hash;
- revision ID and lifecycle status;
- inspectable coordination dimensions and source net volume;
- explicit detail mode when a complex assembly is represented by its review envelope.

Sixteen track, station, and viaduct tasks are embedded in an
`IfcWorkSchedule`. Final installation tasks are linked to their output products
for Bonsai 4D visualization; predecessors, planning durations, QA holds, and
required evidence remain in the companion sequence index.

## IDS delivery gate and BCF review loop

The exporter writes an IDS 1.0 contract and immediately reopens it with
IfcTester against the written IFC. Three specifications require all 82 civil
assets to carry stable identity, source, revision, lifecycle and coordination
dimensions; require the alignment to state its upstream authority; and require
the project to state its source hash and release status. The current reference
exchange passes all 828 entity-level checks. The audit is deterministic: entity
evidence is sorted before hashing, so a repeat build produces byte-identical
IFC, IDS, audit, BCF, indexes, sequence, and validation files.

Passing IDS means that the information delivery is complete for this declared
coordination purpose. It does not mean the design is structurally or legally
released. The generated BCF 3.0 package therefore carries three open issues
with viewpoints and selected IFC GUIDs:

1. replace the planning axis with accepted survey and alignment geometry;
2. release the elevated station deck structural design;
3. complete the viaduct span, bearing, pier, foundation, and reinforcement work.

City Studio exposes the requirement report and issue index alongside the IFC.
Bonsai can open the native BCF package for discipline coordination and issue
closure against the same stable objects.

City Studio stores a review decision in the project's committed
`coordination/issues.toml`. It never rewrites a prior BCF artifact. Closing or
resolving a topic requires both resolution evidence and a reviewer; the next
civil job reads the new content-addressed revision and emits a fresh BCF with
the same deterministic topic/viewpoint identities and updated status,
assignee, resolution, and reviewer.

## Engineering release boundary

The generated model is deliberately labelled **design-reference / not for
construction**. Its nine current gates check interface geometry such as
rail/platform datums, clearance gaps, pier bearing top to girder soffit, and
station/viaduct track-support continuity. It does not release geotechnical
parameters, reinforcement, prestress, bearing schedules, seismic restraints,
drainage capacity, construction loads, or local-code compliance. Those remain
deployment analyses and competent-engineer decisions linked back into IFC only
after review.

## Upstream references

- [Bonsai introduction and native IFC workflow](https://docs.bonsaibim.org/quickstart/introduction_to_bim.html)
- [Bonsai road and rail alignment guide](https://docs.bonsaibim.org/guides/alignment.html)
- [IfcOpenShell alignment API and current design limitations](https://docs.ifcopenshell.org/autoapi/ifcopenshell/api/alignment/index.html)
- [IfcTester IDS API](https://docs.ifcopenshell.org/autoapi/ifctester/ids/index.html)
- [IfcOpenShell BCF 3 topic API](https://docs.ifcopenshell.org/autoapi/bcf/v3/topic/index.html)
- [buildingSMART IFC4.3 rail domain](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/ifcraildomain/content.html)
