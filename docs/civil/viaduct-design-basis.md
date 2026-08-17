# OSR Rapid Viaduct Kit — Design Basis

**Status:** controlled planning basis; not a construction design  
**Primary product:** OSR-U25 full-span prestressed single-track U-trough  
**Closure product:** OSR-U20  
**Exceptional products:** OSR-US segmental U/box and OSR-SP special crossing

## Catalogue boundary

Two identical single-track troughs share a single-column pier. The reference
clear trough width is 4.5 m, external envelope is 4.9 m, track centres are
5.3 m, and the normal span is 25 m. A 20 m unit uses the same principal mould
with adjustable stop ends. A 30 m full-span unit is only a planning option and
requires a released transport route, lifting analysis, erection plant, and
supplier structural design. Anything over 30 m is not the same product.

| Product | Controlled use |
|---|---|
| `OSR-U25` | Tangent and broad-curve normal span |
| `OSR-U20` | Closure bays, junctions, constrained geometry |
| `OSR-US` | 2.5–3.0 m match-cast segments where access or curvature prevents full-span erection |
| `OSR-SP` | Separately engineered I-girder, steel-composite, or segmental crossing over 30 m; turnouts and exceptional crossings |

The Python geometry in `osr_mech.civil.ugirder` is a clearance and quantity
envelope. Flanges, haunches, diaphragms, bearing/anchorage zones, tendon
corridors, lifting zones, drainage, containment, cable routes, and the escape
ledge are coordination placeholders until a supplier design is independently
checked.

## Actions and design situations

Use the deployment country's adopted standards and combinations. The design
must include the complete 12-axle train, a 16 t infrastructure axle allowance,
dynamic amplification, braking, traction, nosing, centrifugal force, wind on
empty and loaded trains, derailment/containment, collision, maintenance and
rescue vehicles, temperature, creep, shrinkage, fatigue, seismic/foundation
interaction, and every lifting, transport, temporary-bracing, and erection
stage. The machine-readable seed is
[`viaduct-load-model.toml`](viaduct-load-model.toml).

Open U sections require three-dimensional analysis for torsion, asymmetric
loading, distortion, end-zone bursting, camber, creep, shrinkage, and staged
prestress. Final reinforcement, tendons, anchorages, bearings, foundations,
rail/bridge interaction, and temporary works require independent checking by
licensed bridge and geotechnical engineers.

## Geometry and constructability gates

- A straight 25 m full-span unit is preferred at radii of about 300 m or more.
- Below about 300 m, use OSR-US, a shorter verified product, an I-girder deck,
  or realign. A 90 m system curve is exceptional elevated geometry.
- Interior simply supported piers carry eight bearings in two longitudinal
  rows; end supports carry four.
- Parapet/containment height is measured above the finished escape walkway,
  not above the structural soffit or pre-track floor.
- The trackform is local direct-fixation plinths over the waterproofed
  structural floor. A full structural topping is a project-specific acoustic
  or vibration option, not the default.
- Monopiles/large bored shafts are preferred only where geotechnical,
  overturning, seismic, durability, and constructability checks release them.

Automated catalogue checks live in `osr_mech.civil.viaduct`. Passing them is
necessary but not sufficient for design release.

## Minimum release evidence

The release package must close survey and utilities, ground model, design
basis and combinations, global and local analysis, prestress/reinforcement,
fatigue and durability, bearings and movement, rail/bridge interaction,
drainage and egress, transport/erection, first-article testing, independent
check, and deployment-authority approvals.
