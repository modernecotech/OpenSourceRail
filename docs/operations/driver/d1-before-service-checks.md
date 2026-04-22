# D1 — Before-service checks

**Scope:** actions the driver performs at the depot before the
first revenue move of a shift.

**Time budget:** ≤ 10 minutes on an in-service trainset.
A trainset with a red fault from the previous shift is referred
to maintenance without a driver attempt.

**Cross-refs:** RFC 0008 §3.4 (cab), RFC 0013 §4.1, safety-case
G4.1 (osr-atp correctness), G4.2 (osr-brake correctness), G4.3
(osr-vigilance correctness).

## Rules

### D1.1 — Power-on sequence

On entering the cab, the driver powers up in the order
`cab isolator ON → DMI power button → wait for green "ready" banner`.

**Why:** the cab isolator gates the 24 V DC rail that feeds the
DMI and the master controller; powering the DMI first on a dead
isolator produces a red bus-fault on the event recorder that
looks like a real fault during later investigation.

### D1.2 — Brake test on the pit

With the trainset over the depot pit, the driver runs
`DMI → Pre-service → Brake test`. The test actuates service +
emergency brake and reports pass/fail within 60 s.

**Why:** the electromagnetic disc brake is self-monitoring, but
the stuck-caliper failure mode only surfaces under commanded
actuation. The pit position lets depot maintenance observe
caliper motion from below during the first test of the shift.

### D1.3 — Vigilance test

On the DMI prompt, the driver acknowledges within the displayed
5 s window, then intentionally misses the next prompt —
confirming `osr-vigilance` escalates Nominal → Warning →
Tripped and applies emergency brake within the 5 s warning
window.

**Why:** vigilance is one of the five independent brake-apply
sources (RFC 0005 §6.1 O4). If the driver's ack loop doesn't
reach `osr-vigilance`, the train must not leave depot — this
is the only pre-service test that exercises the full loop.

### D1.4 — Door-interlock test

The driver issues `open → close` on every car via the DMI.
Every door must close within 6 s and report green-interlocked
on the DMI mimic diagram.

**Why:** a stuck-open door at revenue departure is a Cat I2
disruption (RFC 0013 §7). Testing all 24 doors at depot catches
the small fraction that jam after overnight thermal soak.

### D1.5 — Event-recorder handshake

The DMI shows an `event-recorder: green` indicator. Driver
confirms; no further action.

**Why:** if the event recorder is not logging, an in-service
incident produces no investigable trace. The Cat I3 / I4 / I5
evidence chain depends on a known-good recorder from service
start.

### D1.6 — Cab-to-cab confirmation

If the opposite cab is occupied simultaneously (shift overlap),
the driver confirms over intercom that only one master
controller is armed. The DMI shows a red banner if both cabs
arm.

**Why:** master-controller ambiguity is a rulebook violation
flagged in the event recorder; the intercom check catches it
before the DMI banner.

### D1.7 — Defect reporting

Any failure of D1.1–D1.6 is logged via `DMI → Fault → Report`
and the trainset is returned to maintenance before departure.
The driver does not attempt a workaround on any D1 failure.

**Why:** every failure mode D1 exercises is safety-relevant.
Workarounds establish precedent; the rulebook stays strict.
