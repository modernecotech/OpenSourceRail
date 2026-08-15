# S7 — Intrusion response

**Scope:** OCC dispatcher response to wayside track-intrusion
detections raised by `osr-intrusion-detect`. Per-section verdicts
arrive on the OCC dashboard as `Present` / `Unknown` / `Clear`
(RFC 0016 §5.2).

**Cross-refs:** [`osr-intrusion-detect`](../../../crates/osr-intrusion-detect/),
[`osr-interlocking`](../../../crates/osr-interlocking/)
`SectionIntrusion` entries, RFC 0016 §7.1.

## Rules

### S7.1 — First-response track patrol

On the first `Present` verdict on any section, the dispatcher
dispatches track-patrol within 10 minutes and notifies the
engineer-on-call. While the verdict stands, the interlocking
withholds MA on that section automatically — no manual hold
is required.

**Why:** the interlocking already enforces the safety
restriction — there is no "move faster before the gate drops"
concern. The dispatcher's job is to resolve the underlying
cause (animal, debris, trespasser) and return the section to
`Clear`, which is a ground-level task.

### S7.2 — Sustained Unknown treated as equipment failure

A `Unknown` verdict persisting for more than 5 minutes is
treated as a wayside-equipment fault. The dispatcher opens
a work ticket against the affected junction box, holds or
diverts any trains whose route requires the section, and
notifies maintenance per M7.

**Why:** a brief `Unknown` is a sensor flap; five minutes of
`Unknown` is a hardware problem that will not resolve itself.
The ticket routes the fix into the CBM stream rather than
the dispatcher improvising a repair.

### S7.3 — Return to service

The dispatcher returns the section to revenue only after:
(a) track-patrol confirms the section clear of obstruction,
(b) wayside sensors have produced at least one fresh `Clear`
verdict, and (c) any affected PSDs and stations are ready.
The "return to service" action is an OCC-console command
that logs the dispatcher's confirmation to the shift log.

**Why:** clearing the patrol check but not the sensor check
is the shortest path to immediately re-blocking the same
section (e.g., debris missed on walk-through). The three-gate
sequence keeps the system honest.

### S7.4 — Multi-section outage escalation

When three or more sections on the same line carry non-Clear
verdicts concurrently, the dispatcher treats it as a line-
wide event — escalates to the supervisor, considers cutting
revenue service on the affected line, and activates the
network-disruption passenger communications protocol.

**Why:** three concurrent intrusions are almost always
either a coordinated event (storm, security incident) or a
wayside comms failure that's affecting multiple junction
boxes. Both cases call for line-level intervention, not
per-section management.

### S7.5 — No override

The dispatcher has no authority to force a section to
`Clear` by dispatcher action. The interlocking's
`section_available_to` gate (d) is a hard interlock.

**Why:** if the dispatcher could clear the verdict from the
console, the safety case for wayside detection is broken —
the interlocking would be advisory rather than authoritative.
Real clearance comes from track-patrol + sensor agreement per
S7.3, not from a dispatcher button.
