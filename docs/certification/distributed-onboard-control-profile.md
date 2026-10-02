# Distributed Onboard Control Profile

**Status:** development target; not the deployable pilot baseline.

This profile reduces dependence on centralised wayside computation and permits
continued route *selection* during a communications outage. It does not remove
the safety functions commonly implemented by interlocking, ATS or ATP. Those
functions may move between onboard and distributed equipment only after a
hazard analysis, independent assessment and deployment approval demonstrate
equivalent or better safety.

The deployable reference remains the conservative sectional-authority profile
in [pilot-signalling-profile.md](pilot-signalling-profile.md).

## Executable train-centred milestone

[RFC 0033](../rfcs/0033-tacs-runtime-and-resource-control.md) and the
[TACS assurance package](../../engineering/assurance/tacs/README.md) use the
existing committed interlocking MA and ATP/ATO/brake components through thin,
authenticated process hosts. The reference includes two train agents, three
static voters, point I/O and two station/charging interfaces. Generated software
evidence remains unreviewed. HIL, measured braking/integrity, field recovery,
independent assessment and a named approved installed bundle are required to
change the deployable profile. The conservative pilot remains the default.

## Three independent route inputs

The onboard selector compares:

1. a signed, versioned plan stored onboard;
2. route and position inferred from onboard sensors against immutable topology;
3. an authenticated network command from operations control.

An input is eligible only while trusted, fresh and internally valid. Exactly
matching route, next-section and plan-epoch values from two eligible sources
are required. If all three disagree, only one source is eligible, or the two
available sources disagree, the result is `Hold`. A network outage can produce
`OnboardAutonomous` only when the onboard plan and sensor-derived input agree.

Route selection is not permission to move. Every accepted selection carries an
explicit `movement_authority_required` condition and is passed through the
independent authority, localisation, speed-envelope and emergency-brake path.

## Functions that must remain

Any implementation must retain, even if equipment placement changes:

- movement-authority generation and expiry;
- train separation and opposing-move exclusion;
- route locking and detected/locked point position;
- occupancy or safety-integrity localisation;
- overspeed supervision and emergency braking;
- intrusion/obstacle gates required by the operating envelope;
- degraded-mode supervision, event recording and accountable override.

“Eliminating interlocking/ATS/ATP” is therefore interpreted as reducing
duplicated central equipment, not deleting their safety outcomes. A model,
sensor fusion algorithm or radio link cannot independently claim equivalence.

## Narrow single-track operation

Short single-track sections are permitted only on exclusive guideway and with
passing loops at passenger stops or protected portals. Entry requires locked
route exclusivity, detected points, clear occupancy, a valid authority and a
proved timetable/degraded-mode strategy. Loss of required state prevents entry;
it does not rely on two trains negotiating informally over the radio.

## Recovery sites and shunt robots

The reference planner reserves a recovery siding at or immediately beyond
every third passenger station. Each site has a protected mainline interface,
independent stop detection and remote isolation. Its small shunt robot is
remote-controlled, has local emergency stop and fail-held braking, and cannot
autonomously enter the main line. Radio loss inhibits traction. Mainline entry,
towing and return to service remain controlled recovery operations.

## Evidence gates

Before this profile can replace any pilot equipment, the project must freeze
the safety allocation and demonstrate source independence/common-cause
analysis, target-hardware timing, localisation accuracy, radio-loss behaviour,
point and occupancy interfaces, cybersecurity, HIL fault injection, shadow
running, representative field trials, recovery drills and independent safety
assessment. The deterministic report records design coherence; it does not
close these physical or regulatory gates.
