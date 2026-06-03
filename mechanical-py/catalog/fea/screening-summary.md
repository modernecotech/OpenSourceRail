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

| Study | Load case | Nodes | Elements | Vertical load kN | Max displacement mm | Target mm | Max von Mises MPa | SF to S355 yield | Status |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Low-floor chassis supported at bogie connectors | 360 kN vertical service load distributed over low-floor and high-floor bearer grid | 155 | 159 | 360.0 | 11.335 | 25.0 | 19.8 | 17.95 | OK |
| Motor/trailer bogie H-frame screening model | 160 kN bogie vertical load applied through two secondary-air-spring seats | 29 | 24 | 160.0 | 0.771 | 5.0 | 10.6 | 33.51 | OK |
| Full car body side/roof frame screening model | 420 kN distributed body/payload gravity plus 30 kN roof equipment allowance | 72 | 136 | 450.0 | 0.372 | 15.0 | 6.7 | 52.83 | OK |

## Study Notes

### Low-floor chassis supported at bogie connectors

- Bogie support points represent four secondary-air-spring/chassis interface pads.
- Reworked chassis uses deep side torsion boxes, twin keel beams, upper battery-zone chords, and stiffer cross-bearers.

### Motor/trailer bogie H-frame screening model

- Axlebox/primary-suspension support nodes constrain vertical displacement.
- Motor reaction brackets are not included in this load case; use the motor connector CAD for interface review.

### Full car body side/roof frame screening model

- Side posts, side sills, waist rails, cant rails, and roof bows are idealised as S355 beams.
- Composite panels and glazing are treated as non-structural for this screening pass.

## Geometry/Model Caveats

- Beam sections are conservative rectangular approximations of the CAD envelopes.
- Composite body panels, glazing, adhesive lands, local brackets, bolt holes, weld toes, and notches are not meshed.
- Loads are static gravity/service loads only; no crash, fatigue spectrum, modal, thermal, or derailment cases are included.
- Any stress above the 0.6 x S355 yield service screen should trigger a detailed shell/solid mesh and local joint design.
