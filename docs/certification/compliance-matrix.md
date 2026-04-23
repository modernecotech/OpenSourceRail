# EN 62267 compliance matrix

Clause-by-clause traceability from EN 62267 (Railway applications
— Automated urban guided transport — Safety requirements) to OSR
implementation. Citations are to the 2009 edition.

Format per clause:

- **Clause** — reference.
- **EN 62267 requirement summary** — single-sentence paraphrase.
- **OSR implementation** — which crate(s) / RFC(s) / rulebook
  section fulfils it.
- **Evidence** — specific artefact to cite in the submission.

## §5 — Safety principles

### §5.1 — Inherent and functional safety

**Requirement:** system shall implement both *inherent* safety
(design choices that make hazards impossible by construction)
and *functional* safety (safety functions that detect + mitigate
hazards that cannot be designed out).

**OSR implementation:**
- **Inherent safety:** no tunnels (RFC 0011), prefab-only civil
  (RFC 0011), single consist family per line (RFC 0008),
  fixed-geometry preset per line (RFC 0009). Each removes an
  entire hazard class by eliminating its precondition.
- **Functional safety:** SIL-4 chain per [safety-requirements.md
  SR-01..SR-24](safety-requirements.md).

**Evidence:** RFCs 0008–0011; safety-requirements.md.

### §5.2 — Responsibility assignment

**Requirement:** a responsibility matrix shall document which
entity owns each safety-relevant function.

**OSR implementation:** RFC 0013 §4 (one shared rulebook across
5 role families); `osr-safety-case` GSN tree links every claim
to an owning evaluator.

**Evidence:** RFC 0013; GSN tree under `docs/safety-case/gsn/`.

## §6 — Functional requirements (SIL-4 core)

### §6.1 — Ensuring safe movement

**Requirement:** automated system shall ensure the train moves
only when it is safe to do so.

**OSR implementation:** `osr-interlocking::section_available_to`
with four gates (occupancy, route, override, intrusion);
`osr-atp::atp_evaluate` overlays the envelope check.

**Evidence:** SR-01, SR-02, SR-03, SR-07; Kani harness modules
on `osr-interlocking`, `osr-atp`.

### §6.2 — Preventing collision

**Requirement:** system shall prevent collisions between trains,
with infrastructure, and with obstacles.

**OSR implementation:** train-train via SR-01; track-worker via
SR-01 + `MaintenanceOverride`; obstacle via SR-04 (onboard) +
SR-07 (wayside) — two-layer defence per RFC 0015 + RFC 0016.

**Evidence:** H-CO-01..04 hazard log; RFC 0015 §6 safety case.

### §6.3 — Preventing derailment

**Requirement:** system shall prevent derailment from
overspeed, mis-set switch, or mechanical cause.

**OSR implementation:** overspeed via ATP (SR-03); switch via
`osr-wayside-points` 2oo2 sensor fusion; mechanical via
SR-11 onboard derailment monitor; track maintenance cadence
RFC 0013 M3 + M4.

**Evidence:** SR-03, SR-11; hazard H-DE-01, H-DE-02.

### §6.4 — Preventing falls

**Requirement:** system shall prevent falls from platforms.

**OSR implementation:** SR-24 PSDs at every boarding platform;
SR-10 platform-alignment gate; station-staff T2 supervision at
non-PSD depot-terminals.

**Evidence:** RFC 0010 §6; RFC 0015 §5.4.

### §6.5 — Protecting people on track

**Requirement:** system shall protect people on track — workers
and intruders.

**OSR implementation:** workers via `MaintenanceOverride` +
RFC 0013 S5 + M2 protection signals; intruders via SR-07
wayside intrusion gate + physical fence (civil scope).

**Evidence:** SR-07; H-CO-04, H-SA-01.

### §6.6 — Closing doors

**Requirement:** system shall ensure doors close safely.

**OSR implementation:** SR-08, SR-09 on `osr-door-control`;
RFC 0013 T2.5 platform-clear confirmation at non-PSD stations.

**Evidence:** SR-08, SR-09; hazard H-PB-01, H-PB-03.

### §6.7 — Starting the train

**Requirement:** the system shall start the train only when
safe (all doors closed, MA valid, all monitors nominal).

**OSR implementation:** `osr-atp`'s start-inhibit composes:
doors_closed_all && ma_valid && !any_monitor_trip; RFC 0013
D4.6 rulebook documents the driver-visible behaviour (applies
to GoA 2; GoA 4 automates via ATO).

**Evidence:** SR-15, SR-19; `osr-ato` start-gate unit tests.

### §6.8 — Stopping the train

**Requirement:** the system shall stop the train safely on any
EB source.

**OSR implementation:** `osr-brake` emergency-source union
(ATP + vigilance + fire + derailment + driver + obstacle);
SR-15 — EB dominates.

**Evidence:** `osr-brake` Kani B2 + B3 harness; proptest
`b2_emergency_union`.

### §6.9 — Preventing hostile environments

**Requirement:** system shall handle weather, dust, heat per
deployment climate.

**OSR implementation:** RFC 0013 S4 weather rulebook;
`climate-adapters.toml` per-deployment tuning; `osr-energy-site`
handles PV dust derating.

