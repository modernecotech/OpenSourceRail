# S3 — Incident handling

**Scope:** dispatcher response to in-service incidents. Covers all
six categories from RFC 0013 §7 (I1 self-recovery → I6 mass
casualty).

**Cross-refs:** RFC 0013 §7, [`osr-event-recorder`](../../../crates/osr-event-recorder/),
[`osr-occ`](../../../crates/osr-occ/).

## Rules

### S3.1 — I1 single-train fault

For a single-train fault that clears within one dwell (lost
ATO link recovers, door-close recycle succeeds), the
dispatcher logs the event to `osr-event-recorder`, notifies
the depot for trend analysis, and issues no passenger PA
unless service-minute impact exceeds 2 minutes.

**Why:** a PA on every blip trains passengers to ignore PAs,
which is bad when a real PA matters. The 2-minute threshold
keeps announcements credible.

### S3.2 — I2 service disruption

For a service disruption lasting more than 5 minutes (trainset
unable to move under own power, signalling fault requiring
staff talk-through), the dispatcher initiates the rescue-
coupling protocol (D7), issues a passenger PA every 3
minutes, and logs a timetable recovery plan (short-turns,
skip-stops) to the shift log.

**Why:** disruptions longer than a few minutes need both a
technical response (rescue) and a communications response
(PA cadence). Running them as a single protocol reduces the
chance that one is forgotten while the dispatcher focuses on
the other.

### S3.3 — I3 short safety event

For a short safety event (EB triggered, SPAD, overspeed trip),
the dispatcher orders the driver not to move until the event
recorder is preserved, initiates a 72-hour investigation with
a minute-by-minute timeline, and holds the trainset out of
service pending the investigation outcome.

**Why:** moving a trainset after an EB contaminates the event
record with recovery data and obscures the initiating
sequence. The 72-hour window matches RFC 0013's safety-
case evidence retention requirement.

### S3.4 — I4 passenger injury

For a passenger injury (reported by driver, station staff, or
passenger emergency intercom), the dispatcher places a medical
call, coordinates with station staff for a station handover
of the casualty, and files the passenger-injury report form
within 24 hours.

**Why:** the injured passenger needs a named owner on the OCC
side so the ambulance arrives at the right platform. The
24-hour form is the insurance record, which is expensive to
reconstruct from memory.

### S3.5 — I5 collision or derailment

For a collision or derailment, the dispatcher orders a full
line shutdown, notifies the National Rail Safety Authority
within 2 hours (or the equivalent regulator per the
deployment), and issues an incident-site preservation order
(no movement, no cleanup) until the NRSA investigator
releases the site.

**Why:** the first instinct after a major incident is to clear
the site to restore service — which destroys the evidence
the regulator needs to determine cause. The preservation
order makes the cost of not clearing explicit.

### S3.6 — I6 mass casualty

For a mass-casualty event (fire, explosion, structural
failure), the dispatcher activates the evacuation protocol
for the affected stations, escalates to emergency services
(fire + ambulance + police), notifies NRSA and regional
media liaisons, and coordinates shutdown boundaries to
contain the incident.

**Why:** mass-casualty response is a multi-agency operation
where the rail dispatcher is one voice among many. The
role is to own the *rail* side of the response — tracks
de-energised, trains stopped, stations evacuated — and
hand off everything else to the authorities trained for
it.

### S3.7 — Onboard battery fire or off-gas alarm

On a confirmed battery-compartment event, the dispatcher verifies the
reported car/module/string identity, charge inhibit, HV isolation request,
mist-system status, train movement-safety assessment, nearest usable platform,
platform evacuation route, and emergency-service rendezvous point.

When `osr-fire-safety` requests a controlled stop and the train remains safe
to move, OCC protects the route to the nearest suitable platform, clears that
platform, prevents another train entering it, and prepares immediate door
release/evacuation on the side approved by the incident assessment. OCC does
not command the train to continue beyond that platform.

When immediate danger, loss of containment, crash damage, essential-control
loss, unsafe route, or emergency-brake output is present, OCC accepts the
immediate stop, protects both directions, isolates nearby charging equipment,
and directs evacuation only after trackside hazards and the safer egress side
are established. The water-mist indication is treated as propagation-control
status, not proof that the cell event is extinguished.
