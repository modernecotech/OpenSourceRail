# Door motion coordinate correction — current installation model

This packet records a coordinate correction in the generated six-car
installation plan. The proposed door leaves are placed and swept along the
vehicle's longitudinal **X** axis; each joint also declares `axis=[1,0,0]`.
The earlier result encoded the same ±0.72 m stroke along **Y**, even though the
open positions and swept bounds were calculated along X. The generator now
stores a three-component global translation consistent with the declared
axis, and records the resulting open centre explicitly.

## Candidate identity and scope

- Source body candidate: `907da3680bcbd01ffe1223652443e4e34a9f581e201385917a99edf4150bd90a`
- Generated installation candidate: `17ce7a724fcd661e5c4f195cde19b68377c0968e4e7d7dbb5d6ac7c8d4074ad4`
- Installation evaluation: `037627d412bbda73ccf4149fbedb36ecd865c57652fcad8020d04bb606c716fb`
- Output manifest: [`manifest.json`](manifest.json), manifest identity
  `6a3e3d9fd394f8d0f47c603b5d661e1c5724d665996be0296e56b6d429b0c004`

This is a new installation evaluation derived from the current `907da…`
vehicle-parts bundle. It is **not** the separate `9f6d…` compact-drive body or
the older 668-part delivery proposal. Its BOM, installation estimate, axle
loads and static GLB preview were freshly regenerated from the `907da…`
source bundle; no cost, FEM, city or delivery result from `9f6d…` is inherited.

The regenerated model has 605 source component types, 9,342 occurrence
patterns and 116,128 listed occurrences. Its 24 door leaves now carry
`closed_center_m`, `open_center_m`, `travel_m` in global XYZ and a swept box
derived from the endpoints. The declared slide remains 0.72 m per leaf; the
model's 20 mm header margin is a hypothesis, not a clearance acceptance.

## Limits

This is a geometric consistency check of the proposed joint record, not a
kinematic CAD assembly or a collision-free door design. The door leaves remain
envelope geometry. Rail/carriage positions, belt and pulley path, tolerance
stack, end stops, seals, obstacle detection, force limits, emergency release,
door interlock, platform gap, fire performance, inspection and maintenance
access remain unresolved. The generated GLB is an OSR static preview, not a
SolidCraft model. No native CAD or FEM solver was run. Physical, engineering,
manufacturing, operating and movement-authority flags remain false.

The 9f6d candidate-specific service and door audits remain valid for their
own candidate. This packet does not revise those archived identities; it
shows a separate correction in the current `907da…` installation generator.

## Reproduction and execution boundary

From the repository root, generate into a fresh private directory:

```bash
tools/automation/osr-python -m engineering.vehicle_installation \
  --output /path/to/fresh-installation-run
```

Then inspect the generated `installation.json.gz` and confirm every door row
has an X-only translation matching its closed-to-open centre displacement.
The focused regression command was:

```bash
tools/automation/osr-python -m pytest -q tests/test_vehicle_installation.py
```

Result: **15 passed**. The generated run took 12.91 s application time (13.05 s
wall time), with 141,404 KiB maximum RSS. The run had a 120 s timeout. The
first attempted invocation failed because its caller pre-created the required
fresh output directory; that execution log is retained in
[`execution-logs/attempts.stderr.log`](execution-logs/attempts.stderr.log).
The successful retry used a new child directory. The execution environment
provided no OS-enforced source sandbox; source and payload hashes are recorded
in the manifest and [`execution.json`](execution.json).

The corrected source was also replayed from an isolated sparse Git worktree at
the exact prior generator commit `2af9058b372fdc3e4f26e45d41f7615e796d0381`,
with only the same vector correction applied. Its generator source hashes,
candidate ID, evaluation ID, and every output-file hash matched the current
worktree run byte-for-byte. The replay manifest is
`fc8fc75c39191fb578de810e6270cd296409de23c4baa96959d34bb855058589`; its
manifest ID differs because the run records its own output location.
