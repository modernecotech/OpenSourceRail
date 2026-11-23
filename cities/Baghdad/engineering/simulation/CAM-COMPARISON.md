# CamCraft and FreeCAD on the Airport wax coupon

**Use CamCraft as an optional interactive CAM tool for an agent, and retain FreeCAD as the Airport drawing and solid-geometry reference.** CamCraft's headless server let the agent inspect job state, edit operations, regenerate, simulate and obtain a named refusal from the Grbl post when a fixture obstructed the cutter. FreeCAD maintained the stronger link from the edited drawing to the toolpath for this coupon. The released Airport fabrication and pricing scope keeps its existing identity.

The comparison used CamCraft v0.25.0, Apache-2.0, and FreeCAD 1.1.4 from the LGPL-2.1 Flatpak. The portable CamCraft Linux archive was checked against the publisher's SHA-256 before execution. The MCP server identified itself as 0.25.0 and exposed 117 tools. The FreeCAD trial used its native Job, Tool Controller, Engrave operation, post, voxel simulator and solid kernel from a Python session. Both sessions ran locally and wrote preview files under the ignored build directory. [CamCraft release and assets](https://github.com/NeoTech/Camcraft/releases/tag/v0.25.0) · [Pinned agent interface](https://github.com/NeoTech/Camcraft/blob/7e2a8119c8aec2140135cadbc6afc7922aee955a/docs/agents/mcp-tools.md) · [FreeCAD trial](FREECAD-INTERACTIVE.md)

## Results on the same drawing

The 60 × 40 × 8 mm wax blank has a 3 mm wide L slot, two depths of 0.5 and 1.0 mm, and a finished 7 mm floor. Both systems used the same end mill, 6,000 rpm, 180 mm/min cutting and 60 mm/min plunge. The edited design extends the second leg from Y28 to Y30. Independent STEP references came from the drawing dimensions. The explicit kinematic test uses a fixed vertical cutter and holder, plus two jaw solids. [Released drawing and setup](../prototype/cam/CAM.md)

| Trial | CamCraft MCP | FreeCAD CAM |
|---|---|---|
| Author the centreline | Read the open DXF, identified its two primitives and one chain. Trace generation refused this DXF source. Two explicit Slot operations on the STEP part generated the same slot, with a retract between legs. | One Engrave operation followed the linked two-leg wire in a native document. |
| Extend second leg 2 mm | Reimporting only the STEP left 6.047 mm³ of stock on the simulation and allowed the old program to post. Editing the second Slot's endpoint marked it stale. Regeneration cleared the residual. | Editing the wire propagated to both depth passes on recompute. Exact removal rose from 138.586 to 144.586 mm³. The 0.25 mm voxel result rose from 150.188 to 156.688 mm³. |
| Increase depth | Against the unchanged −1 mm drawing, deepening only the second Slot to −1.5 mm produced 30.516 mm³ of gouge. The worst overcut was 0.50 mm. The verifier refused to post. Restoring depth reproduced the previous preview digest. | A separate design-depth control produced three passes and a 6.5 mm floor, verified by independent solid section and cutter sweep. |
| Add a physical obstruction | The simulation's material image still read clean. The fixture check found two flute strikes, at moves 3 and 8. The native post refused and wrote zero files for this trial. | The native post still generated its preview. The caller's swept-solid check found 52.5 and 60.0 mm³ cutter overlap at the two depths and blocked release. |
| Inspect the result | The stock renderer checked 68,160 cells at 0.1875 mm pitch. The baseline and corrected edit had zero reported rest or gouge in this discrete model. The previews contained all six expected feed endpoints at G54. | Exact BRep comparison against the dimensioned design found no difference in the two fitted shapes. FreeCAD retains the editable parametric document and the exported STEP models. |

The obstruction occupies X35–40, Y10–14 and Z−2 to +3 mm. The tools agreed on contact, and their automation treated it differently. CamCraft's native fixture refusal is valuable for agent-driven retries. Its successful post after the target-only edit shows why an automated client must read the remaining-stock result and compare the output with the requested geometry. An agent using the two-Slot workaround must update the authored coordinates after design changes. These tests cover a fixed-axis coupon and one machine/post pair. They supply no production post approval or validation of bogie workholding.

The CamCraft run took **1.71 s** for 57 MCP tool calls, including the DXF control, seven generation/verification cycles and local preview writes. A separate fresh invocation of the complete FreeCAD trial took **5.45 s** including Flatpak launch, exact BRep operations, voxel runs and the independent dimensional tests. The two scripts perform different amounts of geometric work. These times describe this machine and trial. [CamCraft numerical receipt](cam_compare_results.json) · [FreeCAD numerical receipt](freecad_interactive.json)

## Reproduce

Use a fresh output directory. The [CamCraft comparison driver](cam_compare.py) records the full request/reply transcript, elapsed times by tool, named refusals, material renderings, the project, digital previews and a compact result. Its assertions cover the target-only residual, depth and fixture refusals, endpoint propagation and restored output digest.

1. Download the official `camcraft-0.25.0-linux-x86_64.tar.gz` asset to an ignored build directory. Verify SHA-256 `4dc0269e27a39525346a219db42e6f3a0e213ce3af5b9f15d2736c23ddd14cdf` and extract it. The tested installation used the shared filesystem reservation mechanism with a 512 MiB allowance, ongoing free-space monitoring and the project's 20 GiB floor. The input asset was 62,505,156 bytes. No system package or source build was needed.
2. Generate the baseline and edited STEP files from the installed FreeCAD application. The command below also replays its native CAM checks.
3. Run the CamCraft comparison with the binary and STEP directory from those steps. Replace the binary path if the release was extracted elsewhere.

```sh
flatpak run --command=sh org.freecad.FreeCAD -c 'PYTHONPATH=/app/freecad/lib:/app/freecad/Mod/CAM python3 cities/Baghdad/engineering/simulation/freecad_interactive.py --out build/coupon-reference'
python3 -m cities.Baghdad.engineering.simulation.cam_compare \
  build/camcraft-0.25.0-linux-x86_64/camcraft-cli \
  build/coupon-camcraft-replay build/coupon-reference
```

The release commit is `7e2a8119c8aec2140135cadbc6afc7922aee955a`. Both tool installations remain local to the development machine. Tool binaries are excluded from the railway deliverable. [CamCraft licence](https://github.com/NeoTech/Camcraft/blob/7e2a8119c8aec2140135cadbc6afc7922aee955a/LICENSE) · [Grbl 1.1 post source](https://github.com/NeoTech/Camcraft/blob/7e2a8119c8aec2140135cadbc6afc7922aee955a/assets/posts/grbl.cps)
