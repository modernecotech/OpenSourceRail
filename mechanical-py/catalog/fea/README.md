# FEA Screening Outputs

This folder contains generated FreeCAD/CalculiX first-pass screening
artifacts. The Python source under `../../src/osr_mech/freecad_fea.py`
defines the beam models, loads, supports, result parsing, and FreeCAD
visual document generation.
Each regeneration clears the old solver output folders and summaries
first, then rewrites the stable latest paths documented below.

## Outputs

| Path | Purpose |
|---|---|
| [`screening-summary.md`](screening-summary.md) | Human-readable result summary |
| [`screening-summary.json`](screening-summary.json) | Machine-readable result summary |
| [`dependency-check.json`](dependency-check.json) | FreeCAD/FEM/CalculiX/gmsh availability captured at generation time |
| [`chassis-bogie-screen/`](chassis-bogie-screen/) | Low-floor chassis supported at bogie connectors: `.inp`, `.dat`, `.frd`, `.sta`, `.cvg`, `.12d`, and solver log |
| [`bogie-frame-screen/`](bogie-frame-screen/) | Motor/trailer bogie H-frame screening model raw CalculiX inputs and outputs |
| [`full-body-frame-screen/`](full-body-frame-screen/) | Full car body side/roof frame screening model raw CalculiX inputs and outputs |

## Raw File Index

| Study | Files |
|---|---|
| Chassis/bogie | [`chassis-bogie-screen.inp`](chassis-bogie-screen/chassis-bogie-screen.inp), [`chassis-bogie-screen.dat`](chassis-bogie-screen/chassis-bogie-screen.dat), [`chassis-bogie-screen.frd`](chassis-bogie-screen/chassis-bogie-screen.frd), [`chassis-bogie-screen.sta`](chassis-bogie-screen/chassis-bogie-screen.sta), [`chassis-bogie-screen.cvg`](chassis-bogie-screen/chassis-bogie-screen.cvg), [`chassis-bogie-screen.12d`](chassis-bogie-screen/chassis-bogie-screen.12d), [`chassis-bogie-screen.ccx.log`](chassis-bogie-screen/chassis-bogie-screen.ccx.log), [`spooles.out`](chassis-bogie-screen/spooles.out) |
| Bogie frame | [`bogie-frame-screen.inp`](bogie-frame-screen/bogie-frame-screen.inp), [`bogie-frame-screen.dat`](bogie-frame-screen/bogie-frame-screen.dat), [`bogie-frame-screen.frd`](bogie-frame-screen/bogie-frame-screen.frd), [`bogie-frame-screen.sta`](bogie-frame-screen/bogie-frame-screen.sta), [`bogie-frame-screen.cvg`](bogie-frame-screen/bogie-frame-screen.cvg), [`bogie-frame-screen.12d`](bogie-frame-screen/bogie-frame-screen.12d), [`bogie-frame-screen.ccx.log`](bogie-frame-screen/bogie-frame-screen.ccx.log), [`spooles.out`](bogie-frame-screen/spooles.out) |
| Full body frame | [`full-body-frame-screen.inp`](full-body-frame-screen/full-body-frame-screen.inp), [`full-body-frame-screen.dat`](full-body-frame-screen/full-body-frame-screen.dat), [`full-body-frame-screen.frd`](full-body-frame-screen/full-body-frame-screen.frd), [`full-body-frame-screen.sta`](full-body-frame-screen/full-body-frame-screen.sta), [`full-body-frame-screen.cvg`](full-body-frame-screen/full-body-frame-screen.cvg), [`full-body-frame-screen.12d`](full-body-frame-screen/full-body-frame-screen.12d), [`full-body-frame-screen.ccx.log`](full-body-frame-screen/full-body-frame-screen.ccx.log), [`spooles.out`](full-body-frame-screen/spooles.out) |

Regenerate from `mechanical-py/` with:

```bash
scripts/freecad_fea.sh
scripts/freecad_screenshots.sh
```

The FreeCAD visual document is
[`../freecad/fea-screening-models.FCStd`](../freecad/fea-screening-models.FCStd),
and the rendered review screenshots are embedded in
[`docs/rolling-stock/light-metro-3car/README.md`](../../../docs/rolling-stock/light-metro-3car/README.md#freecad-assembly-and-fea-screenshot-review).
