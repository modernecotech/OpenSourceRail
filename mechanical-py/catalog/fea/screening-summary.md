# Rolling-Stock FEA Screening Summary

This is a first-pass FreeCAD/CalculiX beam-model screen for gross
load paths. It is not a homologation, fatigue, crashworthiness, weld,
shell-buckling, or supplier-final mesh.

## FEA Stack

- FreeCAD importable: True
- FreeCAD version: ['1', '1', '3', '44987 (Git)', 'https://github.com/FreeCAD/FreeCAD.git', '2026/07/25 04:52:02', '(HEAD detached at 1.1.3)', '145529fe741292ff0b3977a01195bf0247425794']
- Modules: {'Fem': True, 'femtools': True, 'femmesh': True, 'Assembly': True}
- Executables: {'ccx': {'path': '/app/bin/ccx', 'version': ['This is Version 2.23']}, 'gmsh': {'path': '/app/bin/gmsh', 'version': ['4.15.0-git']}}

## Results

| Study | Load case | Nodes | Elements | Applied load kN | Vertical load kN | Max displacement mm | Target mm | Max von Mises MPa | SF to S355 yield | Result PNG | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| Low-floor chassis supported at bogie connectors | 360 kN vertical service load distributed over low-floor and high-floor bearer grid | 155 | 159 | 360.0 | 360.0 | 9.843 | 25.0 | 18.2 | 19.52 | [PNG](chassis-bogie-screen/chassis-bogie-screen-result.png) | OK |
| Low-floor chassis AW3 vertical proof-load screen | 540 kN vertical proof load: 1.5 x the baseline 360 kN service gravity case | 155 | 159 | 540.0 | 540.0 | 14.765 | 35.0 | 27.3 | 13.01 | [PNG](chassis-aw3-proof-screen/chassis-aw3-proof-screen-result.png) | OK |
| Low-floor chassis asymmetric track-twist screen | Asymmetric 65/110/125% side load bias plus 25 kN diagonal equipment offset | 155 | 159 | 385.0 | 385.0 | 11.415 | 30.0 | 21.0 | 16.94 | [PNG](chassis-track-twist-screen/chassis-track-twist-screen-result.png) | OK |
| Motor/trailer bogie H-frame screening model | 160 kN bogie vertical load applied through two secondary-air-spring seats | 29 | 24 | 160.0 | 160.0 | 0.771 | 5.0 | 10.6 | 33.51 | [PNG](bogie-frame-screen/bogie-frame-screen-result.png) | OK |
| Bogie frame brake/traction longitudinal load screen | 160 kN vertical bogie load plus 60 kN longitudinal brake/traction reaction | 29 | 24 | 220.0 | 160.0 | 2.723 | 6.0 | 18.6 | 19.05 | [PNG](bogie-brake-traction-screen/bogie-brake-traction-screen-result.png) | OK |
| Full car body side/roof frame screening model | 420 kN body/payload plus 60 kN installed systems and 30 kN roof equipment allowance | 72 | 168 | 510.0 | 510.0 | 0.240 | 15.0 | 5.8 | 61.29 | [PNG](full-body-frame-screen/full-body-frame-screen-result.png) | OK |
| Full car body lateral sway screen | 165 kN lateral body/interior/installed-systems equivalent load through side posts, waist rails, and cant rails | 72 | 168 | 165.0 | 0.0 | 18.055 | 20.0 | 40.2 | 8.83 | [PNG](full-body-lateral-sway-screen/full-body-lateral-sway-screen-result.png) | OK |
| Three-train full-set longitudinal buff/draft screen | 180 kN longitudinal buff/draft load through the 148.5 m full-set spine and two open train-to-train joints | 127 | 155 | 180.0 | 0.0 | 0.536 | 35.0 | 0.8 | 468.60 | [PNG](full-set-longitudinal-buff-screen/full-set-longitudinal-buff-screen-result.png) | OK |
| Three-train full-set vertical service screen | 1,080 kN distributed nine-car service gravity plus 70 kN across two open train-to-train joints | 162 | 155 | 1150.0 | 1150.0 | 0.811 | 45.0 | 1.3 | 277.98 | [PNG](full-set-vertical-service-screen/full-set-vertical-service-screen-result.png) | OK |
| Train-to-train open joint vertical load screen | 90 kN vertical load through open portal, threshold bridge, lower drawbar, and upper links | 48 | 51 | 90.0 | 90.0 | 4.420 | 12.0 | 40.8 | 8.70 | [PNG](train-to-train-joint-vertical-screen/train-to-train-joint-vertical-screen-result.png) | OK |
| Train-to-train open joint lateral/racking screen | 55 kN lateral load through open portal clamp frames, upper links, and threshold bridge | 48 | 51 | 55.0 | 0.0 | 2.306 | 16.0 | 21.5 | 16.48 | [PNG](train-to-train-joint-lateral-sway-screen/train-to-train-joint-lateral-sway-screen-result.png) | OK |

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

### Three-train full-set longitudinal buff/draft screen

- Models three LM3 modules as one 148.5 m spine with two train-to-train open joints.
- The load is a gross service/recovery screen, not an EN 15227 crash case.

### Three-train full-set vertical service screen

- Supports represent all 18 bogies in the full-set example.
- The two open train-to-train joints receive explicit vertical allowances for gangway, threshold, and passenger transfer loads.

### Train-to-train open joint vertical load screen

- Screens the local common end-interface carrier rings and open gangway cassette.
- The fixed-side ring is supported along its full moulded end-frame interface, matching the chassis/body pick-up concept.
- Passenger threshold bridge and gangway loads are included as vertical distributed loads.

### Train-to-train open joint lateral/racking screen

- Complements the full-set vertical and longitudinal screens with a local racking case.
- The fixed-side ring is supported laterally along its full moulded end-frame interface.
- Supplier bellows fabric, rubber fatigue, clamps, and fastener details still require supplier proof evidence.

## Geometry/Model Caveats

- Beam sections are conservative rectangular approximations of the CAD envelopes.
- Composite body panels, glazing, adhesive lands, local brackets, bolt holes, weld toes, and notches are not meshed.
- Loads are static screening loads only; no crash, fatigue spectrum, modal, thermal, or derailment cases are included.
- Any stress above the 0.6 x S355 yield service screen should trigger a detailed shell/solid mesh and local joint design.
