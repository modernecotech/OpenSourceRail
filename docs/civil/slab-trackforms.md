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

Long open, machine-accessible corridors use a continuously slipformed slab by
default. The table below defines the six-metre single-track ST6 product kept
for constrained streets, utility crossings, short possessions, flood-prone
and replaceable zones. Both methods retain the same controlled track support
section and concrete quantity basis; a project method-zone schedule determines
panel counts.

| Item | Reference value |
|---|---:|
| Trackform | OSR-ST6 single-track transportable panel; two rows form double track |
| Panel length | 6.0 m |
| Overall panel width | 2.9 m |
| Track-centre spacing | 3.5 m |
| Base slab thickness | 250 mm |
| Rail plinth width | 380 mm |
| Rail plinth height above base slab | 160 mm |
| Direct-fixation pitch | 650 mm |
| Rail seats per 6 m panel | 20 |
| Nominal concrete per 6 m panel | 5.08 m3 |
| Planning bare panel mass | 12.7 t |

Use ST6 where the corridor is in a constrained street, utility or transition
zone, short possession, flood-prone location, station interface, depot throat, or other
place where ballast dust, tamping possessions, and loose aggregate are
unwanted.

The slab uses two edge troughs for drainage, low-voltage/data routing,
and maintainable cable access. The direct-fixation plinths are continuous
so baseplates can recover small alignment tolerances without breaking out
concrete.

## Elevated Deck Slab

| Item | Reference value |
|---|---:|
| Trackform | Local direct-fixation plinths over thin non-structural alignment layer |
| Panel length | 6.0 m |
| Overall alignment-layer width | 2.7 m |
| Deck compatibility | Fits the 2.9 m OSR-Pi20/Pi25 flange |
| Alignment layer thickness | 40 mm; may be omitted by project design |
| Rail plinth width | 380 mm |
| Rail plinth height above base slab | 160 mm |
| Direct-fixation pitch | 650 mm |
| Rail seats per 6 m panel | 20 |
| Nominal concrete per 6 m panel | 1.38 m3 |

Use one elevated trackform run per single-track Pi-beam. A double-track
elevated section therefore uses two parallel Pi-beam/trackform assemblies.

The Pi-beam upper flange is the structural deck. The alignment layer provides local
tolerance recovery only and may be omitted where surveyed casting plus
adjustable baseplates can recover rail geometry. A full-width reinforced or
floating slab is reserved for locations where a vibration/noise and structural
study justifies its dead weight.

The cable/drainage trough is installed on the inner/non-egress side. The
separate outer 1.0 m walkway/barrier cassette remains clear of service covers,
cabinets, screen posts and other permanent obstructions.

## FreeCAD Scene Renders

The slab trackforms are shown below in station context with driverless
rolling stock and the station access elements that affect civil cost.

| At-grade ballastless station track | Elevated deck station track |
|---|---|
| ![At-grade ballastless station track with driverless train](../screenshots/stations/freecad-at-grade-station-track-train.png) | ![Elevated deck station track with driverless train](../screenshots/stations/freecad-elevated-station-track-train.png) |

The source scene document is
[`mechanical-py/catalog/freecad/station-scenes.FCStd`](../../mechanical-py/catalog/freecad/station-scenes.FCStd)
and is regenerated with
[`mechanical-py/scripts/freecad_station_scenes.sh`](../../mechanical-py/scripts/freecad_station_scenes.sh).

## Fabrication And Installation Rules

- Slipform long accessible runs over the released machine-controlled
  formation. Keep the 6 m ST6 module for constrained and replaceable zones;
  use closure pours only at turnouts, station ends, curves that require local
  survey correction, and transitions to bridge/special spans.
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

These slab designs feed the generated civil planning contract:

| Civil class | Design-derived target | Retained benchmark |
|---|---:|---:|
| At-grade ballastless slab | 2.584 M USD/route-km | 3.0 M USD/route-km |
| Elevated guideway with local-plinth trackform | 9.748 M USD/route-km | 12.0 M USD/route-km |
| Bridge/water-crossing guideway | 18.0 M USD/route-km | 18.0 M USD/route-km |

The active values come from
[`civil-cost-model.toml`](../../lib/templates/civil-cost-model.toml) and are
planning targets, not tender or turnkey EPC estimates. Build the project
estimate from
[`viaduct-quantity-cost-model.toml`](viaduct-quantity-cost-model.toml) plus
site rates, utilities, access, risk, programme, independent checking, and
contingency. Short elevated stubs, stations, soft ground, deep utilities,
tight curves, or repeated special spans carry project-specific premiums.
