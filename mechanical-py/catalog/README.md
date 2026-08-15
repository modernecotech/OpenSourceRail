# Generated Mechanical Review Artifacts

This directory contains generated mechanical review artifacts from
`mechanical-py`. The authoritative designs are the parametric source
files under [`../src/osr_mech/`](../src/osr_mech/). Tracked artifacts
are FreeCAD `.FCStd` review documents, FEA screening output, and
screenshots referenced from the docs. Neutral CAD interchange exports
are local-only scratch files and are ignored by git.

## Regenerate

FreeCAD review documents are regenerated with:

```bash
scripts/design-iterate.sh
scripts/buildable-trainset.sh
PYTHONPATH=mechanical-py/src mechanical-py/scripts/freecad_trainset.sh --family light-metro-3car
PYTHONPATH=mechanical-py/src mechanical-py/scripts/freecad_assembly_review.sh
PYTHONPATH=mechanical-py/src mechanical-py/scripts/freecad_fea.sh
```

Supplier interchange exports, when needed, should be written outside
the tracked tree or left ignored.

## Sections

| Folder | Scope |
|---|---|
| [`design-system/`](design-system/) | Generated top-down / bottom-up design iteration scorecards and candidate shortlists |
| [`buildable-trainset/`](buildable-trainset/) | Generated buildable product tree from parts through subassemblies, assemblies, and the trainset |
| [`freecad/`](freecad/) | FreeCAD review assemblies, including trainset, assembled/exploded state documents, and FEA-screening model documents |
| [`fea/`](fea/) | FreeCAD/CalculiX first-pass beam-model screening inputs, solver outputs, and result summaries |
