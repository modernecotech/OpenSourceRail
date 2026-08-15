# One-metre clip-on fiberglass body — `LM3-BDY-160`

The train exterior is a replaceable, non-structural weather skin made from
simple fiberglass modules on a **1,000 mm longitudinal pitch**. The welded
S355 underframe, side posts, door portals, window carriers, roof bows, end
rings, anti-climbers, and crash structure remain the certified load path.

Each 16.5 m car has sixteen full 1 m cladding bays between two 250 mm steel
end-ring transitions. A three-car train therefore uses 144 main modules:
96 side modules and 48 roof modules. Solid, window-edge, door-edge, and roof
parts share the same mould width, clip datums, trim datum, seals, and repair
method. CNC trimming creates the aperture variants after moulding.

## Controlled geometry

| Item | Design value |
|---|---:|
| Longitudinal pitch | 1,000 mm |
| Finished module width | 994 mm |
| Dry joint | 6 mm replaceable EPDM compression seal |
| Nominal sandwich depth | 28 mm |
| Bays per 16.5 m car | 16 |
| Side modules per car | 32 |
| Roof modules per car | 16 |
| Main modules per trainset | 144 |
| End transition outside module grid | 250 mm at each car end |

The parametric source is
[`modular_fiberglass_body.py`](../../../mechanical-py/src/osr_mech/rolling_stock/modular_fiberglass_body.py).
It generates side modules with the released door/window cuts, roof modules,
clip hardware, anti-lift retention, and joint gaskets. The machine-readable
module and assembly manifest is generated under
[`mechanical-py/catalog/modular-fiberglass-body`](../../../mechanical-py/catalog/modular-fiberglass-body/).

## Retention and sealing

Every module hangs on an asymmetric keyed upper hook and closes onto captive
over-centre clips. An independent anti-lift retainer prevents a panel leaving
the vehicle if a clip is not fully latched. Clip witness marks are visible
from the service side. The fasteners remain captive when open.

The weather joint is a dry, replaceable EPDM compression gasket over a drained
secondary rail. Production adhesive is not used between the body module and
frame, so there is no cure delay and a damaged 1 m section can be exchanged.
Adhesive remains permitted inside a supplier-controlled fiberglass sandwich,
for glazing, and at released non-service seams in the separate end cowl.

The clip, insert, rail, and backing-plate loads still require calculation and
first-article proof. The release pack must include fire/smoke/toxicity evidence,
laminate coupons, insert pull-out tests, clip proof load, fatigue/vibration,
water ingress, aerodynamic pressure, and timed removal/refit evidence.

## One-day exterior-body route

Six two-person crews work on three released frames in parallel, two crews per
car. All parts are moulded, trimmed, painted, labelled, gasketed, and kitted
before the frames enter the body station.

| Seq | Activity | Elapsed | Crews | Release evidence |
|---:|---|---:|---:|---|
| 10 | Verify frame datums and kit revisions | 0.5 h | 3 | Frame/module map signed |
| 20 | Fit dry seals and inspect clip receptacles | 1.0 h | 6 | Seals continuous; drains open |
| 30 | Hang and latch both side skins | 3.0 h | 6 | All clip witness marks visible |
| 40 | Hang and latch roof modules | 1.5 h | 6 | Anti-lift retainers closed |
| 50 | Fit closures, skirts, labels, and earth bonds | 1.0 h | 6 | Continuity and access checks |
| 60 | Water/rattle test and close snags | 1.0 h | 3 | Signed eight-hour body release |
| **Total elapsed** | | **8.0 h** | | |

This is an exterior-body installation claim, not a claim that an uncertified
train can go from bare steel to passenger service in one day. Doors, glazing,
roof equipment, interiors, traction equipment, batteries, bogies, static and
dynamic commissioning, homologation, and first-article testing remain their
own controlled operations.

## Cost and plant effect

The repeated short mould removes the full-car mould, large cure fixture, long
bonding operation, and bonded-panel rework allowance from the baseline. The
CAPEX source therefore uses a 28% local assembly allowance, a **$900 k**
three-car trainset planning unit, and **$60 k per car** production-plant setup
allowance. The high plant sensitivity is $120 k per car. These remain
planning values until supplier quotes and timed first-article builds replace
them.
