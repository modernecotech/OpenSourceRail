# D7 — Emergencies

**Scope:** driver response to emergencies — emergency-brake
plunger, EB recovery, passenger medical, fire, derailment,
onboard violence.

**Cross-refs:** [`osr-brake`](../../../crates/osr-brake/),
[`osr-fire-safety`](../../../crates/osr-fire-safety/),
[`osr-derailment`](../../../crates/osr-derailment/), RFC 0013
§4.1 D7 + §7 incident categorisation.

## Rules

### D7.1 — Emergency-brake plunger

The driver strikes the plunger any time they believe the
trainset must stop and any normal mechanism may fail. The
plunger hardwires to `osr-brake`'s emergency source — no
DMI, no timeout, immediate brake application.

**Why:** the plunger is the cheap, always-available last line.
Drivers should strike it without deliberation; a false-positive
stop is recoverable, a missed-positive is not.

### D7.2 — Post-EB recovery

After any EB (triggered by plunger, ATP, vigilance, fire,
derailment, or passenger alarm), the driver does NOT release
the brake until (a) the DMI's EB-source indicator clears,
(b) OCC authorises via radio, (c) the driver visually confirms
no obvious trainset fault.

**Why:** an EB without root-cause clarification is how Cat I3
becomes Cat I5. The 3-way confirmation adds 30–60 s to every
EB recovery; that's worth it.

### D7.3 — Fire alarm

If the DMI's fire banner shows, the driver confirms
`osr-fire-safety`'s automatic suppression has fired (DMI shows
`Suppression: discharged`). If not, the driver presses the
cab's manual fire-suppress button. In either case the
trainset is stopped at the next station if within 30 s, then
passengers evacuated via emergency door release. PA:
"Fire on board — exit via the nearest open door."

**Why:** `osr-fire-safety`'s automatic path is reliable but
not foolproof; manual backup covers the residual risk. The
"next station within 30 s" rule matches D3.5's passenger-
alarm rule — stopping inside a station means passengers reach
ground evacuation paths, not the track bed.

### D7.4 — Derailment / unusual motion

If the DMI shows derailment alarm OR the driver feels a lurch
they cannot explain (not a curve, not a brake, not a PA), the
driver pulls the plunger immediately, cuts traction, radios
OCC with Cat I5 + line + approximate milepost, and prepares
the consist for evacuation (doors to emergency-release mode,
PA: "Brace, brace, brace — then prepare to exit").

**Why:** derailment is the worst-case rail scenario. Every
second of uncertainty in the response adds to injury risk.
This rule is the single most consequential in the entire
rulebook.

### D7.5 — Passenger medical incident

The driver stops at the next station within 30 s travel (or
immediately, if not), makes the `medical on board at car N`
PA, radios OCC for ambulance dispatch, and holds the train
until handover to station staff.

**Why:** holding a trainset in station is cheaper than
coordinating ambulance access to a midline stop. The 30 s
rule is the same calculation as D3.5.

### D7.6 — Onboard violence or terror suspicion

The driver locks the cab (mechanical latch on cab door + DMI
"Cab secured" command), radios OCC with Cat I6, proceeds to
the next staffed station at nominal speed (no stop-short), and
lets OCC coordinate with emergency services. The driver does
not leave the cab and does not engage with passengers.

**Why:** the driver's job is to get the train to help, not to
intervene. Cab-lock + continue-to-help is the rail-world
analogue of a pilot's "fly the airplane" — don't become a
second casualty.
