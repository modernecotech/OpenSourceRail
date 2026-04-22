# T3 — Passenger incidents

**Scope:** station-level response to passenger-side incidents —
medical, behavioural, fare dispute, lost property.

**Cross-refs:** RFC 0013 §§4.3 T3 + §7 incident categorisation.

## Rules

### T3.1 — Medical

On a medical incident, staff render first aid to the level of
their training, request emergency services via the OCC (who
calls I4 per S3.4), and preserve a 3 m area around the
casualty clear of other passengers.

**Why:** first responder staff don't diagnose — they stabilise
and wait. The clear area is both dignity for the casualty
and room for ambulance crew to work when they arrive.

### T3.2 — Behavioural / altercation

On an altercation or threatening behaviour, staff de-escalate
verbally, call transit security (where provided by the
deployment) or local police, and log the incident to the
station SCADA event log. Staff do not physically intervene
except to protect an identified victim.

**Why:** station staff are not trained for physical
intervention and are usually outnumbered. De-escalation plus
summoning trained responders is the evidence-based
protocol.

### T3.3 — Fare dispute

On a fare dispute at the gate, staff do not debate the fare
at the gate — they issue a supplement ticket or a dispute
slip and direct the passenger to the documented appeal
route (station office or online). The gate is cleared
within 30 s.

**Why:** a fare dispute at the gate blocks every passenger
behind. The dispute process happens off the critical path;
the passenger is neither presumed guilty nor let through
free.

### T3.4 — Lost property

Lost-property items are logged to the station log with
description, finder, and time, secured in the station
office locker for 30 days, and entered into the network
lost-property database accessible to other stations. After
30 days, items are donated or disposed of per deployment
policy.

**Why:** passengers tracking lost items often call or visit
more than one station. The network database makes the find
discoverable from any station; the 30-day ceiling keeps
the locker from filling with old umbrellas.

### T3.5 — Child separated

On a child-separated-from-caregiver report, staff issue a
platform PA with description, initiate CCTV review from the
last known time and place, and notify the OCC within
5 minutes if the child is not found. Station exit gates are
watched manually until the child is located.

**Why:** separated children are found most often within the
first 10 minutes. The staged response (PA → CCTV → OCC
escalation) scales effort to duration without burning the
network on a 2-minute reunion.
