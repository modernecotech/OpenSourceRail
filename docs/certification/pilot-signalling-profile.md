# Pilot Signalling Profile

`OSR-PILOT-1` is the conservative deployment baseline for a segregated pilot.
It separates what can be exercised now from the research target so that a city
does not need to accept novel moving-block authority on day one.

The machine-readable source is
[`lib/templates/signalling.toml`](../../lib/templates/signalling.toml) under
`profiles.osr-pilot-1`.

## Live Pilot Boundary

| Function | Pilot treatment |
|---|---|
| Occupancy | Independently detected by assessor-accepted axle counters or track circuits. A loss, disagreement or unknown state is occupied. |
| Movement authority | Conservative wayside sectional/fixed-block authority. No authority extends beyond independently proved clear and locked sections. |
| Points | Independently detected, locked and fail-safe before authority is issued. |
| OSR ATP | Active only inside the conventional sectional authority and selected safety-controller boundary. |
| OSR ATO | Supervised; ATP and the conventional authority remain the hard limit. |
| Consensus and onboard MA | Recorded, compared and alarmed in shadow mode; unable to drive a safety output. |
| Right of way | Segregated pilot only, with local operating rules and independently assessed degraded modes. |

The application host is not the safety controller. The deployment must freeze
a qualified safety channel using the
[controller selection gate](../../control-electronics/safety-controller-selection.md),
including watchdog, power, I/O, common-cause, environmental and HIL evidence.

## Staged Transition

1. **Shadow:** compare OSR position, consensus state and calculated authority
   against the conventional pilot authority without controlling movement.
2. **Supervised sectional:** permit OSR ATO under active ATP, while independent
   occupancy and sectional movement authority remain authoritative.
3. **Sectional GoA 4:** remove the onboard attendant only after operations,
   obstacle detection, evacuation, communications and safety assessment close.
4. **Moving-block trial:** exercise distributed authority on a closed test
   track with independent fallback and an assessor-approved test plan.
5. **Revenue moving block:** only after machine-checked refinement or an
   assessor-accepted equivalent argument, full bounded-proof evidence,
   selected hardware qualification, HIL/field results and national authority
   approval.

No stage inherits approval from the previous stage automatically. Each city
must record its own hazards, authority, configuration, evidence and rollback
criteria. The target profile in the template is a research configuration, not
a construction or revenue-service release.
