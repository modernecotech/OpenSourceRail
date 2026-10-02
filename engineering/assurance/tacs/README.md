# Distributed-control process reference

[RFC 0033](../../../docs/rfcs/0033-tacs-runtime-and-resource-control.md) is the
proposed development target. Existing `osr-consensus`, `osr-interlocking`, ATP,
ATO and brake components supply the decisions; `osr-runtime` supplies thin
hosts. The earlier separate `osr-tacs` engine is retired.

Two train processes, three static voters, one point interface and two station
interfaces exchange authenticated messages through bounded asynchronous queues.
Each decision/communications process has a filesystem journal. Two additional
output processes independently enforce the brake deadline/latch contract;
qualified hardware independence remains pending. The harness provides synthetic local
physics/proving inputs without supplying global truth to onboard authority.
The physics fixture rejects unsupported geometry/formation/braking bundles
before startup and checks moving footprints against retained protection.
Positions use measured speed and non-zero bounded uncertainty. Platform locks
remain owned at arrival. Process restart uses SIGKILL and the same journal.

```sh
cargo test -p osr-runtime -p osr-consensus -p osr-interlocking
python3 tools/automation/tacs_reference.py --output /tmp/reference.json
python3 tools/automation/tacs_assurance.py --check
python3 tools/automation/tacs_assurance.py --verify-replay

# Explicit new development bundle and actual execution evidence
python3 tools/automation/tacs_assurance.py --generate-deployment --run-twin
python3 tools/automation/tacs_assurance.py --run-formal build/toolchain/tla/tla2tools-1.8.0.jar
python3 tools/automation/tacs_cost.py engineering/assurance/tacs/cost-model.json
```

[report.md](report.md) and raw execution records contain unreviewed software
results. [assurance.json](assurance.json) uses the shared hierarchical FMEA and
change-impact compiler. Source changes invalidate recorded execution and frozen
configuration applicability; compilation does not create passing run evidence
or independent acceptance. Reference keys are publicly reproducible test keys.
PIDs differ on replay; all semantic results and traces must match.

Designed, installed and approved configuration states are distinct. This
bundle is synthetic and not installed; operational activation is rejected.
Storage compaction retains the full Raft log. Torn storage inhibits startup;
physical power loss/flash behavior remains to qualify. The formal resource
model checks two trains, two resources and two epochs under qualified
clearance/no-reentry assumptions; batching and filesystem/runtime refinement
remain independent-review work. No complete safety proof is claimed.

HIL must establish independent safe outputs/deadlines, sensor/integrity/points,
clock and radio bounds, per-car charging/doors/PSD/BMS/traction integration,
real braking/adhesion and storage power-loss behavior. Closed-track recovery,
independent assessment and named G0–G4/profile-release decisions follow. Depot,
rescue, turnback, following trajectories, arbitrary topology and large fleets
are protected/unimplemented service extensions, not passed operating cases.

[cost-model.json](cost-model.json) records equipment and lifecycle inputs for
equivalent service/availability. Missing values remain unknown; no equipment
removal, percentage saving or city-cost reduction is approved.
