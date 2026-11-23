# FreeCAD CAM trial on the wax coupon

FreeCAD 1.1.4 created a native CAM Job, 3 mm end-mill Tool Controller, explicit 60 × 40 × 8 mm stock and linked Engrave operation from the released L-slot coupon. The headless Python session kept the same document and operation through both edits. It recomputed the path, generated a GRBL preview with G54 and replayed the preview in FreeCAD's voxel stock simulator. [Released coupon and setup](../prototype/cam/CAM.md) · [FreeCAD CAM Job](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/CAM_Job.md) · [FreeCAD Engrave operation](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/CAM_Engrave.md)

| Native operation | Slot at X25 | Remaining floor | Exact removal | Voxel removal at 0.25 mm |
|---|---:|---:|---:|---:|
| Released L shape, end Y28 | 3 × 1 mm | 7 mm | 138.59 mm³ | 150.19 mm³ |
| Linked centreline edit, end Y30 | 3 × 1 mm | 7 mm | 144.59 mm³ | 156.69 mm³ |
| Independent final-depth edit to −1.5 mm | 3 × 1.5 mm | 6.5 mm | 216.88 mm³ | 235.03 mm³ |

The geometry edit regenerated both Y30 endpoints. The depth edit introduced a third pass at −1.5 mm. Restoring the depth regenerated the earlier Y30 GRBL preview byte for byte. Exact cutter sweeps agree with the target solids constructed directly from the drawing dimensions. The voxel meshes overstate removed volume by about 8.4% at the chosen pitch. The comparison uses the exact sweep for dimensional inspection and the native voxel mesh as a separate removal check. [Machine-readable receipt](freecad_interactive.json)

A rectangular test obstacle at X35–40, Y10–14, Z−2 to +3 crosses the first leg. The native operation/post still generated the same program. The script's solid-intersection check identified two cutter contacts of 52.5 and 60.0 mm³ and blocked the fixture trial. FreeCAD's Job Fixtures field specifies work coordinate systems such as G54. The script supplies the physical jaw and obstacle solids explicitly and checks both cutter and holder. The test covers this coupon's linear XY cuts, axial entry and fixed tool geometry. A released job needs the actual workholding and machine model.

## Reproduce

Run from the repository root with FreeCAD 1.1.4 Flatpak. With no arguments, the script reruns the trial and compares its result with the retained receipt. The optional output directory also receives the live FreeCAD document, direct-design STEP references and preview text.

```bash
flatpak run --command=sh org.freecad.FreeCAD -c 'PYTHONPATH=/app/freecad/lib:/app/freecad/Mod/CAM python3 cities/Baghdad/engineering/simulation/freecad_interactive.py --out build/freecad-interactive'
```

The trial used FreeCAD's native application libraries without launching its graphical interface. The document, target solids, GRBL previews and fixture checks are digital evidence. Machine control and physical coupon acceptance are open.
