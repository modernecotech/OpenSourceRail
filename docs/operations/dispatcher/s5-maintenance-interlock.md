# S5 — Maintenance interlock

**Scope:** granting work-on-track authorities, blocking sections
for maintenance, and restoring to revenue after work completes.

**Cross-refs:** [`osr-interlocking`](../../../crates/osr-interlocking/)
`MaintenanceOverride` entries, RFC 0013 §4.2 S5.

## Rules

### S5.1 — Formal work-block authorisation

The dispatcher issues a work block by committing a
`MaintenanceOverride` entry to `osr-interlocking` with a
specific work-crew id, section ids, and an expiry timestamp
(default 60 min, extendable per S5.4). The OCC console prompts for
each field; blank fields reject the commit.

**Why:** open-ended blocks with vague scope are how work crews
get dispatched onto live track. The structured form makes
every block uniquely identifiable, time-bounded, and
traceable to a named crew.

### S5.2 — Train clear verified

Before the `MaintenanceOverride` commit is accepted,
`osr-interlocking` verifies no trainset footprint overlaps
the requested section. The dispatcher cannot override this
check.

**Why:** granting a work block while a trainset is in the
section puts the crew in front of a moving train. The
interlocking's section-occupancy logic is the same one that
enforces Movement Authority — so if it can't prove the
section is clear, the block waits.

### S5.3 — Protection signals

Before work begins, the dispatcher requests protection
signals (red aspect + trap point if fitted) at both ends of
the blocked section. The wayside crew radio confirms each
protection signal is visible and effective.

**Why:** the interlocking prevents new MA into the section,
but a trainset already holding MA through the section must
still see a stop signal. Protection is the last defence
against a runaway movement.

### S5.4 — Block extension

Block extensions are granted in 30-minute increments, not
open-ended. The dispatcher renews the `MaintenanceOverride`
expiry at each increment with a fresh radio check to the
crew.

**Why:** a 4-hour block that overruns silently leaves the
track blocked after the crew has gone home. The 30-minute
cadence forces regular radio contact, which catches silent
overruns.

### S5.5 — Block clearance

The dispatcher clears the block only after: crew withdrawal
confirmed on radio, protection signals cleared, and track
walk-back confirmed clear of tools and material. The
`MaintenanceOverride` expiry is then committed — which
returns the section to revenue availability.

**Why:** tools left on the track are how the first trainset
back into the section derails. The walk-back is the non-
negotiable final step; the dispatcher is the gatekeeper.