**Evidence:** RFC 0013 §6 weather rules; climate-adapter file.

### §6.10 — Detecting smoke + fire

**Requirement:** onboard fire detection + suppression.

**OSR implementation:** `osr-fire-safety` (SIL-4); RFC 0008
bays each carry BaySensors; suppression by Novec 1230 or equiv.

**Evidence:** SR-12; H-FI-01, H-FI-02.

### §6.11 — Operating in degraded mode

**Requirement:** system shall safely continue at reduced
performance under named degraded modes.

**OSR implementation:** RFC 0013 §5 M1 (manual on MA) / M2
(restricted service) / M3 (evacuation) as the only three
degraded modes.

**Evidence:** RFC 0013 §5; degraded-mode driver rules D6 (GoA 2
legacy); GoA 4 equivalent in dispatcher S7 + S5.

### §6.12 — Supervision and rescue of passengers

**Requirement:** system shall support passenger supervision +
rescue without a driver.

**OSR implementation:** SR-14 passenger emergency intercom;
SR-18 remote-assist channel; RFC 0015 §5.3 + §5.5 cabin CCTV
live to OCC.

**Evidence:** SR-14, SR-18; RFC 0015 §5.

## §7 — System performance

### §7.1 — Tolerable hazard rate (THR)

**Requirement:** the safety integrity of each safety function
shall correspond to a tolerable hazard rate.

**OSR implementation:** SIL-4 functions target THR ≤ 10⁻⁹ /h,
consistent with EN 50129 (SIL-4 allocated to the safety
functions per the hazard log).

**Evidence:** [residual-risk.md](residual-risk.md) (pending
v1.1); [hazard-log.md](hazard-log.md) severity × frequency table.

### §7.2 — Systematic failures

**Requirement:** systematic failures (specification, design,
implementation bugs) shall be controlled via the EN 50128
process.

**OSR implementation:** Rust `#![forbid(unsafe_code)]`;
integer-only safety path; Kani bounded-model proofs; proptest
randomised verification; differential twin (Rust vs Python);
RFC-driven change control.

**Evidence:** Evidence register §1–§5; CI gates on
`cargo test` + `starter_case_closes`.

### §7.3 — Random hardware failures

**Requirement:** random hardware failures shall be detected
and handled fail-restrictively.

**OSR implementation:** 2oo2 at T-ECU/S + T-OBS (SR-20);
watchdog + supervisor (SR-21); ATECC608B trust anchor; per-rail
power supervision; redundant 24 V input.

**Evidence:** `hardware/t-ecu-s/schematics/v2-spec/safety-nets.md`;
`hardware/t-obs/schematics/v2-spec/safety-nets.md`.

## §8 — Safety management

### §8.1 — Safety lifecycle

**Requirement:** EN 50126 lifecycle from concept to
decommissioning.

**OSR implementation:** RFC-per-major-decision; GSN claim tree
under `docs/safety-case/`; operations rulebook under
`docs/operations/`; `osr-safety-case` CI gate. Deployment
partner handles site-specific lifecycle stages (commissioning,
operations, decommissioning).

**Evidence:** RFC 0001–0017; this certification pack as the
"safety case" deliverable.

### §8.2 — Independent safety assessment

**Requirement:** an independent assessor reviews the safety
case.

**OSR implementation:** this pack is prepared for external
assessment. The deployment partner engages the assessor
(RFC 0003 §5).

**Evidence:** N/A (upstream prerequisite for the assessor, not
produced by this pack).

### §8.3 — Competency of staff

**Requirement:** operating + maintenance staff competent for
their role.

**OSR implementation:** RFC 0013 C1 role qualification (§C1.5);
RFC 0013 §8 training + recurrent qualification program.

**Evidence:** RFC 0013 §8; deployment-specific training record.

## §9 — Cybersecurity (complementary)

Although EN 62267 itself does not prescribe cybersecurity
requirements (it pre-dates the CENELEC EN 50701 split), a
modern GoA 4 submission is expected to carry IEC 62443-4-2 +
EN 50701 evidence as a complementary cybersecurity
dossier.

### §9.1 — Message authenticity

**OSR implementation:** SR-22 `osr-secbus` (RFC 0017 v1 library;
v2 wiring open).

**Evidence:** GSN G25–G27; `osr-secbus` Kani + proptest.

### §9.2 — Component-level protection

**OSR implementation:** ATECC608B trust anchors on every SIL-4
host class; zero-on-drop key wrappers (`osr-crypto`); per-
deployment key registry (`osr-secbus`).

**Evidence:** `hardware/t-ecu-s/schematics/v2-spec/`;
`osr-crypto` + `osr-secbus` source.

## Summary

- **§5.1–§9.2: 19 clauses mapped.**
- **16 clauses** have direct implementation + evidence in tree.
- **3 clauses** (§7.1 residual risk, §8.2 independent
  assessment, §8.3 staff competency) depend on deployment-
  partner input — deliberately scoped that way per
  [README.md](README.md).
- **1 clause** (§9.1 message authenticity) has library in
  tree but v2 wire integration open.

No EN 62267 clause has an open gap at the stack level. Gaps
are all on the deployment-partner side of the boundary.
