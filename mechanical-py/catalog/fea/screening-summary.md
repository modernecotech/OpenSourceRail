# Rolling-Stock FEA Screening Summary

This is a first-pass FreeCAD/CalculiX beam-model screen for gross
load paths. It is not a homologation, fatigue, crashworthiness, weld,
shell-buckling, or supplier-final mesh.

## FEA Stack

- FreeCAD importable: True
- FreeCAD version: ['1', '1', '1', '44874 (Git)', 'https://github.com/FreeCAD/FreeCAD.git', '2026/04/14 22:09:59', '(HEAD detached at 1.1.1)', '0108fd4b4850cc46e625b60e53cea7a7bbe69f8d']
- Modules: {'Fem': True, 'femtools': True, 'femmesh': True, 'Assembly': True}
- Executables: {'ccx': {'path': '/app/bin/ccx', 'version': ['This is Version 2.23']}, 'gmsh': {'path': '/app/bin/gmsh', 'version': ['4.15.0-git']}}

## Results

| Study | Load case | Nodes | Elements | Applied load kN | Vertical load kN | Max displacement mm | Target mm | Max von Mises MPa | SF to S355 yield | Result PNG | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| Low-floor chassis supported at bogie connectors | 360 kN vertical service load distributed over low-floor and high-floor bearer grid | 155 | 159 | 360.0 | 360.0 | 11.335 | 25.0 | 19.8 | 17.95 | [PNG](chassis-bogie-screen/chassis-bogie-screen-result.png) | OK |
| Low-floor chassis AW3 vertical proof-load screen | 540 kN vertical proof load: 1.5 x the baseline 360 kN service gravity case | 155 | 159 | 540.0 | 540.0 | 17.002 | 35.0 | 29.7 | 11.97 | [PNG](chassis-aw3-proof-screen/chassis-aw3-proof-screen-result.png) | OK |
| Low-floor chassis asymmetric track-twist screen | Asymmetric 65/110/125% side load bias plus 25 kN diagonal equipment offset | 155 | 159 | 385.0 | 385.0 | 13.124 | 30.0 | 22.7 | 15.64 | [PNG](chassis-track-twist-screen/chassis-track-twist-screen-result.png) | OK |
| Motor/trailer bogie H-frame screening model | 160 kN bogie vertical load applied through two secondary-air-spring seats | 29 | 24 | 160.0 | 160.0 | 0.771 | 5.0 | 10.6 | 33.51 | [PNG](bogie-frame-screen/bogie-frame-screen-result.png) | OK |
| Bogie frame brake/traction longitudinal load screen | 160 kN vertical bogie load plus 60 kN longitudinal brake/traction reaction | 29 | 24 | 220.0 | 160.0 | 2.723 | 6.0 | 18.6 | 19.05 | [PNG](bogie-brake-traction-screen/bogie-brake-traction-screen-result.png) | OK |
| Full car body side/roof frame screening model | 420 kN distributed body/payload gravity plus 30 kN roof equipment allowance | 72 | 136 | 450.0 | 450.0 | 0.372 | 15.0 | 6.7 | 52.83 | [PNG](full-body-frame-screen/full-body-frame-screen-result.png) | OK |
| Full car body lateral sway screen | 145 kN lateral body/interior equivalent load through side posts, waist rails, and cant rails | 72 | 136 | 145.0 | 0.0 | 21.834 | 20.0 | 38.3 | 9.26 | [PNG](full-body-lateral-sway-screen/full-body-lateral-sway-screen-result.png) | Review: screening deflection exceeds 20.0 mm target |

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
- Composite panels and glazing are treated as non-structural for this screening pass.

### Full car body lateral sway screen

- Applies an approximate 0.15 g lateral inertial load through the occupied side-frame height.
- This complements the vertical body frame case; it is not a modal, ride, or fatigue analysis.

## Geometry/Model Caveats

- Beam sections are conservative rectangular approximations of the CAD envelopes.
- Composite body panels, glazing, adhesive lands, local brackets, bolt holes, weld toes, and notches are not meshed.
- Loads are static screening loads only; no crash, fatigue spectrum, modal, thermal, or derailment cases are included.
- Any stress above the 0.6 x S355 yield service screen should trigger a detailed shell/solid mesh and local joint design.
