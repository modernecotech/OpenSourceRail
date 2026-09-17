# Evidence register

Complete inventory of verification evidence produced by the
OpenSourceRail project, indexed to the safety requirements from
[safety-requirements.md](safety-requirements.md) and the hazards
from [hazard-log.md](hazard-log.md).

## 1. Formal-methods evidence (Kani bounded-model checking)

Each SIL-4 evaluator carries Kani harnesses under
`crates/<name>/src/kani_proofs.rs`, gated on `cfg(kani)` so `cargo
test` skips them and `cargo kani` runs them. These are written proof harnesses. A successful Kani run can establish the
stated property within its recorded bounds; the presence of a harness or a
passing `cargo test` run does not establish that result.

| Crate | Harness module | Properties | SR coverage |
|---|---|---|---|
| `osr-atp` | `kani_proofs.rs` | A1–A7 | SR-01, SR-02, SR-03 |
| `osr-brake` | `kani_proofs.rs` | B1–B5 | SR-15 |
| `osr-odometry` | `kani_proofs.rs` | O1–O5 | SR-10 |
| `osr-wayside-points` | `kani_proofs.rs` | W1–W6 | SR-01, H-CO-02 |
| `osr-interlocking` | `kani_proofs.rs` | P1–P5 | SR-01, SR-02, H-CO-01, H-CO-04 |
| `osr-obstacle-detect` | `kani_proofs.rs` | O1–O5 | SR-04, SR-05, SR-06 |
| `osr-intrusion-detect` | `kani_proofs.rs` | I1–I5 | SR-07, H-CO-03, H-SA-01 |
| `osr-secbus` | `kani_proofs.rs` | S1, S3 | SR-22, H-DI-01 |

**Inventory:** named-property harnesses across the eight evaluators above.
Harnesses written, runs passed, results current and results independently
accepted are separate states. The two selected CI properties are documented
in the [safety-case README](../safety-case/README.md); wider proofs remain open. Rerun with `cargo kani --package <name>` on
a host with Kani installed (Kani is not part of the `cargo test`
default path).

## 2. Randomised property testing (proptest)

Every Kani property has a matching proptest that exercises the
same invariant across a random input space (typically 256–1000
cases per property per run). Proptest runs on `cargo test` by
default.

| Crate | Test file | Props | Typical cases per run |
|---|---|---|---|
| `osr-atp` | `tests/proptest_atp.rs` | A1–A7 + bonus | 256 |
| `osr-brake` | `tests/proptest_brake.rs` | B1–B5 | 256 |
| `osr-odometry` | `tests/proptest_odom.rs` | O1–O5 | 256 |
| `osr-wayside-points` | `tests/proptest_wayside.rs` | W1–W6 | 256 |
| `osr-interlocking` | `tests/proptest_ma.rs` | P1–P5 | 1000 |
| `osr-interlocking` | `tests/proptest_determinism.rs` | derive-state determinism | 1000 |
| `osr-interlocking` | `tests/differential.rs` | Rust ↔ Python twin agreement | 256 |
| `osr-consensus` | (inline + suite) | 5 Raft properties; refinement open | 2000 |
| `osr-obstacle-detect` | `tests/proptest_obstacle.rs` | O1–O5 + severity + classifier downgrade | 256 |
| `osr-intrusion-detect` | `tests/proptest_intrusion.rs` | I1–I5 | 256 |
| `osr-secbus` | `tests/proptest_secbus.rs` | S1–S3 + roundtrip | 256 |
| `osr-crypto` | (inline) | C1–C4 + ed25519 determinism | 256 |

**Total proptest properties:** 60+ across the SIL-4 + SIL-2
crates. Rerun with `cargo test --workspace`; keep the resulting
workspace test count in the release log rather than baking a drifting
number into this register.

## 3. Differential testing (Rust ↔ Python)

The `tools/reference-ma/` directory carries a stdlib-only Python
re-implementation of `osr-interlocking`. `crates/osr-interlocking/tests/differential.rs`
generates random log prefixes, computes the MA in both Rust and
Python, and asserts byte-identical JSON output. Catches spec-
level bugs in either implementation.

- **Coverage:** ring lines, switch observations, route grants,
  speed restrictions, partial sections.
- **Run:** `cargo test -p osr-interlocking --test differential`.

## 4. Integration-level evidence (sim shadow stack)

`crates/osr-sim` runs the full Samawah network under the ATP +
brake + obstacle-detect + fire + derailment shadow
stack per-tick per-train. Fault injection exercises each SIL-4
evaluator's restrictive path end-to-end.

