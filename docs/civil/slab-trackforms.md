# Ballastless Slab Trackform Designs

This note records the OSR planning-grade slab trackforms for urban
at-grade and elevated sections. The parametric CAD source lives in
[`mechanical-py/src/osr_mech/civil/slab.py`](../../mechanical-py/src/osr_mech/civil/slab.py).

The designs are reference envelopes for cost, clash, fabrication, and
constructability review. Deployment partners still need local structural
checks for concrete grade, reinforcement, geotechnical support, drainage,
stray-current control, thermal movement, seismic load, flood/scour, and
product acceptance of the direct-fixation fasteners.

## At-Grade Urban Slab

| Item | Reference value |
|---|---:|
| Trackform | Double-track ballastless slab with continuous rail plinths |
| Panel length | 6.0 m |
| Overall panel width | 6.2 m |
| Track-centre spacing | 3.5 m |
| Base slab thickness | 280 mm |
| Rail plinth width | 420 mm |
| Rail plinth height above base slab | 220 mm |
| Direct-fixation pitch | 650 mm |
| Rail seats per 6 m panel | 40 |
| Nominal concrete per 6 m panel | 12.6 m3 |

Use the at-grade slab where the corridor is in a street, median,
segregated urban right of way, station approach, depot throat, or other
place where ballast dust, tamping possessions, and loose aggregate are
unwanted.

The slab uses two edge troughs for drainage, low-voltage/data routing,
and maintainable cable access. The direct-fixation plinths are continuous
so baseplates can recover small alignment tolerances without breaking out
concrete.

## Elevated Deck Slab

| Item | Reference value |
|---|---:|
| Trackform | Single-track U-girder topping slab with continuous rail plinths |
| Panel length | 6.0 m |
| Overall panel width | 3.2 m |
| U-girder internal width compatibility | Fits 3.5 m internal trough |
| Base slab thickness | 220 mm |
| Rail plinth width | 380 mm |
| Rail plinth height above base slab | 160 mm |
| Direct-fixation pitch | 650 mm |
| Rail seats per 6 m panel | 20 |
| Nominal concrete per 6 m panel | 5.0 m3 |

Use one elevated deck slab per single-track U-girder. A double-track
elevated section therefore uses two parallel girder/slab assemblies unless
a deployment partner replaces the reference U-girder with a certified
double-track viaduct section.

The elevated slab is narrower and thinner than the at-grade panel because
the U-girder carries the main structural depth. The slab provides direct
fixation, local tolerance recovery, drainage/cable troughs, and a
maintainable track support surface.

## Fabrication And Installation Rules

- Keep the 6 m slab module for ordinary urban geometry; use closure pours
  only at turnouts, station ends, curves that require local survey
  correction, and transitions to bridge/special spans.
- Cast embedded inserts, earthing/bonding points, drainage scuppers, and
  lifting anchors in the precast yard.
- Require surveyed casting beds and a dimensional QA record for every
  batch.
- Use adjustable baseplates on all running rails.
- Keep prestressed elevated girders conservative; recycled aggregate and
  aggressive low-carbon mixes can be used first in non-prestressed slabs,
  piers, pile caps, and station modules.
- Treat direct-fixation pads, anchors, and baseplates as replaceable
  wear/interface parts, not as buried civil structure.

## Cost Model Link

These slab designs support the current civil planning floors:

| Civil class | Planning floor |
|---|---:|
| At-grade ballastless slab | 3.0 M USD/route-km |
| Elevated guideway with deck slab | 12.0 M USD/route-km |
| Bridge/water-crossing guideway | 18.0 M USD/route-km |

The elevated number is a repetitive-package floor. Short elevated stubs,
many elevated stations, soft-ground foundations, deep utilities, tight
curves, or repeated special spans should carry a local premium.
