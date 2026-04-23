# Evidence register

Complete inventory of verification evidence produced by the
OpenSourceRail project, indexed to the safety requirements from
[safety-requirements.md](safety-requirements.md) and the hazards
from [hazard-log.md](hazard-log.md).

## 1. Formal-methods evidence (Kani bounded-model checking)

Each SIL-4 evaluator carries Kani harnesses under
`crates/<name>/src/kani_proofs.rs`, gated on `cfg(kani)` so `cargo
test` skips them and `cargo kani` runs them. The harnesses are
*bounded* formal proofs: they explore every input combination
within a stated unwind, not just test-case samples.

| Crate | Harness module | Properties | SR coverage |
|---|---|---|---|
| `osr-atp` | `kani_proofs.rs` | A1–A7 | SR-01, SR-02, SR-03 |
| `osr-brake` | `kani_proofs.rs` | B1–B5 | SR-15 |
| `osr-vigilance` | `kani_proofs.rs` | V1–V6 | (GoA 2 legacy only) |
| `osr-odometry` | `kani_proofs.rs` | O1–O5 | SR-10 |
| `osr-wayside-points` | `kani_proofs.rs` | W1–W6 | SR-01, H-CO-02 |
| `osr-interlocking` | `kani_proofs.rs` | P1–P5 | SR-01, SR-02, H-CO-01, H-CO-04 |
| `osr-obstacle-detect` | `kani_proofs.rs` | O1–O5 | SR-04, SR-05, SR-06 |
| `osr-intrusion-detect` | `kani_proofs.rs` | I1–I5 | SR-07, H-CO-03, H-SA-01 |
| `osr-secbus` | `kani_proofs.rs` | S1, S3 | SR-22, H-DI-01 |

**Total Kani harnesses:** 40+ named-property proofs across 9 SIL-4
and SIL-2 evaluators. Rerun with `cargo kani --package <name>` on
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
| `osr-vigilance` | `tests/proptest_vigilance.rs` | V1–V6 | 256 |
| `osr-odometry` | `tests/proptest_odom.rs` | O1–O5 | 256 |
| `osr-wayside-points` | `tests/proptest_wayside.rs` | W1–W6 | 256 |
| `osr-interlocking` | `tests/proptest_ma.rs` | P1–P5 | 1000 |
| `osr-interlocking` | `tests/proptest_determinism.rs` | derive-state determinism | 1000 |
| `osr-interlocking` | `tests/differential.rs` | Rust ↔ Python twin agreement | 256 |
| `osr-consensus` | (inline + suite) | 5 TLA-refined Raft properties | 2000 |
| `osr-obstacle-detect` | `tests/proptest_obstacle.rs` | O1–O5 + severity + classifier downgrade | 256 |
| `osr-intrusion-detect` | `tests/proptest_intrusion.rs` | I1–I5 | 256 |
| `osr-secbus` | `tests/proptest_secbus.rs` | S1–S3 + roundtrip | 256 |
| `osr-crypto` | (inline) | C1–C4 + ed25519 determinism | 256 |

**Total proptest properties:** 60+ across the SIL-4 + SIL-2
crates. Rerun with `cargo test --workspace`; 705 tests currently
pass with zero failures.

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
brake + obstacle-detect + vigilance + fire + derailment shadow
stack per-tick per-train. Fault injection exercises each SIL-4
evaluator's restrictive path end-to-end.

| Scenario | Fault kinds | What it demonstrates |
|---|---|---|
| `scenarios/samawah.toml` | None | Nominal operation: zero spurious emergencies over multi-hour revenue sim |
| `scenarios/samawah-dust-storm.toml` | PV dust, grid outage, charging pad outage | Energy-system fault-tolerance |
| `scenarios/samawah-obstacle-fault.toml` | LIDAR/radar/ultrasonic/peer-disagreement (RFC 0015) | O1–O5 all fire through `BrakeInputs::obstacle_emergency` |
| `scenarios/samawah-wayside-intrusion.toml` | Present/Unknown on specific sections (RFC 0016) | Interlocking gate (d) withholds MA without a single train violating |

Rerun with `cargo run --release --bin osr-sim -- --config scenarios/<name>.toml`.

## 5. GSN safety-case tree

Goal-Structuring-Notation argument tree under `docs/safety-case/gsn/`,
compiled by the `osr-safety-case` CI gate. Every safety goal links
to evidence (Kani harness, proptest file, sim scenario); the CI
job fails if any goal is added without a verifying evidence link.

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

**Total:** 27 top-level goals; 70+ solution links to concrete evidence.

**CI gate:** the `starter_case_closes` test in `crates/osr-safety-case/tests/`
fails the build if any goal is un-closed.

## 6. Operational-controls evidence (RFC 0013 rulebook)

The operations rulebook under `docs/operations/` defines 40+
rules across five role families. Each rule is one sentence plus
a `Why:` paragraph, cross-referenced to the specific crate it
relies on.

| Role | File count | Rule count |
|---|---|---|
| Driver (GoA 2 legacy) | D1–D8 | 45 |
| Dispatcher | S1–S7 | 35 |
| Station staff | T1–T5 | 29 |
| Maintenance | M1–M7 | 42 |
| Control centre | C1–C3 | 16 |

**Total:** 167 operational rules backing the safety-case claims.

## 7. Hardware-level evidence

Per-board spec documents under `hardware/<class>/schematics/v2-spec/`:

| Board | Complete spec |
|---|---|
| T-ECU/S | ✅ (block diagram, power budget, pinout RP2350, pinout CM5, safety-nets, connector tables) |
| T-OBS | ✅ (block diagram, power budget, pinout RP2350, safety-nets, connector tables) |
| T-ECU/A | pending (see option 3 of the current sprint) |
| W-SBC | pending |
| S-SBC | pending |

KiCad schematic capture + gerber generation are v3.1 per-board
milestones (deferred alongside RFC 0007 v3 rollout).

## 8. Summary of evidence density

- **51 crates** in the safety-relevant workspace.
- **705 Rust tests** passing, 0 failing (as of 2026-04-23).
- **40+ Kani harnesses** across 9 SIL-4/SIL-2 evaluators.
- **60+ proptest properties** across 13 crates.
- **27 GSN top-level goals** closed against 70+ evidence solutions.
- **167 operational rules** across 5 role families.
- **4 sim scenarios** exercising nominal + fault + driverless +
  wayside-intrusion paths.
- **2 hardware v2 specs** (T-ECU/S, T-OBS) with safety-nets
  traceable to the SIL-4 hardware argument; 3 more pending.

Zero test failures. Zero workspace build warnings. Zero open
safety-case gaps against SR-01 through SR-24 at the crate level.
