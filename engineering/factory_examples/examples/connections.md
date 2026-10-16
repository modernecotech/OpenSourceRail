# Factory fabrication interfaces — iteration 3

This extends the mechanical and civil examples together. Original models and failed cases remain available. Two additional native models develop a perforated/diaphragm-stiffened strongback end and a retained locator-button coupon. These are preliminary fabrication concepts, with no physical release.

## Grip spacing and strongback layout

The baseline 45 mm strand pitch clashes with the candidate 50 mm grip bodies by 5.0 mm. The 60 mm-pitch candidate gives 10.0 mm body clearance against a 5 mm research allowance. Side cover to the 15.2 mm clearance envelope is 52.4 mm. This does not qualify concrete cover, the exact strand/grip combination or jack-nose access.

The new end box is 4 m across, 900 mm deep in the stressing direction and 1.3 m high, with 40 mm outer plates, 20 mm internal diaphragms and 48 aligned 22 mm clearance holes in each stressing face. Return-rail stubs are raised to the initial tendon centroid. Strongback plate holes are actual native boolean cuts; the grip cylinders remain external envelopes.

The initial 1.2 m-height aligned box also leaves an upper grip body overhanging the plate by 8.3 mm. The 1.3 m-height candidate provides 41.7 mm minimum body-to-plate-edge clearance. This is a geometric seat screen, not local plate resistance or a qualified bearing seat.

The aligned return axis is z=1.2667 m. Its final initial-force vertical couple is zero in the stated symmetric model; temporary stressing stages still matter. The lower-first sequence reaches 1.363 MNm, while the proposed balanced-pair ordering reaches 0.133 MNm. Both individual-strand half-steps are retained, so simultaneous stressing is not assumed. Release needs its own accepted sequence.

Gross in-plane bending demand is 82.2 MPa. The nominal combined bending/average shear/closed-box torsion demand over the balanced stages is 127.6 MPa. Nominal grip annular bearing is 97.3 MPa. These omit local plate bending, openings/seat effects, weld resistance, buckling, distortional behaviour and fatigue; no stress allowable is adopted.

[Strongback end CAD](strongback-end/model.FCStd) · [48-step proposed stressing sequence](stressing-sequence.csv)

## Ground-restraint load path

The raised return-rail support uses a nominal 250 × 250 × 12.5 mm post concept of 1.0167 m height. Its ideal fixed-base lateral stiffness is 67.1 MN/m. Steel-post, base rotation, connection and ground translation compliance act in series. Actual effective restraint remains unknown.

If every other interface were rigid, the ground-translation stiffness alone would need at least 1.015 MN/m to retain the proposed 1 MN/m spring. Alternatively, with all other interfaces rigid, the base rotational stiffness alone needs 1.049 MNm/rad. These individual limiting budgets cannot be combined as if they jointly met the requirement. Both-plane restraint, column/base/anchor resistance and geotechnical design remain open.

## Retained mechanical locator

The cartridge preserves the z=0.840 m datum with a 32 mm contact head and a 19.990 mm nominal stem in a 20.000 mm bore. Declared ±2 micrometre size hypotheses give a 6–14 micrometre diametral clearance range; heat treatment, temperature, finish and actual machining capability are not qualified.

A proposed M8 × 20 retaining screw passes through the RHS top-wall clearance hole; a 22 mm underside access opening permits assembly. A stepped pin solid contains a blind tap-drill, while the screw is a nominal thread envelope. Helical threads and their intended engagement interference are not modelled. Mount retention is not a rated lifting connection.

The button's nominal mass is 0.171 kg, top contact demand is 5.78 MPa and nominal screw engagement is 13.0 mm. Thread stripping, screw grade/preload/locking, local tube-wall/access-hole effects, pin heat treatment and repeatability remain open.

[Locator cartridge CAD](locator-cartridge/model.FCStd) · [concept fabrication BOM](fabrication-bom.csv)

## British manufacture and subcontract machining cases

These are published capabilities and unsent enquiries, not supplier offers. Pro-Mil's listed Starcut 260 travel is 6 × 4.35 × 2.15 m; its 50 t shop crane does not establish machine payload. Responsive lists a 10 × 3 × 1.5 m horizontal CNC capability. Boneham publishes UK custom cylindrical-component manufacture. Asquith Butler's current site focuses on service, spares and retrofit, so no new-build machine offer is inferred.

| Part with OSR setup allowance | Pro-Mil Starcut travel screen | Responsive advertised-range screen |
| --- | --- | --- |
| runway-baseplate, [1.2, 1.2, 0.25] m | within | within |
| strongback-box, [4.3, 1.2, 1.5] m | within | within |
| strongback-end-steel, [4.9, 4.3, 2.117] m | within | outside |
| runway-girder, [6.3, 0.75, 1.4] m | outside | within |

The 6 m girder plus 300 mm setup length exceeds the 6 m Starcut X travel. Axis orientation, usable simultaneous envelope, workholding, table payload, tool/head clearance and fabrication inspection need actual supplier returns for every case. UK work, raw-stock origin and installed Iraqi costs remain separate unknowns.

[Unsent fabrication RFQs](fabrication-rfq.csv) · [Full staged calculations](connections.json)

- Boneham & Turner: [official source 1](https://www.boneham.co.uk/precision-special-parts); [official source 2](https://www.boneham.co.uk/uk-manufacturing)
- Pro-Mil Engineering: [official source 1](https://www.pro-mil.co.uk/services/precision-cnc-milling--large-cnc-machining-capacities/7.htm)
- Responsive Engineering: [official source 1](https://responsive-engineering.com/services/machining/); [official source 2](https://responsive-engineering.com/services/fabrication/)
- Asquith Butler: [official source 1](https://www.asquithbutler.com/)
