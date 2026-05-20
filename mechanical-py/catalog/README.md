# Generated STEP Catalogue

This directory contains generated STEP artifacts from `mechanical-py`.
The authoritative designs are the build123d source files under
[`../src/osr_mech/`](../src/osr_mech/). Do not hand-edit the STEP
files; update the source and regenerate the catalogue.

## Regenerate

```bash
PYTHONPATH=mechanical-py/src python3 -m osr_mech.catalog --out mechanical-py/catalog
```

## Sections

| Folder | Scope |
|---|---|
| [`rolling_stock/`](rolling_stock/) | Trainsets, layered car-body subassemblies, bogies, batteries, doors, platform safety interfaces, couplers, electronics, sensor packs |
| [`bogie/`](bogie/) | Bogie frame, wheelset, suspension, brakes, PMSM motor, gearbox |
| [`track/`](track/) | Rails, sleepers, fasteners, panels, turnouts |
| [`civil/`](civil/) | U-girders and platform edge units |
| [`station/`](station/) | Platform, canopy, portal, solar-roof, and tactile-path parts |
| [`depot/`](depot/) | Depot archetype envelopes |
| [`fixtures/`](fixtures/) | Supplier-neutral COTS fixture envelopes |
