# Drilled longitudinal stock alternatives

Provisional rigid-car full-AW3 sensitivity. The existing GFRP sandwich remains the leading structural-body study. These two-spine alternatives are not adopted.

| Case | Added kg/car | Full kg/car | Series MN/m | Phase degrees | 5 degree screen |
|---|---:|---:|---:|---:|---|
| gfrp-control | 0.000 | 26200.000 | 15.884339 | 11.447463 | hold |
| steel-wall-003 | 65.317 | 26265.317 | 33.222812 | 5.365565 | hold |
| steel-wall-004 | 247.053 | 26447.053 | 39.744180 | 4.429299 | pass |
| steel-wall-005 | 426.653 | 26626.653 | 45.048339 | 3.978316 | pass |
| steel-wall-006 | 604.118 | 26804.118 | 49.446151 | 3.689825 | pass |

[Exact source/stock derivation and metrics](study.json.gz) · [Compiler/run receipt](execution.json.gz) · [Overview](overview.svg) · [Checksums](manifest.json)

Each case retains its complete raw trace in the correspondingly named JSON.gz file. Two 17m tubes with a140×220mm envelope,384 bolt axes/768 wall cuts and384 length-corrected crush spacers are accounted for. Only directly replaced counted tube/spacer material is credited; all resulting mass increases are added to the full26200kg/car baseline.

Structurally participating GFRP sandwich remains the leading body study. Steel spines are an explicit alternative, not a hidden conventional complete underframe or adopted architecture.

Full joined-body skin/frame participation, torsion, bending, buckling, fatigue and coupler/hardpoint compliance remain unqualified; this is a rigid-car lumped axial sensitivity.

Thin steel wall bearing/pull-through, crushing, weld heat/distortion, tube splices, local buckling, corrosion, thermal expansion/magnetic interaction and dissimilar-material interfaces require independent design and tests.

E=200GPa, density=7850kg/m3, GFRP properties and coupler100MN/m are assumptions. Actual supply, local fabrication, steel grade, dimensional tolerances, weld procedure and inspectability remain unverified.

Full AW3 reference mass plus every added directly replaced tube/spacer kg is retained; equipment, payload and contingency reserves receive no removal credit. Baseline assumed roll/pitch inertias and ideal independently allocated thrust are unchanged.

The existing hardpoint load hypothesis is26400kg/car. Alternatives above it need heavier-load re-evaluation as well as the new steel-wall joint design; a phase-screen pass does not close this gate.

The 5 degree magnetic phase screen, physical gap/stroke/force controllers and numerical controls are unchanged. Passing them is not shared-field electromagnetic feasibility, a flexible-body confirmation, manufacturing or physical acceptance.

No city default, equipped-body mass, plant stiffness, manufacturing release or physical output is authorised.
