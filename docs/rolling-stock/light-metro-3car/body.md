# Body structure — `light-metro-3car`

The body architecture is deliberately simple to manufacture in a
regional workshop: a welded carbon-steel primary structure with
bonded/bolted composite cladding and COTS passenger-facing modules.
The design avoids large aluminium extrusion dies, stainless body
pressings, and bespoke door/window/HVAC development.

## Architecture

Each 17.0 m car is split into four production zones:

| Zone | Construction | Function |
|---|---|---|
| Stepped underframe ladder | Cut/bend/weld S355 steel box and folded plate | Carries buff/compression, bogie pivots, battery boxes, coupler loads; drops through the centre door/PRM zone and rises over standard bogies |
| Side/roof spaceframe | S355 rectangular hollow section | Door posts, window rails, roof equipment rails, composite panel support |
| Composite exterior | Fire-rated glass-fibre or basalt-fibre sandwich panels | Weather skin, insulation, aerodynamics, livery surface |
| Interior cassette | COTS panels, seats, lights, grab rails, PIS, HVAC ducting | Passenger finish and replaceable equipment |

Steel is the certified load path. Composite panels are non-structural:
they may stiffen local skins, but crashworthiness, jacking, lifting,
coupler loads, and bogie loads are closed through the welded frame.

The CAD implementation follows the same hierarchy in
[`car_body.py`](../../../mechanical-py/src/osr_mech/rolling_stock/car_body.py):

| CAD subassembly | Included layers |
|---|---|
| `car_body_structure()` | Welded shell, 350 mm and ~10 m low-floor centre pan, 760 mm and ~3 m high-floor bogie-end decks, transition ramps/steps, side sills, raised bogie plinths, bogie sweep/drop envelopes, crossmembers, window posts, waist rails, end rings, anti-climber beams, roof cantrails, door portal posts and headers |
| `car_body_exterior()` | Solar-train exterior skin: glazing, door leaves, livery band, removable skirts, roof PV array, compact HVAC roof units |
| `car_body_interior()` | Under-seat battery strakes, longitudinal seats, PRM bays, grab poles, handrails, passenger information displays |
| `car_body_services()` | HVAC supply/return/drop ducts, LV/TCN cable trays, LED lighting, CCTV, intercoms, door harness loops, HV traction/PV routing, coolant pipes, battery fire vent paths |

`car_body()` returns the complete nested assembly. FreeCAD and PNG
review artifacts are generated from that source; they are not the
design authority.

## Primary steel structure

### Underframe

The underframe is a jig-welded ladder:

| Member | Section | Material | Notes |
|---|---|---|---|
| Side sill | 200 × 100 × 8 mm RHS | S355J2 or local equivalent | Continuous between end modules |
| Centre spine | 250 × 100 × 8 mm RHS | S355J2 | Battery-box and equipment support |
| Cross bearer | 160 × 80 × 6 mm RHS | S355J2 | 750 mm nominal pitch |
| Bogie bolster | Folded/welded 12 mm plate box | S355J2 | Machined centre-pivot insert after weld |
| Coupler pocket | 16 mm folded plate + crush can interface | S355J2 | EN 15227 energy absorber bolts on |
| Battery tray rail | 80 × 60 × 5 mm RHS | S355J2 | Under-seat module cassette support |
| Articulation adapter frame | 12 mm folded plate + machined inserts | S355J2 | Lower spherical joint, bellows clamp, and upper-link clevis datums |

The floor is not flat. The two centre doors per side and wheelchair
bay sit in a ~10 m low-floor zone at 350 mm above top-of-rail for
platform boarding. The end saloon zones rise to 760 mm over the
standard ~3 m bogies, with short interior steps and ramp panels
between the zones. The body sides therefore use a lowered side sill
through the centre door bay and raised plinth rails over the bogie
zones.

All primary welds are made in a rotating fixture so flat/horizontal
weld positions dominate. The v2 drawing pack assigns EN 15085 weld
classes per joint; the v1 assumption is CL1 for bolsters, coupler
pockets, and crash boxes, CL2 for side sills/cross bearers, CL3/CL4
for panel tabs and interior brackets.

### Articulation interface frames

Each inner car end carries an articulation adapter frame rather than a
simple drawbar bracket. The frame includes:

- underframe anchor casting for the semi-permanent articulated drawbar,
- machined land for the lower spherical bearing and anti-lift keeper,
- vertical anti-climb shear-key pockets beside the lower joint,
- upper clevis brackets for the twin roll-yaw-pitch stabilising links,
- bellows bolted clamp frame and replaceable nutplates,
- drain channel lands and a floor service-hatch aperture,
- separated HV/data/coolant/HVAC bracket datums for the energy-guidance
  routes through the gangway.

