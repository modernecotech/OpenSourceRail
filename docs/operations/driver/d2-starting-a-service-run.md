# D2 — Starting a service run

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

**Scope:** from cab ready to first motion on a revenue run.
Authority acknowledgement, platform-clearance confirmation,
door close coordination, MA release to `osr-atp`.

**Cross-refs:** RFC 0001 §7, [`osr-atp`](../../../crates/osr-atp/),
[`osr-psd`](../../../crates/osr-psd/), RFC 0013 §4.1 D2.

## Rules

### D2.1 — Acknowledge the incoming MA

On the DMI's "MA received" prompt, the driver presses `Accept`
before releasing the brake. The DMI shows the MA validity
window counting down; the driver must accept within that
window.

**Why:** an MA is only valid for 3 s of wall clock per
RFC 0001 §6.3 (`MA_VALIDITY_WINDOW_NS`). Accepting an expired
MA is a null action — the dispatcher re-issues. Accepting a
stale MA *and* treating it as live is the failure mode this
rule rules out.

### D2.2 — Confirm platform clearance

On PSD-equipped stations, the driver reads `PSD: closed +
interlocked` on the DMI. On non-PSD stations, the driver
visually scans the platform for passengers within 1 m of the
edge before issuing door-close.

**Why:** the door-close command initiates dwell end. A platform
obstruction under or at the door-line produces a passenger-
injury incident that the vehicle-side sensors cannot always
detect.

### D2.3 — Close trainset doors

The driver issues `Door close` on the DMI. All 24 doors must
report `closed + interlocked` on the mimic diagram within 8 s.
Any door not reporting: reopen that door, wait 3 s, reissue
close.

**Why:** an unclosed door fails the ATP envelope check in
`osr-door-control`; the train will not move. But a *mis*-reporting
door (closed mechanically but interlock not latched) can pass
the static check and fail mid-motion. Reopening resets the
state.

### D2.4 — ATO / manual authorisation

In GoA 2 operation (driver supervising ATO), the driver presses
`Start` on the DMI; ATO takes the consist to the next station
within the ATP envelope. In GoA 1 / fallback manual, the driver
notches off the master controller at ≤ 10 % tractive effort
initial.

**Why:** ATO's acceleration ramp is pre-configured and smooth;
manual notch-off should match ATO's behaviour unless there is
a specific operational reason (e.g. slippery-rail procedure).
Aggressive manual departure is a passenger-comfort complaint
that the event recorder tags.

### D2.5 — First-motion check

Within the first 5 s of motion, the driver confirms: speed rising
monotonically on the DMI, no red banners, event recorder still
green, and the vibration / sound profile of the trainset is
nominal (driver judgement).

**Why:** a failure to move — or anomalous motion — at departure
is the one moment a driver has full-attention on the trainset
before passenger interactions start. This 5-second window is
the cheapest quality check in the whole shift.

### D2.6 — Abort conditions

If at any point during D2.1–D2.5 the MA revokes (DMI banner
`MA revoked`), a PSD re-opens, the passenger-emergency alarm
fires, or a red fault banner appears, the driver immediately
stops the trainset with service brake and notifies the
dispatcher via TRG-1 radio before any further action.

**Why:** multiple faults stacking at departure produce
corrupted root-cause evidence. Stopping immediately on any one
of them preserves the event-recorder trace for investigation.
