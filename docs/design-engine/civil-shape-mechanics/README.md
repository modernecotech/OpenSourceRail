# Civil shape mechanics

18 nominal span candidates have 189 conditional stepped-beam evaluations under the same selected six-car train: empty, normal and crowd-control loads, each with low/base/high accounted span mass. The hybrid also has separate steel-only and perfect-bond hypotheses. No civil design is selected or qualified.

| Family / profile | Primary elastic hypothesis | Crowd/high-mass model deflection bound (mm) | Base assumed hook capacity exceeded | Lift-adjusted scoped installed cost (IQD million, base) |
|---|---|---:|---|---:|
| reference_box / lean | full-section-uncracked | 36.26 | False | 93.18 |
| reference_box / reference | full-section-uncracked | 22.80 | True | 97.92 |
| reference_box / robust | full-section-uncracked | 15.56 | True | 103.90 |
| ribbed_u / lean | full-section-uncracked | 90.23 | False | 89.90 |
| ribbed_u / reference | full-section-uncracked | 51.25 | False | 93.20 |
| ribbed_u / robust | full-section-uncracked | 32.34 | True | 98.61 |
| variable_depth_box / lean | full-section-uncracked | 44.69 | False | 94.20 |
| variable_depth_box / reference | full-section-uncracked | 27.85 | True | 97.10 |
| variable_depth_box / robust | full-section-uncracked | 18.85 | True | 102.01 |
| folded_plate / lean | full-section-uncracked | 81.21 | False | 90.68 |
| folded_plate / reference | full-section-uncracked | 48.94 | False | 92.76 |
| folded_plate / robust | full-section-uncracked | 32.15 | False | 95.01 |
| hybrid_steel_concrete / lean | steel-only-longitudinal | 153.60 | False | 195.40 |
| hybrid_steel_concrete / reference | steel-only-longitudinal | 92.09 | False | 232.51 |
| hybrid_steel_concrete / robust | steel-only-longitudinal | 59.88 | False | 273.33 |
| load_following_ribs / lean | full-section-uncracked | 126.45 | False | 90.31 |
| load_following_ribs / reference | full-section-uncracked | 70.57 | False | 92.59 |
| load_following_ribs / robust | full-section-uncracked | 43.69 | False | 95.07 |

Every value above depends on unvalidated material/load-transfer hypotheses and accounted masses. There is no universal displacement pass limit. Concrete tensile resistance, reinforcement, prestress force, rail stiffness and steel–concrete bond receive no undeclared credit. Steel-only analysis retains the full concrete dead weight. Other installed mass, shear deformation, torsion, cracking, creep, local steps, buckling, fatigue, unequal rail loading, supports and construction stages remain unresolved.

## Mechanical calculation

Each actual polygon-prism cell has its own modulus-weighted neutral axis and flexural rigidity. Concrete at 35 GPa and steel at 200 GPa are explicit research hypotheses, not tested article properties or design allowables. Equilibrium gives reactions and piecewise moments/shears. Unit-load virtual work integrates actual-pose deflection across every cell, axle and observation boundary using exact-order Gaussian quadrature, subject to floating-point roundoff. The representative train position maximises midspan live moment only; it is not asserted to maximise deflection or stress.

Six full axles can occupy the declared 20 m span. Let Q be their maximum total factored force. For every train position, live moment is at most Q·x·(L−x)/L. The unit-moment influence for any displacement observation is at most x·(L−x)/L. Integrating the product of this influence envelope and the total moment envelope over each cell's EI bounds every observation and train position **within the declared beam model**. This is not a physical deflection bound when cracking, shear, slip or unknown installed loads invalidate that model. The dynamic-factor hypothesis is applied once; each axle load already covers both rails.

The three span mass scenarios reuse the priced reinforcement/prestress/rail/fastener accounts once. Nominal geometry gravity follows its actual cells; additional accounts are spread uniformly as an explicit hypothesis. Foundation and service price reserves are not converted into beam mass. Concrete stress results are demands without credited resistance, not strength screens.

## Manufacturing and experiment ranking

Required hook mass includes nominal span stock, preliminary reinforcement/prestress and 25% rigging. A declared 60 t hook-capacity hypothesis is checked without assuming any crane radius or lifting-point qualification. When exceeded, erection cost is increased using the configured Class C scaling law; the result does not confirm that a suitable crane or lift exists. Manufacturing and civil labour retain the parent portfolio's two-shift basis.

The family-cell archive compares conditional stiffness, lifting-adjusted provisional cost and stock mass. It preserves the original quantity-only archive and every rejected alternative. Experiment ordering grants no stage-two admission; resistance, interfaces and manufacture remain explicit next tasks. Calculations run in the current Python process with a runtime guard between candidates; the memory request is recorded but is not an operating-system limit or isolation boundary.

## Reproduce

```bash
python3 -m engineering.design_search.civil_shape_mechanics build
python3 -m engineering.design_search.civil_shape_mechanics verify
```

Methods: [University of Illinois beam/composite bending](https://mechref.engr.illinois.edu/sol/bending.html) and [University of Alberta virtual work](https://engcourses-uofa.ca/variational-principles/the-principle-of-virtual-work/). These explain the analytical methods; they do not validate this railway or its assumed material properties.

[Exact inputs, hypotheses and results](result.json.gz) · [Mechanical assumptions](../../../campaigns/civil-shape-mechanics.toml) · [Source/payload receipt](manifest.json) · [Physical geometry and cost portfolio](../civil-shape-portfolio/README.md)
