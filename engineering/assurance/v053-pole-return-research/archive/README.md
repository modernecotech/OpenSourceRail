# Pole-face and 25 mm return-path research — 24 October 2026

No canonical source, configuration or generated packet was changed. This is a separate, unqualified research appendix; no candidate is adopted or accepted.

The original candidate `a79a21a0767355fcb6518471769e532a04e2e23f4bd33db90968ef4a385df5bd` is still disqualified. At an 8 mm gap and +120 A, its 435.97 kg module gives 3064 N, below its 4275 N own weight and 15371 N full AW3 allocation. Its unchanged 25 mm return has an optimistic 3476 N ceiling at 2.2 T. This bound and failure remain invariant under all three alternative pole-flux allocations tested on the exact original geometry and mass.

Executed evidence contains 78 initial pole/stack/winding cases, 118 refinement/topology cases, 9 exact baseline/asymmetric controls and 20 larger guidance-winding cases. Controls overlap designs; these are 225 executed case records, not 225 unique completed designs. Every rejection and one preliminary driver `TypeError` are retained. All acceptance, release and adoption flags are false.

## Original flux allocation

Only four of the first 78 cases pass the conditional symmetric static screen. A 25 mm face with a 2× stack weighs 772.26 kg per module and raises AW3 to 45.69 t/car. It needs 47.37 A at 40 °C; the conditional copper equilibrium is 57.68 °C under the original unqualified 24 W/K heat path. At 1.3 AW3 it requires 330.51 A and 2.711 T: both the 120 A and 2.2 T screens fail. Refined widths and stacks up to 2.4× retain positive geometric stock; none passes the 1.3 AW3 screen under the original allocation. More turns can reduce current but cannot remove the recorded excessive field.

## Topology sensitivity — not a corrected 3D model

The real declared leakage clearance is from the fork edge toward the inner guidance pole; it bypasses the separate lift pole. The original network nevertheless assigns total branch flux `psi=q+leakage` to its lift-pole path. The sensitivity moves the complete lift-pole path and 0%, 50% or 100% of the guidance-pole path length into useful-only `q` reluctance. All stock and mass stay counted. Positive B-H energy terms, their gradients and Hessians, and the original coil incidence and linkage remain consistent. Exact guidance-pole merging, leakage-only lengths, cross-field/fringing and 3D behaviour remain unresolved.

This sensitivity changes narrow-pole conclusions. A 22.5 mm face, 2.2× stack and 23.5 mm² lift-copper example weighs 846.14 kg and raises AW3 to 47.46 t/car; it requires 9.97 A for symmetric AW3 and 85.94 A at 2.105 T for 1.3 AW3 at 40 °C. The same geometry under the original allocation fails the 1.3 AW3 screen. The numerical sensitivity is not a physical correction or accepted solution. Multiple initial flux states converge, and finite-difference linkage/coenergy checks agree with the same network. They are not independent spatial or physical validation.

## Guidance and physical winding envelopes

The same representative sensitivity fails the simultaneous 1.0 AW3 lift plus 0.1 AW3 lateral research case: guidance needs about 102.8 A and exceeds 2.2 T. Different turns alone cannot remove the winding ampere-turn/current-density requirement.

Twenty new guidance-winding cases count actual copper, square-wire enamel, flooded pack fluid, 1 mm bobbins and, where needed, cover/coldplate extensions plus relocated connectors. The existing global fluid allocation is retained without credit. All 20 have nominal box clearance; 16 meet the unchanged 55% copper-fill limit and 4 overfill controls are retained. Additional mass feeds all 24 modules into AW3 before solving simultaneous forces. No demands or current, temperature or field limits were reduced.

Zero cases pass the combined 1.0 AW3 lift plus 0.1 AW3 lateral current-density/thermal screen. The best fitting/fill case by peak circuit current density weighs 961.93 kg/module and gives 50.24 t/car AW3. Its 200-turn, 13.4 mm² guidance winding requires 62.79 A: 4.686 A/mm² exceeds 3.75 A/mm². With the retained 18 W/K guidance cooling there is no equilibrium within 40–120 °C. Algebraic temperatures above 120 °C and enormous out-of-domain currents are failure indicators, not physical operating predictions or ratings. Individual-turn routing and bend radius, tolerances, pressure/cooling manifolds, RL/bus voltage, protection, native clearance, manufacturing and physical qualification remain open.

Reducing face width is worth studying, but this bounded work establishes neither a lighter self-consistent complete system nor a feasible train. Stationary return steel remains 436.505 kg/m, with no civil support, strength or cost acceptance. The larger moving mass, unqualified topology and guidance failures prevent adoption.

## Verify and replay

`python verify.py` checks every archived byte, compressed raw receipt and original source binding without the current repository. It requires the expected archive schema, ordinary files and directories without symlinks in their paths, safe relative member names, and bounded file counts and byte sizes. Only the root `manifest.json` is excluded from its own inventory; any nested file with that name must be inventoried and hashed.

`python verify.py --replay` reconstructs the original tree in a temporary directory and runs all four successful drivers using only archived inputs. NumPy and SciPy are required; recorded versions are in the raw results. Each driver is bounded to 300 seconds by the verifier. Replay compares all raw results exactly apart from elapsed wall time. No network or canonical paths are used.

`summary.json` and `research-comparison.png` present the raw executed cases. All sources, successful and failed drivers, logs and complete results are retained under `inputs/` and `evidence/`; `manifest.json` gives checksums. Hash consistency and replay provide research reproducibility, not authenticated engineering acceptance.
