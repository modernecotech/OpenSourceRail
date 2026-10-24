# Magnetic redesign bounds — research appendix

The main candidate remains `a79a21a0767355fcb6518471769e532a04e2e23f4bd33db90968ef4a385df5bd`, with its recorded failures. This appendix preserves twelve isolated hypotheses. It changes no production design, default, source, configuration or canonical packet. Every changed hypothesis has a separate research identity in [results.json](results.json).

At an 8 mm gap and +120 A, the current 435.97 kg module produces **3,064 N**, below its **4,275 N** own weight and **15,371 N** full AW3 allocation. Its present 25 mm return section has an optimistic **3,476 N** lift ceiling at 2.2 T. More PM or current cannot overcome that cross-section bound while retaining the field limit.

For symmetric lift, useful branch flux is `q = sqrt(F × μ0 × pole_area)`. The necessary return wall is `t ≥ q / (stack_fill × extrusion_length × B_limit)`. The existing pole area is 0.016 m², extrusion length 0.16 m and stack fill 0.95. Supporting the full current AW3 allocation requires at least **52.57 mm at 2.2 T**, or **64.25 mm at 1.8 T**. These area bounds are insufficient by themselves: the actual nonlinear steel proxy still needs 331 A with a 55 mm wall.

Two hypotheses pass only the conditional symmetric static-lift screen:

| Hypothesis | Module mass | Full AW3/car | Return + wear stock per 25 m track | Conditional hot current / copper temperature | Current required at 1.3 AW3, 40°C |
|---|---:|---:|---:|---:|---:|
| 80 mm returns, existing module | 435.97 kg | 37.619 t | 36.09 t | 66.92 A / 64.32°C | 132.13 A — exceeds 120 A |
| 1.5× core stack, 55 mm returns | 611.19 kg | 41.824 t | 24.09 t | 67.51 A / 69.57°C | 250.06 A — exceeds 120 A |

The original return + wear stock is 10.91 t per 25 m. Added guideway stock has not received concrete, bracket, joint, pier, foundation, erection or cost acceptance. Actual changed module and copper mass feeds back into AW3; retained equipment, propulsion band and protection mass stay counted. There is no removal credit for hypothetical simplification.

The static screen retains 120 A, 2.2 T, coil fill and 3.75 A/mm² limits. It assumes the existing unqualified 24 W/K lift cooling path. The direct symmetric stationarity reduction is cross-checked by the original four-flux Newton evaluator; both describe the same reluctance network. This is **not independent spatial or physical validation**. Extreme saturated points explain failure; they are not proposed operating ratings.

Guidance/asymmetry authority, dynamic and fault reserve, actual RL control, PM tolerance/demagnetization, independent 3D force/linkage/loss maps, native clearance and joints, insulation/connectors, measured cooling, civil strength/dead load, propulsion, manufacturing and supplier qualification remain open. **Neither heavier hypothesis passes the 1.3 AW3 current screen. No complete system is feasible or adopted from this appendix; every release/acceptance flag is false.**

[Exact executed driver](run.py) · [Executed source receipt](source-manifest.json) · [Execution log](execution.log) · [Original generated report](executed-README.md) · [Archive receipt](archive-receipt.json) · [Reproduction instructions](reproduction.txt)

`verify.py` validates all archived source/output bytes without relying on current repository sources. Its optional replay reconstructs the original paths in a temporary tree using the archived inputs and compares all results, ignoring only elapsed wall time.
