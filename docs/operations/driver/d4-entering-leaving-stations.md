# D4 — Entering + leaving stations

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

**Scope:** approach, stopping, dwell, and departure. PSD
coordination, passenger-boarding timing, dwell-extension
protocol.

**Cross-refs:** [`osr-psd`](../../../crates/osr-psd/), RFC 0010
§4 (platform geometry), RFC 0013 §4.1 D4.

## Rules

### D4.1 — Platform-stop accuracy

The trainset stops within ± 0.5 m of the reference stop mark
(painted line at the platform edge, aligned with door 2 of car
1). In GoA 2 the ATO handles this automatically; in GoA 1 the
driver targets the mark by eye + DMI position indicator.

**Why:** stops outside ± 0.5 m put some doors outside the PSD
zone (at PSD-equipped stations) or leave passengers reaching
up to the retractable skirt (at non-PSD stations).

### D4.2 — PSD open command

At PSD-equipped stations, the driver commands `Door open` on
the DMI. The PSDs open first (via `osr-psd` FSM), then the
trainset doors follow. The DMI mimic shows both layers green.

**Why:** `osr-psd` requires a train-stopped-at-platform signal
before opening. Commanding train doors first at a station
where PSDs are closed puts passengers between two panes of
glass.

### D4.3 — Dwell-timer start

Dwell timer starts when the last door opens, not on train
stop. The DMI shows remaining dwell time.

**Why:** slow-opening doors extend effective dwell by up to a
few seconds at peak; starting on the last door keeps the
schedule honest.

### D4.4 — Dwell extension

The driver extends dwell via `DMI → Dwell → Extend` in 5 s
increments, up to 3 extensions per station (15 s total
extra). Reasons: passenger obstruction, wheelchair boarding,
accessibility hold. Beyond 3 extensions the dispatcher must
authorise via radio.

**Why:** 15 s of extension on a handful of stations is absorbed
by the schedule slack. Chronic over-extension is a sign that
the station archetype or headway is undersized — a dispatcher-
level signal, not a driver discretion.

### D4.5 — Door + PSD close

The driver commands `Door close` when boarding is complete.
Train doors close first; PSDs follow 1 s later (per
`osr-psd`'s FSM). The DMI mimic shows all doors green-closed
+ interlocked + all PSDs green-closed.

**Why:** closing train doors first prevents a passenger from
stepping through a closing PSD into a moving door.

### D4.6 — Release to depart

The driver's `Start` command is accepted by `osr-atp` only
when: MA is valid, all train doors green, all PSDs green (if
fitted), no alarms. A red block on any of these prevents
first-motion.

**Why:** the start gate is a hard safety interlock with no
manual override. A driver cannot coax past it — which is the
point. The rulebook makes this explicit so drivers don't
waste troubleshooting time on the start command itself.
