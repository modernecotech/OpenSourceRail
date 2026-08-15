# Rolling-stock top-down / bottom-up design system

This is the design authority layer above the parametric CAD. It gives
the project a systemic way to move from whole-train intent down to
bought-in parts, fabricated parts, subassemblies, final assemblies, and
then back up through scoring and evidence.

The rule of thumb is simple:

1. Start top-down with requirements: platform fit, axle load, range,
   traction margin, thermal margin, cost, mass, manufacturability, and
   safety evidence.
2. Decompose into the owned design hierarchy:
   external components, fabricated parts, subassemblies, final assemblies.
3. Iterate candidate definitions automatically inside an explicit design
   space.
4. Promote only feasible candidates into FreeCAD/FEM regeneration.
5. Freeze only when the requirements scorecard, supplier evidence, CAD,
   FEM, BOM, and manufacturing plan agree.

## Hierarchy

| Layer | Meaning | Examples | Source of truth |
|---|---|---|---|
| Top-level requirements | What the train must achieve | platform margin, range, axle load, cost, mass, traction/HVAC margin | `osr_mech.design_definition.REQUIREMENTS` |
| External components | Bought-in or BID/SOURCE modules | traction motors, HVAC, batteries, doors, glazing, sensors, couplers | `ExternalComponent` records plus supplier evidence |
| Fabricated parts | Parts OSR owns and regional workshops make | shell, bogie frame, motor cradle, cowl rings, articulation adapters | `FabricatedPart` records plus CAD templates |
| Subassemblies | Integration units that can be inspected | car module, powered bogie, trailer bogie, cowl, articulation, roof services | `Subassembly` records plus FreeCAD review groups |
| Final assemblies | Released trainset configurations | promoted light-metro 3-car trainset | `FinalAssembly` records plus generated CAD/FEM/BOM |

## Automated iteration

The first implementation is deterministic and dependency-free:

```bash
scripts/design-iterate.sh
```

It exhausts the declared discrete design space for the default
`light-metro-3car` family, evaluates every candidate, and writes:

- `mechanical-py/catalog/design-system/design-iteration.json`
- `mechanical-py/catalog/design-system/design-iteration-summary.md`

To turn the winning candidate into a buildable product tree and review
the current CAD/BOM baseline against it:

```bash
scripts/buildable-trainset.sh
```

That writes the buildable manifest and buildability review under
`mechanical-py/catalog/buildable-trainset/`.

To run a bounded exploratory pass:

```bash
scripts/design-iterate.sh --family metro-4car --max-iterations 250
```

The current scorecard is intentionally planning-grade. It is good enough
to rank candidate architecture choices before spending FreeCAD/FEM time,
but it is not a certification result. As the project matures, replace
or augment the simple metrics with:

- FreeCAD-derived mass properties and package clearances;
- CalculiX margins from `scripts/freecad-generate.sh --fem`;
- supplier quotations and evidence status;
- lifecycle energy and maintenance models;
- risk penalties from the hazard log and compliance matrix.

## Promotion loop

Use the generated best candidate as a design review input, then run:

```bash
scripts/freecad-generate.sh --models --assemblies --fem
scripts/freecad-generate.sh --screenshots --station-scenes
```

If CAD/FEM/supplier evidence rejects the candidate, update the component
catalogue or constraints in `osr_mech.design_definition`, rerun
`scripts/design-iterate.sh`, and promote the next best feasible
candidate. That is the closed loop: requirements drive definitions,
definitions drive CAD/FEM, evidence updates definitions.
