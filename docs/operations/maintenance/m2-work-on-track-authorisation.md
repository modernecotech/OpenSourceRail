# M2 — Work-on-track authorisation

**Scope:** formal work blocks, protection signals, access to active
ROW. Paired 1:1 with the dispatcher's S5 rules.

**Cross-refs:** S5 (dispatcher) + `osr-interlocking` `MaintenanceOverride`,
RFC 0013 §4.4 M2.

## Rules

### M2.1 — Request work-block

Work-block requests are submitted to the OCC at least 48
hours in advance for planned work; 2 hours minimum for
urgent (safety-affecting) work. The request names the
crew lead, section ids, scope of work, and planned
duration.

**Why:** 48 hours allows the dispatcher to slot the block
without service disruption; the 2-hour floor for urgent
work balances speed against coordination with other
movements. Unplanned drop-in requests strand crews.

### M2.2 — Protection signals set

On arrival at the work site, the crew lead confirms
protection signals (per S5.3) are set at both ends of the
block and radios the OCC to commit the `MaintenanceOverride`.
Work does not start until the commit is acknowledged.

**Why:** arriving and working before the commit means the
crew is on track with no interlocking protection. The
radio handshake is the moment the crew is formally
protected.

### M2.3 — Stay inside the block

During the block, crew members remain inside the protected
section except for a single "roamer" permit per crew (one
person authorised to step outside for inspection or tool
retrieval). The roamer carries a high-visibility armband and
a personal radio.

**Why:** crew members outside the block are not protected by
the block. Limiting this to a single named roamer keeps the
accounting tractable and ensures the roamer knows they are
exposed.

### M2.4 — Half-hourly check-in

The crew lead radios the OCC every 30 minutes with a crew
headcount and progress update. Missed check-ins trigger the
OCC welfare protocol (S5.4 extension check).

**Why:** a crew in trouble (medical, fall, entrapment) needs
help fast; the 30-minute cadence bounds the OCC's discovery
delay and matches the S5.4 block-extension cadence on the
other side.

### M2.5 — Block clearance

On work completion, the crew lead confirms: all tools
withdrawn, all personnel accounted for by name, track walked
clear of debris, protection signals cleared. The OCC is then
radioed to release the `MaintenanceOverride` per S5.5.

**Why:** a hammer left on a rail derails a trainset. The
named-personnel accounting prevents leaving a worker behind;
the walk-clear is the final sweep.

### M2.6 — No trains through a block

No rolling-stock movement is authorised through a section
under active `MaintenanceOverride`, regardless of written
orders, radio instruction, or apparent urgency. The block
is a hard interlock.

**Why:** historical incidents almost all involve "just one
train through" at a supposedly secure block. Making M2.6 a
no-exception rule removes the ambiguity — if a train must
go through, the block must first be cleared, not
overridden.
