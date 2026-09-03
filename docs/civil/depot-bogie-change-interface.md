# LM3 Depot Bogie-Change Interface

This design-reference contract ties the LM3 underframe lifting hardware to the
main-heavy depot civil and equipment assembly. Both models consume
`lm3_bogie_change_datum()`; changing a jack centre on one side without changing
the other therefore fails the cross-domain geometry test.

It is a coordination baseline, not a certified lifting design. Vehicle mass
cases, asymmetric support cases, foundation reactions, reinforcement, column
capacity, controls integrity, proof loads, and the equipment supplier's exact
installation remain release inputs.

## Controlled geometry

| Interface | Design-reference value |
|---|---:|
| Rail gauge | 1,435 mm |
| LM3 car envelope | 16,500 × 2,850 mm |
| Bogie centre spacing | 12,300 mm |
| Jack-point longitudinal spacing | 11,200 mm |
| Jack-point transverse spacing | 2,360 mm |
| Lift-column transverse spacing | 4,400 mm |
| Inspection-pit clear envelope | 16,000 × 1,400 × 1,500 mm |
| Bogie extraction clear width | 5,000 mm |
| Nominal lift stroke reserved | 1,500 mm |

Coordinates use car centre as X/Y origin and top of rail as the local vertical
datum. The four lift heads are at X = ±5,600 mm and Y = ±1,180 mm. Lift-column
bodies are outside the car at Y = ±2,200 mm; retractable arms reach the vehicle
pads while preserving the pit and bogie-drop path.

## Assembly boundary

The rolling-stock side contains four underframe load spreaders, four replaceable
pad faces, surveyed J1–J4 targets, retained lifting-eye bosses, two towing and
rerailing lugs, and external recovery instruction plates. `LM3-BDY-P120` is the
packed car kit; `underframe-jacking-recovery-interface` is its installed review
state within the full mechanical-interface assembly.

The main-heavy depot side contains the reinforced pit base and edge beams,
running rails, four lift-column foundation/anchor pockets, supplier column
envelopes, retractable mechanically locked arms, four controlled lift heads,
two transverse extraction paths, transfer-table guide rails, a restrained bogie
parking zone, local controls, emergency stop, and trapped-key isolation. The
secondary and layup archetypes do not inherit overhaul lifting capability.

## Release sequence and hold points

1. Freeze the weighed vehicle load cases, centre-of-gravity envelope, allowable
   jack reactions, and permitted support combinations.
2. Release underframe load paths, pad drawings, weld maps, NDT, proof-load
   values, and the physical four-point interface gauge.
3. Complete site geotechnical work and the pit, foundation, drainage,
   reinforcement, settlement, and accidental-action calculations.
4. Freeze the synchronized lift and transfer-table suppliers, including stroke,
   mechanical locks, loss-of-level limits, controls integrity, emergency
   lowering, and rescue provisions.
5. Survey the installed rail and J1–J4 head coordinates with the same gauge used
   on the vehicle; record the as-built results against the asset IDs.
6. Prove no-load motion, mechanical locks, emergency stop and isolation, then
   conduct the approved staged proof and asymmetric-load tests.
7. Perform a complete bogie disconnect, lift, drop, transverse extraction,
   restraint, replacement, lowering, reconnection, brake test, and vehicle
   release rehearsal before operational acceptance.

The generated station product row `STN-DEP-P060` carries these acceptance gates.
Deployment structural, lifting-equipment, electrical-control, occupational
safety, and local approval records remain mandatory external evidence.
