# S2 — Routine dispatching

**Scope:** timetable adherence, route grants, headway maintenance
during nominal operation.

**Cross-refs:** [`osr-occ`](../../../crates/osr-occ/),
[`osr-interlocking`](../../../crates/osr-interlocking/),
RFC 0013 §4.2 S2.

## Rules

### S2.1 — Route grant on schedule

The dispatcher issues each route grant via `osr-interlocking`
at the scheduled call time minus the interlocking's route-
setup lead. The OCC console pre-fills the grant from the timetable;
the dispatcher confirms.

**Why:** manual route picking defeats the timetable and
desynchronises the whole line. The confirmation step keeps a
human in the loop for the unusual case (terminal swap,
emergency diversion) without burdening the nominal case.

### S2.2 — Headway drift

When headway drift exceeds 60 s for any pair of adjacent
trainsets, the dispatcher engages the recovery pattern:
shorten dwells on the leading trainset, extend dwells on the
trailing trainset, and hold the next-following at an upstream
station until the gap closes.

**Why:** bunching is self-reinforcing — a late train picks up
more passengers, dwells longer, falls further behind, and
empties the following train. Catching it at the 60 s
threshold prevents a 20-minute unravel later.

### S2.3 — Dwell extensions

Dwell extensions beyond the driver's local 15 s authority
(D4.4) require dispatcher authorisation. The dispatcher may
grant up to 60 s cumulative per station per service; beyond
that, the service is regulated (short-turned or held at a
terminal) rather than extended further.

**Why:** chronic over-dwelling on one service drags the whole
line. The 60 s ceiling forces a regulation decision instead
of letting the problem propagate silently.

### S2.4 — Terminal turnback dispatch

At each terminal, the dispatcher confirms the cab-transfer
report from the driver (ATO handover, brake test, doors
closed) before releasing the reverse-direction route grant.

**Why:** a turnback with an unconfirmed cab transfer risks
dispatching a trainset whose active cab is still the inbound
end — a wrong-end movement that the interlocking will block
but that burns a dispatch slot.

### S2.5 — Crowding response

When a station reports a boarding rate exceeding its archetype
capacity (per RFC 0010 §10), the dispatcher may hold the
next-following trainset at the previous station to create an
empty-train gap that absorbs the surge.

**Why:** a single overcrowded train generates a long dwell,
which generates the next overcrowded train. Holding the
follower briefly costs a headway but breaks the feedback
loop.
