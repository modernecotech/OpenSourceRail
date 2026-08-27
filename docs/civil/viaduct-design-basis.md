# OSR Rapid Viaduct Kit — Design Basis

**Status:** controlled planning basis; not a construction design  
**Primary products:** OSR-Pi25 and OSR-Pi20 prestressed decked single-track beams
**Special products:** OSR-U25-SPECIAL acoustic/project-specific trough, OSR-US segmental U/box, and OSR-SP special crossing

## Catalogue boundary

Two identical 2.9 m-wide decked pi-beams share a single-column pier at the
same 3.5 m tangent track centres used at grade. Each beam has two stems beneath
the rail lines and a full-depth upper flange forming the structural track deck.
Separate 1 m outer walkway/barrier cassettes give a controlled 8.5–9.0 m
twin-track envelope. Pi20 and Pi25 come from one long-line mould with movable
stop ends. A 30 m beam is not in the catalogue.

| Product | Controlled use |
|---|---|
| `OSR-Pi25` | Tangent and broad-curve normal span; target bare mass 65–75 t |
| `OSR-Pi20` | Closure bays, junctions and utility avoidance; target bare mass 50–60 t |
| `OSR-U25-SPECIAL` | Project-specific acoustic/containment trough after transport, lift and structural release |
| `OSR-US` | 2.5–3.0 m match-cast segments where access or curvature prevents full-span erection |
| `OSR-SP` | Separately engineered I-girder, steel-composite, or segmental crossing over 30 m; turnouts and exceptional crossings |

The OSR-US review model places each 2.5–3.0 m chord on a surveyed circular
arc, with rotated match-cast joint planes and chord-following tendon corridors;
it is no longer represented by a straight full-span extrusion with markers.

The default Python geometry is `osr_mech.civil.decked_pi`; legacy troughs stay
in `osr_mech.civil.ugirder` as special products. Flange/stem proportions,
diaphragms, anchorages, tendons, lifting zones, reinforcement, fatigue,
derailment, vibration and rail–structure interaction remain supplier design
and independent-check releases.

## Actions and design situations

Use the deployment country's adopted standards and combinations. The design
must include the complete 12-axle train, a 16 t infrastructure axle allowance,
dynamic amplification, braking, traction, nosing, centrifugal force, wind on
empty and loaded trains, derailment/containment, collision, maintenance and
rescue vehicles, temperature, creep, shrinkage, fatigue, seismic/foundation
interaction, and every lifting, transport, temporary-bracing, and erection
stage. The machine-readable seed is
[`viaduct-load-model.toml`](viaduct-load-model.toml).

Decked pi sections require three-dimensional analysis for torsion, transverse
distribution, asymmetric loading, local flange/stem actions, end-zone
bursting, camber, creep, shrinkage, fatigue and staged prestress. Final
reinforcement, tendons, anchorages, bearings, foundations,
rail/bridge interaction, and temporary works require independent checking by
licensed bridge and geotechnical engineers.

## Geometry and constructability gates

- A straight 25 m full-span unit is preferred at radii of about 300 m or more.
- Below about 300 m, use Pi20, OSR-US, a shorter verified product, an I-girder deck,
  or realign. A 90 m system curve is exceptional elevated geometry.
- Four normal spans form one semi-continuous unit. Internal piers carry four
  bearings in one line; expansion-unit boundaries carry eight in two lines;
  end supports carry four. Link slabs/diaphragms, CWR interaction, temperature,
  braking, seismic and foundation flexibility require project analysis.
- Parapet/containment height is measured above the finished escape walkway,
  not above the structural soffit or pre-track floor.
- The trackform is local direct-fixation plinths over the waterproofed
  structural floor. A full structural topping is a project-specific acoustic
  or vibration option, not the default.
- The shared hollow/precast-shell cap is 6.5–7.5 m wide and targets 25–35 t.
- Foundation selection uses `foundation-catalog.toml`. Deep-element geometry
  and cost require actual site length; no six-metre placeholder is permitted.
- Foundations and accepted beam stock are held 10–15 bays ahead of erection.

Automated catalogue checks live in `osr_mech.civil.viaduct`. Passing them is
necessary but not sufficient for design release.

## Minimum release evidence

The release package must close survey and utilities, ground model, design
basis and combinations, global and local analysis, prestress/reinforcement,
fatigue and durability, bearings and movement, rail/bridge interaction,
drainage and egress, transport/erection, first-article testing, independent
check, and deployment-authority approvals.