| Scenario | Fault kinds | What it demonstrates |
|---|---|---|
| `cities/catalogue/west-asia/Iraq/Samawah/samawah.toml` | None | Nominal operation: zero spurious emergencies over multi-hour revenue sim |
| Built-in dust-storm fixture (sim CLI) | PV dust, grid outage, charging-pad outage | Energy-system fault-tolerance |
| Built-in obstacle-fault fixture (sim CLI) | LIDAR/radar/ultrasonic/peer-disagreement (RFC 0015) | O1–O5 all fire through `BrakeInputs::obstacle_emergency` |
| Built-in wayside-intrusion fixture (sim CLI) | Present/Unknown on specific sections (RFC 0016) | Interlocking gate (d) withholds MA without a single train violating |

Rerun with `cargo run --release --bin osr-sim -- --config scenarios/<name>.toml`.

## 5. GSN safety-case tree

Goal-Structuring-Notation argument tree under `docs/safety-case/gsn/`,
compiled by the `osr-safety-case` CI gate. Every safety goal links
to evidence (Kani harness, proptest file, sim scenario); the CI
job fails if any goal is added without an evidence pointer. It does not run
the pointed-to proof or grant acceptance.

| File | Goals | Strategy |
|---|---|---|
| `00-top.toml` | G0 | Root claim |
| `10-non-overlap.toml` | G1 | Non-overlap of MAs |
| `20-fail-safety.toml` | G2 | Fail-restrictive default |
| `30-consistency.toml` | G3 | Log consistency |
| `40-onboard-sil4.toml` | G4 | Onboard SIL-4 layer |
| `50-wayside-sil4.toml` | G5–G14 | Wayside SIL-4 + infra |
| `60-obstacle-detect.toml` | G15–G19 | Obstacle detection (RFC 0015) |
| `70-intrusion-detect.toml` | G20–G24 | Intrusion detection (RFC 0016) |
| `80-message-authentication.toml` | G25–G27 | Message auth (RFC 0017) |

<!-- safety-case-counts:start -->
Generated case inventory: **32 goals, 6 strategies, 71 solutions**. These counts describe traceability, not successful or accepted proofs.
<!-- safety-case-counts:end -->

**CI gate:** the `starter_case_closes` test in `crates/osr-safety-case/tests/`
fails the build if a goal lacks structural traceability. The separate
[result gate](../safety-case/result-validation.md) checks execution records,
source/report hashes and independent acceptance records.

## 6. Operational-controls evidence (RFC 0013 rulebook)

The operations rulebook under `docs/operations/` defines the unattended-
operation role families. Each rule is one sentence plus
a `Why:` paragraph, cross-referenced to the specific crate it
relies on.

| Role | File count | Rule count |
|---|---|---|
| Dispatcher | S1–S7 | 35 |
| Station staff | T1–T5 | 29 |
| Maintenance | M1–M7 | 42 |
| Control centre | C1–C3 | 16 |

**Total:** 122 operational rules backing the safety-case claims.

## 7. Hardware-level evidence

Per-board spec documents under `control-electronics/<class>/schematics/v2-spec/`:

| Board | Complete spec |
|---|---|
| T-ECU/S | ✅ (block diagram, power budget, pinout RP2350, pinout CM5, safety-nets, connector tables) |
| T-OBS | ✅ (block diagram, power budget, pinout RP2350, safety-nets, connector tables) |
| T-ECU/A | pending (see option 3 of the current sprint) |
| W-SBC | pending |
| S-SBC | pending |

For pilot deployments, the RFC 0019 COTS/SBC path is a valid hardware
implementation route and does not require KiCad or gerbers when no
custom PCB is used. Its missing evidence is the integration pack:
exact SKUs, wiring/harness maps, connector maps, enclosure and mounting
notes, power/thermal margins, SD-card image checksums, `osr-selftest`
output, and bench/commissioning records.

KiCad schematic capture + gerber generation remain custom-board
milestones for any deployment that chooses OSR-specific carrier,
power, safety-I/O, or sensor-interface boards.

## 8. Evidence status and release gaps

Source inventories and successful test runs are useful development evidence.
They do not imply all formal proofs have run or all safety goals are accepted.
Record the exact source scope, named harness, tool version, bounds, result and
report hash for each run, then obtain independent acceptance of that record.
The result gate reports missing or stale records as open, even when all GSN
pointers resolve. It does not authenticate reviewers or replace an assessor.

Current release limitations remain in the
[release-gap register](release-gap-register.md) and
[safety-case proof status](../safety-case/README.md). No zero-gap safety or
physical-release claim follows from the traceability gate.
