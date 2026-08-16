# FEA Screening Outputs

This folder contains generated FreeCAD/CalculiX first-pass screening
artifacts. The Python source under `../../src/osr_mech/freecad_fea.py`
defines the beam models, loads, supports, result parsing, and FreeCAD
visual document generation.
Each regeneration clears the old solver output folders and summaries
first, then rewrites the stable latest paths documented below.
Each study folder also includes a solver-derived `*-result.png` plot:
deformed beam shape, support/load markers, and CalculiX von Mises
stress colour scale parsed from the `.dat` output.

## Outputs

| Path | Purpose |
|---|---|
| [`screening-summary.md`](screening-summary.md) | Human-readable result summary |
| [`screening-summary.json`](screening-summary.json) | Machine-readable result summary |
| [`dependency-check.json`](dependency-check.json) | FreeCAD/FEM/CalculiX/gmsh availability captured at generation time |
| [`chassis-bogie-screen/`](chassis-bogie-screen/) | Low-floor chassis supported at bogie connectors: `.inp`, `.dat`, `.frd`, `.sta`, `.cvg`, `.12d`, and solver log |
| [`chassis-aw3-proof-screen/`](chassis-aw3-proof-screen/) | 1.5 x vertical AW3 proof-load screen for the low-floor chassis |
| [`chassis-track-twist-screen/`](chassis-track-twist-screen/) | Asymmetric track-twist / uneven-load chassis screen |
| [`bogie-frame-screen/`](bogie-frame-screen/) | Motor/trailer bogie H-frame screening model raw CalculiX inputs and outputs |
| [`bogie-brake-traction-screen/`](bogie-brake-traction-screen/) | Bogie vertical plus longitudinal brake/traction reaction screen |
| [`full-body-frame-screen/`](full-body-frame-screen/) | Full car body side/roof frame screening model raw CalculiX inputs and outputs |
| [`full-body-lateral-sway-screen/`](full-body-lateral-sway-screen/) | Full body side-frame lateral sway/racking screen |
| [`train-to-train-joint-vertical-screen/`](train-to-train-joint-vertical-screen/) | Local open train-to-train joint vertical passenger/gangway load screen |
| [`train-to-train-joint-lateral-sway-screen/`](train-to-train-joint-lateral-sway-screen/) | Local open train-to-train joint lateral/racking load screen |

## Raw File Index

Every study folder contains the same generated file set:
`{slug}.inp`, `{slug}.dat`, `{slug}.frd`, `{slug}.sta`, `{slug}.cvg`,
`{slug}.12d`, `{slug}.ccx.log`, and
`{slug}-result.png`.

| Study | Result PNG |
|---|---|
| Chassis service gravity | [`chassis-bogie-screen-result.png`](chassis-bogie-screen/chassis-bogie-screen-result.png) |
| Chassis AW3 proof | [`chassis-aw3-proof-screen-result.png`](chassis-aw3-proof-screen/chassis-aw3-proof-screen-result.png) |
| Chassis track twist | [`chassis-track-twist-screen-result.png`](chassis-track-twist-screen/chassis-track-twist-screen-result.png) |
| Bogie vertical | [`bogie-frame-screen-result.png`](bogie-frame-screen/bogie-frame-screen-result.png) |
| Bogie brake/traction | [`bogie-brake-traction-screen-result.png`](bogie-brake-traction-screen/bogie-brake-traction-screen-result.png) |
| Full body vertical | [`full-body-frame-screen-result.png`](full-body-frame-screen/full-body-frame-screen-result.png) |
| Full body lateral sway | [`full-body-lateral-sway-screen-result.png`](full-body-lateral-sway-screen/full-body-lateral-sway-screen-result.png) |
| Train-to-train joint vertical | [`train-to-train-joint-vertical-screen-result.png`](train-to-train-joint-vertical-screen/train-to-train-joint-vertical-screen-result.png) |
| Train-to-train joint lateral sway | [`train-to-train-joint-lateral-sway-screen-result.png`](train-to-train-joint-lateral-sway-screen/train-to-train-joint-lateral-sway-screen-result.png) |

Regenerate from the repository root with:

```bash
scripts/freecad-generate.sh --fem --screenshots
```

Or regenerate from `mechanical-py/` with the lower-level launchers:

```bash
scripts/freecad_fea.sh
scripts/freecad_screenshots.sh
```

The FreeCAD visual document is
[`../freecad/fea-screening-models.FCStd`](../freecad/fea-screening-models.FCStd),
and the rendered review screenshots are embedded in
[`docs/rolling-stock/light-metro-3car/README.md`](../../../docs/rolling-stock/light-metro-3car/README.md#freecad-assembly-and-fea-screenshot-review).