The articulation supplier owns the internal bearing, bellows,
turntable, and link details. The fabricator owns the steel adapter
frame, weld map, machined datum survey, corrosion protection, and shim
pack. See [`articulation.md`](articulation.md) for the motion envelope
and [`interfaces.md`](interfaces.md#inter-car-articulation-and-gangway)
for the trainline interface.

### Side frame

The side frame is a light spaceframe welded to the underframe:

- Door posts: 120 × 80 × 6 mm RHS.
- Window posts: 80 × 50 × 4 mm RHS.
- Waist rail: 100 × 50 × 5 mm RHS.
- Cant rail: 100 × 50 × 5 mm RHS.
- Roof bows: 80 × 40 × 4 mm RHS at 1 000 mm pitch.
- Equipment rails: bolted stainless inserts for HVAC, antennas,
  marker lights, CCTV, and cable trays.

Door openings are not cut from a finished shell. They are built as
open bays around the COTS door cassette so the door supplier's frame,
threshold, drainage tray, and emergency-release hardware install as
a single bolted module.

## Composite exterior panels

Exterior panels are bonded and mechanically retained to the steel
frame:

| Panel | Construction | Attachment |
|---|---|---|
| Side skin | 25-35 mm fire-rated GFRP or basalt-fibre sandwich | Structural adhesive + M6/M8 retained fasteners |
| Roof fairing | 20-30 mm composite sandwich | Bolted to roof bows; removable above HVAC/equipment |
| Nose/sensor cowl | Multi-part fiberglass (GFRP) cast kit over steel crash frame | Identical at both train ends; bolted, sacrificial, and replaceable; segmented heated RF-transparent end glass panes with LED headlamp/marker clusters |
| Skirts | Composite or aluminium removable panels | Quarter-turn service fasteners |
| Interior liners | EN 45545 HL2 FRP or phenolic panels | Clip/bolt to secondary rails |

The composite supplier owns laminate coupons, resin selection, fire
test evidence, and repair manuals. The OSR body drawing owns only
panel envelopes, edge radii, insert locations, grounding/bonding
points, and removal clearances.

The front and rear exterior ends use the same A/B-end fiberglass kit:
upper brow, left/right cheek casts, lower apron, lamp/service hatches,
and segmented backing-ring flanges over the steel crash frame. See
[`end-cowl.md`](end-cowl.md) for the cast split, laminate schedule,
mould/tooling rules, and glass/sensor service interfaces.

## COTS windows

Windows are bought as certified rail/bus glazing modules rather than
fabricated locally:

- Laminated safety glass to EN 15152 or equivalent.
- Typical opening: 900 × 1 200 mm.
- Bonded-in or gasketed cassette depending on supplier.
- Emergency ventilation only where required by the authority having
  jurisdiction; default HVAC assumes fixed glazing.
- Drainage path and adhesive bead are per supplier installation
  drawing, not re-engineered by OSR.

## COTS doors

Door modules are commercial off-the-shelf electric sliding-plug or
plug-outward rail doors:

- Clear opening: 1 250 mm × 2 000 mm.
- Electric actuation; no trainwide pneumatic door supply.
- Supplier-provided threshold, guide rail, controller, obstacle
  detection, emergency release, seals, and manual isolation.
- OSR provides 24 V DC / 110 V DC power, Ethernet/CAN-FD command,
  hardwired closed-and-locked loop, drainage, and mounting datum.

The preferred procurement pattern is to qualify two door suppliers
against the same envelope. The carbody must not depend on a unique
proprietary door pocket.

## COTS roof and passenger systems

The body reserves bolted envelopes for:

- Roof HVAC: one 20 kW nominal packaged unit per car, hot-climate
  variant for +50 °C ambient.
- LED lighting: 24 V DC rail-rated strip or troffer modules.
- PIS displays and speakers: off-the-shelf rail/bus units.
- CCTV: PoE cameras in serviceable composite housings.
- Intercom: COTS EN 50155 rail intercom stations.
- Seats: longitudinal rail/bus bench modules bolted to under-seat
  battery cover rails.
- Grab rails: stainless tube systems with off-the-shelf clamps.

HVAC, lighting, PIS, CCTV, intercom, seats, and grab rails are
procurement modules. OSR fixes the envelope, fastener grid, power
budget, data interface, fire rating, and maintainability clearance.
Supplier-neutral envelopes and evidence requirements live in
[`hardware/trainset-interiors/cots-catalogue.md`](../../../hardware/trainset-interiors/cots-catalogue.md).

The full interface map, including how the COTS modules join to the
fabricated steel/composite body, is in
[`cots-integration.md`](cots-integration.md).

## Floor

- 5-6 mm steel or aluminium deck panels over cross bearers.
- Removable hatches above battery and HV equipment zones.
- Phenolic or aluminium honeycomb floor boards in the saloon.
- Slip-resistant vinyl or rubber floor covering, EN 45545-2 R5.
- ~10 m low-floor centre door zone; ~3 m raised end decks over bogies.

## Corrosion protection

Steel primary structure receives:

- Shot blast to Sa 2.5.
- Zinc-rich epoxy primer.
- Seam sealer at composite/steel interfaces.
- Cavity wax in closed sections after weld inspection.
- Polyurethane topcoat where visible or exposed below floor.
- Drain holes in every closed bay that can collect condensation.

Composite/steel joints use isolation tape or coated inserts to avoid
galvanic corrosion where aluminium brackets or stainless fasteners
are present.

## Fire compliance

Every passenger-facing material must meet EN 45545-2 HL2 or the
deployment authority's accepted equivalent.

| Item | Requirement |
|---|---|
| Steel primary frame | Non-combustible; coating fire data required |
| Composite exterior panels | R1 HL2 or better |
| Interior panels | R1 HL2 or better |
| Floor covering | R5 HL2 or better |
| Seats | R7 HL2 or better |
| Cable insulation | R15/R24 HL2 or better |
| Door/window seals | R23 HL2 or better |

## v2 deliverables

- Welded frame FreeCAD assembly and 2D drawings.
- Flat pattern DXF for folded plates.
- Tube cut list with mitre angles and fixture datum references.
- Weld map with EN 15085 classes, WPS references, and inspection
  hold points.
- Composite panel envelope drawings and insert maps.
- Door/window/HVAC supplier interface drawings.
- Static proof-load and fatigue FEA report.
- EN 15227 crashworthiness simulation report.
