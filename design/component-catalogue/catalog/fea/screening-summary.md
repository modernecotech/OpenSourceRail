# Rolling-Stock FEA Screening Summary

This is a first-pass FreeCAD/CalculiX beam-model screen for gross
load paths. It is not a homologation, fatigue, crashworthiness, weld,
shell-buckling, or supplier-final mesh.

## FEA Stack

- FreeCAD importable: True
- FreeCAD version: ['1', '1', '4', '45039 (Git)', 'https://github.com/FreeCAD/FreeCAD.git', '2026/09/28 13:46:34', '(HEAD detached at 1.1.4)', '4fd3bf320d9566a27e60069fc8387448aaa3a094']
- Modules: {'Fem': True, 'femtools': True, 'femmesh': True, 'Assembly': True}
- Executables: {'ccx': {'path': '/app/bin/ccx', 'version': ['This is Version 2.23']}, 'gmsh': {'path': '/app/bin/gmsh', 'version': ['4.15.0-git']}}

## Results

| Study | Load case | Nodes | Elements | Applied load kN | Vertical load kN | Max displacement mm | Target mm | Max von Mises MPa | SF to S355 yield | Result PNG | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| Low-floor chassis supported at bogie connectors | 360 kN vertical service load distributed over low-floor and high-floor bearer grid | 155 | 159 | 360.0 | 360.0 | 20.885 | 25.0 | 101.1 | 3.51 | [PNG](chassis-bogie-screen/chassis-bogie-screen-result.png) | OK |
| Low-floor chassis AW3 vertical proof-load screen | 540 kN vertical proof load: 1.5 x the baseline 360 kN service gravity case | 155 | 159 | 540.0 | 540.0 | 31.327 | 35.0 | 151.6 | 2.34 | [PNG](chassis-aw3-proof-screen/chassis-aw3-proof-screen-result.png) | OK |
| Low-floor chassis asymmetric track-twist screen | Asymmetric 65/110/125% side load bias plus 25 kN diagonal equipment offset | 155 | 159 | 385.0 | 385.0 | 24.205 | 30.0 | 121.2 | 2.93 | [PNG](chassis-track-twist-screen/chassis-track-twist-screen-result.png) | OK |
| Motor/trailer bogie H-frame screening model | 160 kN bogie vertical load applied through two secondary-air-spring seats | 29 | 24 | 160.0 | 160.0 | 2.110 | 5.0 | 57.6 | 6.16 | [PNG](bogie-frame-screen/bogie-frame-screen-result.png) | OK |
| Bogie frame brake/traction longitudinal load screen | 160 kN vertical bogie load plus 60 kN longitudinal brake/traction reaction | 29 | 24 | 220.0 | 160.0 | 22.210 | 6.0 | 160.3 | 2.21 | [PNG](bogie-brake-traction-screen/bogie-brake-traction-screen-result.png) | Review: screening deflection exceeds 6.0 mm target |
| Full car body side/roof frame screening model | 420 kN body/payload plus 60 kN installed systems and 30 kN roof equipment allowance | 72 | 168 | 510.0 | 510.0 | 3.035 | 15.0 | 41.2 | 8.61 | [PNG](full-body-frame-screen/full-body-frame-screen-result.png) | OK |
| Full car body lateral sway screen | 165 kN lateral body/interior/installed-systems equivalent load through side posts, waist rails, and cant rails | 72 | 168 | 165.0 | 0.0 | 726.825 | 20.0 | 587.6 | 0.60 | [PNG](full-body-lateral-sway-screen/full-body-lateral-sway-screen-result.png) | Review: screening deflection exceeds 20.0 mm target |
| Train-to-train open joint vertical load screen | 90 kN vertical load through open portal, threshold bridge, lower drawbar, and upper links | 48 | 51 | 90.0 | 90.0 | 18.332 | 12.0 | 255.1 | 1.39 | [PNG](train-to-train-joint-vertical-screen/train-to-train-joint-vertical-screen-result.png) | Review: screening deflection exceeds 12.0 mm target |
| Train-to-train open joint lateral/racking screen | 55 kN lateral load through open portal clamp frames, upper links, and threshold bridge | 48 | 51 | 55.0 | 0.0 | 9.542 | 16.0 | 120.3 | 2.95 | [PNG](train-to-train-joint-lateral-sway-screen/train-to-train-joint-lateral-sway-screen-result.png) | OK |

## Study Notes

### Low-floor chassis supported at bogie connectors

- Bogie support points represent four secondary-air-spring/chassis interface pads.
- Reworked chassis uses deep side torsion boxes, twin keel beams, upper battery-zone chords, and stiffer cross-bearers.

### Low-floor chassis AW3 vertical proof-load screen

- Uses the same bogie support pads as the service screen with a 1.5 x vertical load multiplier.
- This is a static proof-load screen only; fatigue and local weld toe stresses remain v2 work.

### Low-floor chassis asymmetric track-twist screen

- Represents uneven passenger/load distribution during a track-twist or low-speed ramp transition.
- The diagonal equipment allowance biases the roof-side service mass onto one chassis side.

### Motor/trailer bogie H-frame screening model

- Axlebox/primary-suspension support nodes constrain vertical displacement.
- Motor reaction brackets are not included in this load case; use the motor connector CAD for interface review.

### Bogie frame brake/traction longitudinal load screen

- Adds a longitudinal force path through the secondary-seat structure on top of the vertical bogie case.
- Gearbox, axle, and detailed motor-bracket local stresses are still outside this beam-model screen.

### Full car body side/roof frame screening model

- Side posts, side sills, waist rails, cant rails, and roof bows are idealised as S355 beams.
- Revised body includes diagonal side-frame racking members added after the initial lateral-sway exceedance.
- Composite panels and glazing are treated as non-structural for this screening pass.

### Full car body lateral sway screen

- Applies an approximate 0.15 g lateral inertial load through the occupied side-frame height.
- The current candidate includes diagonal side-frame racking members and enlarged side/roof bearers.
- This complements the vertical body frame case; it is not a modal, ride, or fatigue analysis.

### Train-to-train open joint vertical load screen

- Screens the local common end-interface carrier rings and open gangway cassette.
- The fixed-side ring is supported along its full moulded end-frame interface, matching the chassis/body pick-up concept.
- Passenger threshold bridge and gangway loads are included as vertical distributed loads.

### Train-to-train open joint lateral/racking screen

- Complements the open-end vertical screen with a local racking case.
- The fixed-side ring is supported laterally along its full moulded end-frame interface.
- Supplier bellows fabric, rubber fatigue, clamps, and fastener details still require supplier proof evidence.

## Geometry/Model Caveats

- Native study walls and B32R BOX sections share explicit dimensions and proposed 8 mm walls. These research sections are not supplier/CAD-catalogue acceptance; old solid-envelope results are historical diagnostics.
- Composite body panels, glazing, adhesive lands, local brackets, bolt holes, weld toes, and notches are not meshed.
- Loads are static screening loads only; no crash, fatigue spectrum, modal, thermal, or derailment cases are included.
- Any stress above the 0.6 x S355 yield service screen should trigger a detailed shell/solid mesh and local joint design.
