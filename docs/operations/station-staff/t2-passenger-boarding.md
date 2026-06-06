# T2 — Passenger boarding

**Scope:** platform supervision during revenue hours. PSD
monitoring, wheelchair assistance, queue regulation.

**Cross-refs:** RFC 0010 §§5, 7 (access/circulation,
accessibility), RFC 0013 §4.3 T2.

## Rules

### T2.1 — Platform walk

During peak hours, staff walk the length of the platform at
15-minute intervals, checking for unattended items, fallen
passengers, blocked emergency exits, and fare-gate queue
overflow. Walks are logged on the station console.

**Why:** stationary platform staff see the area around their
post; walking staff see the whole platform. Peak hours are
when things go wrong fastest, so the walk cadence tightens
then.

### T2.2 — Wheelchair boarding

On a wheelchair boarding request (pre-notified or spot), staff
position the boarding ramp at door 2 of car 1 (aligned with
the reference stop mark per D4.1), assist the passenger
across the platform gap, and radio the driver to extend dwell
per D4.4.

**Why:** the gap between platform and trainset is wider than
most wheelchairs can clear unassisted, and the dwell is
shorter than unassisted boarding needs. The ramp + extension
is the accessibility guarantee that RFC 0010 §7 commits to.

### T2.3 — Overcrowding

When platform density exceeds the archetype capacity threshold
(per RFC 0010 §10), staff start queue management (rope
dividers, PA announcements regulating flow to the platform)
and notify the dispatcher, who may hold the next-following
trainset per S2.5.

**Why:** platform crowding is a crush risk. Staff have the
local signal the dispatcher cannot see; the dispatcher has
the fleet lever the staff cannot pull. Splitting the
response matches the information to the authority.

### T2.4 — Unattended item

On an unattended item report, staff clear a 5 m radius around
the item, notify the OCC, and call police / security per the
deployment's protocol. The trainset approaching the platform
is held at the previous station until the item is cleared.

**Why:** a suspicious item is rarely a bomb but always a
disruption. The 5 m clear preserves the scene; the hold
prevents a new trainset-load of passengers arriving into it.

### T2.5 — Platform clear confirmation

At non-PSD stations with no train-camera live feed, staff
confirm the platform is clear of passengers in the door zone
before the driver commands door close. Confirmation is by
radio; absence of confirmation defers door close by up to
15 s (one dwell extension) before the driver must interrogate.

**Why:** the driver's side mirror doesn't cover the full
platform length. Staff are the second pair of eyes that
catches a passenger running for the train at door close. At
PSD-equipped stations the PSD handles this mechanically, so
the rule scopes to non-PSD only.
