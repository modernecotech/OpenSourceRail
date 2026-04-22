# D6 — Degraded-mode operation

> **Deprecated for GoA 4 deployments (RFC 0015, 2026-04-22).**
> OpenSourceRail ships as Unattended Train Operation by default
> — no driver cab, no driver role. This rule file is retained
> as the reference for legacy GoA 2 cabbed fleets. GoA 4
> deployments absorb these responsibilities into dispatcher (S),
> station-staff (T), maintenance (M), and control-centre (C)
> rulebooks plus the onboard automation stack (`osr-atp`,
> `osr-ato`, `osr-obstacle-detect`). See
> [RFC 0013 §4.1](../../rfcs/0013-operations-rulebook.md)
> for the per-section migration table.

**Scope:** the three modes per RFC 0013 §5 — M1 (manual on MA),
M2 (restricted on written order), M3 (yard manoeuvre). No
other modes exist; no in-between states.

**Cross-refs:** RFC 0013 §5, [`osr-atp`](../../../crates/osr-atp/),
[`osr-occ`](../../../crates/osr-occ/).

## Rules

### D6.1 — M1 entry

The driver enters M1 when the DMI banner reads
`ATO unavailable — ATP supervising`. Entry is automatic; no
driver keyswitch. The driver takes manual control of traction
and service brake while ATP keeps supervising the envelope.

**Why:** ATO is the convenience layer; ATP is the safety
layer. If only ATO is degraded, the safety envelope is still
intact — the driver just does the driving.

### D6.2 — M1 speed cap

In M1 the driver commands ≤ 80 % of normal line speed. The
DMI tightens the envelope to 80 % automatically; the driver's
± 5 % headroom (D3.1) is within that.

**Why:** manual driving has higher variability than ATO;
80 % headroom absorbs that without nuisance ATP trips.

### M1.3 — M1 dwell extension

At every station in M1, the driver extends dwell by 5 s before
closing doors, to visually verify the platform is clear.

**Why:** ATO communicates with `osr-psd` over TCN-E; in M1
ATO isn't driving, so the PSD coordination is slower and more
error-prone. The 5 s is a cheap recovery window.

### D6.4 — M2 entry

The driver enters M2 only on explicit dispatcher order. The
DMI banner reads `M2 written order in effect, speed cap
15 km/h`. The order carries a block-end station and a time
limit.

**Why:** M2 is the legacy-rail fallback — paper (or
electronic-paper) written order from the dispatcher.
Self-entering M2 is not possible and not allowed.

### D6.5 — M2 operation

In M2 the driver operates at ≤ 15 km/h with sight-distance
braking (stop within the visible track ahead). One train per
block between manned landmarks; the dispatcher's roll-call
over radio confirms block occupancy.

**Why:** M2 lives outside the MA / ATP envelope. The driver's
eye is the primary safety sensor; sight-distance braking is
the only safe rule when a computed authority is unavailable.

### D6.6 — M3 entry (yard manoeuvre)

Inside depot limits the DMI enters M3 automatically once the
trainset crosses the depot geofence. M3 disables ATP below
15 km/h and permits hand-signal-and-line-of-sight operation.

**Why:** the depot is a low-speed, staff-supervised
environment. ATP's nominal envelope would create nuisance
trips on every shunt move; disabling under geofence +
geo-limited speed is the tractable fallback.

### D6.7 — Mode-transition discipline

The driver never transitions M1 → M2 without explicit
dispatcher authorisation. Transitioning M2 → M1 is also
dispatcher-authorised (MA restored, written order revoked).
M3 is implicitly entered/exited by the geofence; no driver
toggle.

**Why:** unauthorised mode transitions produce degraded-state
ambiguity — the dominant root cause of legacy-metro incidents.
The rulebook draws hard boundaries.
