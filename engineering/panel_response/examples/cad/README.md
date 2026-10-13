# Native refined panel arrangements

[Verification](verification.json) checks occupied material, nonoverlap, reopened native identities and STEP volumes against the shared contracts.

| Arrangement | FreeCAD | STEP |
|---|---|---|
| Baseline 1.0 m supports | [baseline.FCStd](baseline.FCStd) | [baseline.step](baseline.step) |
| 0.5 m supports | [closer-supports.FCStd](closer-supports.FCStd) | [closer-supports.step](closer-supports.step) |
| 0.33 m supports | [dense-supports.FCStd](dense-supports.FCStd) | [dense-supports.step](dense-supports.step) |
| 0.2 m supports | [tight-supports.FCStd](tight-supports.FCStd) | [tight-supports.step](tight-supports.step) |
| 40 mm deeper rails | [deeper-rails.FCStd](deeper-rails.FCStd) | [deeper-rails.step](deeper-rails.step) |

Material/part identities and ply schedules are stored in each native document. All physical/manufacturing-release flags remain false. Proposed contact and frame/weld details require further engineering.
