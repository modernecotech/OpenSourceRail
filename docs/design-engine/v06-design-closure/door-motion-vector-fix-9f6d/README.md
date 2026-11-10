# 9f6d door-motion coordinate correction

This packet is a regenerated, source-bound evaluation of the existing `extended-cradle-3240` research candidate. It corrects the coordinate representation inherited by its door-motion records. It does not alter the frozen parent or select a new physical configuration.

## Candidate and evaluation identities

| Record | Before | Regenerated |
| --- | --- | --- |
| Frozen input parent | `b7cac242…` / `efa0e704…` | unchanged |
| Underframe parent | `c89556f4…` / `cf732dd…` | `c89556f4…` / `59943e9e…` |
| Powered-bogie body | `9f6d2230…` / `dfb48ca3…` | `9f6d2230…` / `a7a9ee09…` |
| Powered-bogie run manifest evaluation | — | `75ad184b…` |

The physical candidate IDs remain the same. The revised evaluation IDs record the corrected motion records and their new ancestry. The old body receipt is preserved at `docs/design-engine/powered-bogie-detail/body.json.gz`; it was not edited.

## Correction

The 24 door leaves already declared a vehicle-global X prismatic axis and X swept envelopes, but their inherited `travel_m` stored only `[0, ±0.72]`. The regenerated child plans now store `motion_vector_frame: vehicle-global-xyz`, `travel_m: [±0.72, 0, 0]`, and `open_center_m = closed_center_m + travel_m`. Existing swept-box X bounds are retained and checked to contain the motion path. The copied frozen parent is unchanged.

This is an evaluation-data consistency correction. It is not a kinematic CAD model, measured door operation, collision-free assembly, accessibility or entrapment verification, supplier fit, manufacturing release, or passenger-safety acceptance. The powered-bogie geometry screen remains **HOLD** for required-space conflicts and unverified supplier interfaces.

## Reproduction and evidence

Source commit: `966746d7148011ceb949f716419ea4ef4a23546c`.

Command, with a new output path that did not previously exist:

```bash
tools/automation/osr-python -m engineering.powered_bogie.run /home/hayder/.local/state/opensourcerail/runs/door-motion-9f6d-971d-run-01
```

The run completed in 41.653 seconds of reported application wall time. It generated the two declared policy variants and a presentation GLB preview; `--cad` was not used. No native CAD, FEM, GIS or external solver ran. The run reports source hashes unchanged before and after (22 source entries); the exact request, source body, variants, outputs, summary and file-hash manifest are retained under [`run/`](run/).

The focused test command was:

```bash
tools/automation/osr-python -m pytest -q tests/test_vehicle_installation_underframe.py --tb=short
```

Result: **14 passed**. The new regression checks the untouched frozen-parent vector, corrected child vectors and centers, swept X bounds, unchanged c895 and 9f6d candidate identities, changed evaluation ancestry, and false physical/release flags.

The source ran in a sparse isolated Git worktree and a private output directory; filesystem access was not OS-enforced read-only. Peak memory was not measured. The run manifest and source-bound checks are software evidence only. Engineering, physical, supplier-fit, manufacturing and operating acceptance remain false.
