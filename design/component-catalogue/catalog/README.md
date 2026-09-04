# Generated Mechanical Review Artifacts

This directory contains generated mechanical review artifacts from
`design/component-catalogue`. The authoritative designs are the parametric source
files under [`../src/osr_mech/`](../src/osr_mech/). Tracked artifacts
are FreeCAD `.FCStd` review documents, FEA screening output, and
screenshots referenced from the docs. Neutral CAD interchange exports
are local-only scratch files and are ignored by git.

## Regenerate

FreeCAD review documents are regenerated with:

```bash
tools/automation/design-iterate.sh
tools/automation/buildable-trainset.sh
tools/automation/buildable-civil.sh
PYTHONPATH=design/component-catalogue/src design/component-catalogue/scripts/freecad_trainset.sh --family light-metro-3car
PYTHONPATH=design/component-catalogue/src design/component-catalogue/scripts/freecad_assembly_review.sh
PYTHONPATH=design/component-catalogue/src design/component-catalogue/scripts/freecad_fea.sh
```

Supplier interchange exports, when needed, should be written outside
the tracked tree or left ignored.

## Sections

| Folder | Scope |
|---|---|
| [`design-system/`](design-system/) | Generated top-down / bottom-up design iteration scorecards and candidate shortlists |
| [`buildable-trainset/`](buildable-trainset/) | Generated buildable product tree from parts through subassemblies, assemblies, and the trainset |
| [`buildable-civil/`](buildable-civil/) | Generated 19-type civil/IFC accountability register, six release packages, nine drawing briefs and empty authority record |
| [`../models/cad/`](../models/cad/) | FreeCAD review assemblies, including trainset, assembled/exploded state documents, and FEA-screening model documents |
| [`fea/`](fea/) | FreeCAD/CalculiX first-pass beam-model screening inputs, solver outputs, and result summaries |
