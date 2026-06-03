# Generated STEP Catalogue

This directory contains generated STEP artifacts from `mechanical-py`.
The authoritative designs are the build123d source files under
[`../src/osr_mech/`](../src/osr_mech/). Do not hand-edit the STEP
files; update the source and regenerate the catalogue. Regeneration
refreshes the generated STEP folders before writing so this directory
represents the latest canonical artifact set.

## Regenerate

```bash
PYTHONPATH=mechanical-py/src python3 -m osr_mech.catalog --out mechanical-py/catalog
```

## Sections

| Folder | Scope |
|---|---|
| [`rolling_stock/`](rolling_stock/) | Trainsets, layered car-body subassemblies, bogies, batteries, doors, platform safety interfaces, couplers, electronics, sensor packs, and mechanical interface packages |
| [`rolling_stock/interfaces/`](rolling_stock/interfaces/) | Bogie, chassis, body, roof, window, door, floor, battery, bench, lighting, HVAC, screen/speaker, LIDAR, and train-connector installation hardware |
| [`bogie/`](bogie/) | Bogie frame, wheelset, suspension, brakes, PMSM motor, gearbox |
| [`track/`](track/) | Rails, sleepers, fasteners, panels, turnouts |
| [`civil/`](civil/) | U-girders and platform edge units |
| [`station/`](station/) | Platform, canopy, portal, solar-roof, and tactile-path parts |
| [`depot/`](depot/) | Depot archetype envelopes |
| [`fixtures/`](fixtures/) | Supplier-neutral COTS fixture envelopes |
| [`freecad/`](freecad/) | FreeCAD review assemblies generated from the STEP catalogue, including assembled/exploded state documents |
| [`fea/`](fea/) | FreeCAD/CalculiX first-pass beam-model screening inputs, solver outputs, and result summaries |
