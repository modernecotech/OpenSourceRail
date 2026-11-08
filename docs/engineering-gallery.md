# CAD and FEM image gallery

The front-page gallery uses actual source geometry and native numerical output. The [manifest](assets/engineering-gallery-v06/manifest.json) records each physical candidate, input/evaluation identity, source SHA-256, rendering recipe, output SHA-256 and display transformation. It is a collection of separate research designs, not a selected whole-system assembly.

| View | Geometry and interpretation |
|---|---|
| [Vehicle cutaway](assets/engineering-gallery-v06/vehicle-car0.webp) | Located one-car stock/fitout from the [bogie-detail research body](design-engine/reconciled-pilot-bogie-detail/README.md). Blender renders existing source meshes; roof, high equipment and near-side wall omissions are recorded. Equipment envelopes are not finished supplier geometry. |
| [Bogie cradle](assets/engineering-gallery-v06/bogie-cradle.webp) | SolidCraft snapshot of the [34-solid stock subset](design-engine/powered-bogie-detail/README.md). No invented motor/gearbox housings. Complete bogie fit is held. |
| [Launch shuttle](assets/engineering-gallery-v06/launch-assembly.webp) and [clevis](assets/engineering-gallery-v06/launch-clevis.webp) | SolidCraft snapshots of the [122-region assembly](design-engine/launch-detail/README.md). Transparent/ghosted guards and surrounding stock expose real bores, pin, retainers and hollow members; the geometry itself is unchanged. |
| [Civil assembly](assets/engineering-gallery-v06/civil-assembly.webp) | Source-defined 265-entity two-track segment, rail, bearing, pier and footing proposal. Rendering this assembly does not analyse its joints, reinforcement or supports. |
| [Civil FEM](assets/engineering-gallery-v06/civil-fem.webp) | FieldCraft 0.7.5 full displacement field on the separate continuous gross elastic beam under the retained normal-base load. 22,680 tetra10 elements and 43,340 nodes. Each exterior quadratic face is split through its actual midside nodes; triangle colours average the native nodal displacement magnitudes. Deformation is exaggerated 100×; the legend is in millimetres. |

The FEM replay retained the exact binary mesh and reproduced the earlier **13.9476148427 mm** downward midspan vertical displacement (native Uᶻ = −0.0139476148427 m). Maximum displacement magnitude is **14.1132971464 mm**, which also includes horizontal movement. The coordinate exchange allows only the documented ten-decimal ASCII rounding, bounded by 5.1×10⁻¹¹ m; it does not change an engineering tolerance. The original rejected postprocessing attempt is preserved beside the corrected result.

This is a homogeneous elastic concrete model with ideal bearing lines. Cracking, prestress, segment joints, fatigue, contact, erection and physical qualification remain unresolved. The located assembly image must not inherit this continuous-beam result. Geometry agreement and numerical convergence do not grant manufacturing or operating approval.

## Inspect and reproduce

The packet includes original CAD PNGs, exact recipes/cameras/styles, native execution receipts, the full native VTU export compressed losslessly, the original mesh, a compact nodal field and figure metadata. The larger results-embedded FieldCraft project remains retained in the original private execution package; the public VTU is sufficient to regenerate the figure without solving again.

The vehicle’s complete 3000×1900 PNG was saved before the supervisor stopped the run at its 600-second limit; its worker reports 603.36 seconds. The saved image and unchanged geometry were independently inspected, but the **execution remains held**. The result writer then failed on an empty supervisor-usage file; that failure is retained. In-worker peak RSS was 3.86 GiB for the vehicle and 3.67 GiB for the completed civil render, exceeding their 3 GiB observed targets during final rendering. Supervisor usage for the held run remains unknown. The gallery records these resource misses instead of claiming successful bounded execution or repeating the renders merely to obtain a passing receipt.

From the repository root:

```bash
.venv/bin/python -m tools.engineering_gallery.publication verify
.venv/bin/python -m tools.engineering_gallery.publication replot docs/assets/engineering-gallery-v06 /tmp/osr-civil-field.png
```

The second command reconstructs the existing full-field figure; it does not start a solver. Use a fresh output filename. To rerender an eligible CAD view with the pinned SolidCraft or installed Blender backend, record a fresh private run:

```bash
.venv/bin/python -m tools.engineering_gallery.cad launch-assembly --output /tmp/osr-launch-render
```

Native SolidCraft camera targets/distances are explicitly in millimetres and camera angles in radians; source assembly geometry uses metres. Native CAD runs use the recorded read-only/network-isolated wrapper and CPU/address-space limits. Blender receipts report in-worker memory separately from the Flatpak supervisor and use four rendering threads; they are observed resource records, not an aggregate OS memory sandbox. The coordinator itself has unrestricted workspace access. Render-only colours, cameras and omissions do not change CAD, mass, selection or acceptance.
