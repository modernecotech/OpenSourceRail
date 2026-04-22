# M4 — Switch maintenance

**Scope:** blade lubrication, detection-sensor cleaning, mechanical
inspection per RFC 0012 §4.

**Cross-refs:** RFC 0012 §4, [`osr-wayside-points`](../../../crates/osr-wayside-points/),
RFC 0013 §4.4 M4.

## Rules

### M4.1 — 30-day switch inspection

Every switch is inspected every 30 days per RFC 0012 §4.1:
blade closure at toe (≤ 1.5 mm gap), stretcher-bar
tightness, switch-rail wear limit, stock-rail wear limit,
detection-sensor alignment, and cable-gland integrity.

**Why:** the 30-day cycle matches the switch-machine CBM
curve — beyond that, probability of silent drift into
QN2 territory rises above the acceptable envelope.

### M4.2 — Self-lubricating slide chair

The RFC 0012 self-lubricating slide-chair spec requires no
routine re-greasing, but the 30-day inspection confirms
slide chairs are free of sand contamination, dust clumping,
and debris. Contaminated chairs are cleaned but not
re-greased.

**Why:** greasing over contaminated chairs traps the
contamination in the slide path, which is worse than the
contamination alone. Cleaning without re-grease is the
correct maintenance action per the chair datasheet.

### M4.3 — Stretcher-bar tightness

Stretcher-bar bolts are torque-checked to the RFC 0012 spec
(200 N·m, per RFC 0012 §3 kit) every 30 days. Loose bolts
are tightened and flagged for follow-up on the next cycle.

**Why:** a stretcher-bar failure is a classic derailment
mode — the blade opens under a passing wheel. Torque-checking
is the only way to catch creeping loosening before it
becomes mechanical play.

### M4.4 — Detection-sensor cleaning

A/B inductive detection-sensor faces are cleaned every 30
days with a dry cloth. Sensors showing drift in their
response curve (logged to `osr-wayside-points`) are
replaced at the next 30-day cycle rather than cleaned again.

**Why:** detection sensor reliability is the `osr-wayside-
points` safety case's key assumption. Cleaning maintains the
reliability; replacement at drift onset is cheaper than the
MA-blocking fault that a failed sensor triggers.

### M4.5 — Switch-machine motor

Switch-machine electric motors are inspected every 90 days
for brush wear, commutator condition, and current draw at
throw (compared against the baseline). Motors outside the
current-draw envelope are replaced.

**Why:** motor current rise precedes mechanical failure by
several weeks; catching it at the 90-day cycle prevents
mid-operation failure. The baseline comparison makes the
drift detectable earlier than a single snapshot.

### M4.6 — Points heating

For deployments in climate zones where frost is a concern
(not Samawah, but the RFC 0012 spec covers cold-climate
adaptations), thermostats for points heating are checked at
the start of cold season: calibration check, heating-
element resistance check, contactor operation.

**Why:** frozen points are a winter-morning incident in every
cold-climate system; a heating fault discovered on the first
frost is a reliability failure. The pre-season check moves
discovery into a controlled window.

### M4.7 — Post-dust-storm

After any S4.1 dust-storm event, all switches in the
affected area are inspected and blade-cleaned within 48
hours, independent of the 30-day cycle.

**Why:** dust-jammed switches are the single largest post-
haboob failure mode in the Middle East climate adapter. The
48-hour window ensures the cleaning happens while the drift
is fresh, before wheel traffic packs it into the slide
chair.
