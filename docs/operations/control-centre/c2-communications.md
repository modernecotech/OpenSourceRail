# C2 — Communications

**Scope:** radio discipline, PA authority, external-party
notification (NRSA, emergency services, press liaison).

**Cross-refs:** [`osr-t2g`](../../../crates/osr-t2g/),
[`osr-pis-onboard`](../../../crates/osr-pis-onboard/),
[`osr-pis-station`](../../../crates/osr-pis-station/), RFC 0013 §4.5 C2.

## Rules

### C2.1 — Radio discipline

Radio transmissions open with call sign (dispatcher + unit
being called), cover one topic per transmission, and use
the standard phraseology (Proceed / Stop / Hold / Recall /
Rescue). Ambiguous phrases ("kinda go" / "maybe stop") are
rephrased on the spot.

**Why:** radio is the fallback when everything else is
broken. Standard phraseology removes ambiguity when stress
is high and accents vary across a multi-nationality
operator workforce.

### C2.2 — PA authority

PA authority is partitioned: the dispatcher owns network-
wide PA (all stations or all trains simultaneously), station
staff own station-local PA, drivers own in-train PA. A role
may not make a PA outside its partition without handover.

**Why:** overlapping PAs produce cacophony at the station
where a passenger trying to understand one announcement
gets cut off by another. The partition matches authority to
audience.

### C2.3 — NRSA notification

NRSA notification windows: Category I5 (derailment, collision)
within 2 hours; Category I6 (mass casualty) immediately;
Categories I3 and I4 within 24 hours; I1 and I2 are
consolidated into the monthly safety summary. The supervisor
makes the call; the dispatcher does not.

**Why:** NRSA windows are regulatory — missing them is an
operator-level finding. Centralising on the supervisor
ensures each window is tracked once, not N times by N
dispatchers each assuming the other called.

### C2.4 — Emergency services coordination

Emergency-services coordination (fire, ambulance, police)
is through the OCC supervisor as the single point of
contact. The dispatcher may make the initial 112 / 999 call
(per deployment dialling) but hands the ongoing liaison to
the supervisor within the first 5 minutes.

**Why:** fire chiefs and ambulance incident commanders need
one rail-side point of contact; a dispatcher juggling
services calls and train dispatching does neither well. The
handover within 5 minutes keeps the initial speed without
compromising continuity.

### C2.5 — Press and social media

Press and social-media statements are made only by an
authorised operator-level spokesperson (CEO, press officer,
or nominated deputy). OCC staff do not make public
statements, including on personal social media, about
incidents in progress or under investigation.

**Why:** in-progress incident statements by line staff
contradict themselves (because information is incomplete)
and are quoted against the operator for years. The
centralised spokesperson is the standard mitigation.

### C2.6 — International coordination

Incidents involving foreign nationals or cross-border
operations (rare in Samawah but possible in other
deployments) are coordinated through the supervisor with a
qualified translator on the bridge, including for consular
notifications.

**Why:** consular notifications and cross-border regulator
contacts have specific diplomatic protocol that is outside
the dispatcher's remit. The supervisor + translator
pairing is the compensating control.
