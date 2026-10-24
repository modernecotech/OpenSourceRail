# Propulsion redesign screen — research appendix

This appendix preserves an isolated exploration. The canonical `a79a21a0767355fcb6518471769e532a04e2e23f4bd33db90968ef4a385df5bd` candidate remains rejected, with its recorded lift and propulsion failures. No production source, configuration, default or canonical packet was changed. Every altered geometry has a separate research identity; every adoption, completion and physical-release flag remains false.

The [original manifest](executed/manifest.json), all 67 executed scripts, inputs, results, reports and completed logs are retained byte for byte under `executed/`. Eight exact source inputs are retained under `inputs/`. The [archive receipt](archive-receipt.json) binds these files and the later archive documentation and verifier. Original execution paths and commands are preserved; the archive does not relabel an old run as a new design.

The screen retains **21 executed coupons and two refused requests**. The refused `256 × 64` meshes exceed the existing depth-cell guard; their valid replacements use `256 × 48`. Failed and unknown outcomes remain present.

## What the calculations found

| Geometry | Relevant result | Outcome |
|---|---|---|
| Original Halbach | Local opposing PM field rises from 426 to 464 kA/m with refinement; demagnetisation margins are already −82 to −121 kA/m before armature loading | Failed |
| Original rectangular shoes | Fundamental field changes only 0.18%, while the local opposing PM field rises from 301 to 350 kA/m; fine zero-armature margin is −5.83 kA/m | Failed; a converged fundamental does not establish local material survival |
| Original round shoes | Nonlinear secant mismatch remains 5.42–5.55, with implausible 43.8–72.3 T steel fields, despite small linear matrix residuals | Nonconverged; no operating-force credit |
| 0.5 m period, 40 mm depth, 1 mm chamfer | Cold margin after the declared maximum-current bound falls 57.5 → 26.5 → 4.47 → **−9.43 kA/m** on successive 64 → 128 → 192 → 256 meshes | Failed finer evidence supersedes earlier positive estimates |
| 0.5 m period, 40 mm depth, **8 mm physical chamfer** | Fine `256 × 48` margins are **+28.95 kA/m at 0°C** and **+70.83 kA/m at 40°C**, after the declared maximum-current bound | Positive sampled nonlinear coupons; unresolved design holds remain |

The final physical-corner hypothesis is `2ccec6df01771f2c57d582deb1f7a0dcf44d8ff2ff4f4b8ce56da01609bcfc6a`. The 8 mm chamfer spans 4.096 longitudinal cells and 9.6 depth cells on the finest mesh. Its cold fundamental field is 0.08382 T; the warm value is 0.07800 T. Local peaks still move with refinement: the cold margin changes from 42.10 to 28.95 kA/m. **Four cells across the corner are not a demonstrated grid-convergence result.**

The physical chamfers remove an exact scalar 0.0024576 m³ / 12.288 kg of PM stock across the two 12 m bands (2.56% of their unchamfered PM volume). Fine cell removal is 2.474%, versus 2.734% on the coarse mesh. Revised native CAD, installed mass/CG/inertia, retention and manufacturing are unissued. The 1,258.2144 kg source-box assembly mass is an upper bound, not an adopted net installed mass.

## Conditional force and acceleration

The unchanged source equations were evaluated for **one 12 m band, four independent 5 m groups and actual finite overlap**: only 1 m of overlap in each outer group and 5 m in each middle group. The conditional 40°C magnetic / 80°C copper map at 1,349 A peak and 20 m/s gives:

- 10.092 kN longitudinal force per car; symmetric side-normal terms of 239.95 N per side, with zero net lateral force at that pose.
- Maximum 41.90 V back EMF and 66.77 V steady rotating-current voltage, compared with a 1,385.64 V modulation limit.
- 178.66 kW total copper heating across the four groups and a 3.90 K/group adiabatic rise over ten seconds.

These are conditional undamaged-field model quantities, **not executed inverter/RL/control results or qualified operating capacity**. The exact 1,350 A phasor produces a floating-point magnitude of `1350.0000000000002 A` and is refused by the unchanged strict guard. The 1,349 A evaluation is a separately retained interior request; no current limit was relaxed.

Using the **current canonical 37,618.5915 kg AW3/car as a comparison mass**, the conditional force gives only **0.2683 m/s² before resistance and grade**. The new hypothesis has no reconciled installed mass; this arithmetic does not adopt the old mass for it. [Exact comparison data](acceleration-comparison.json) retain both current acceleration contexts:

| Context | Acceleration | Inertial force required per car | Conditional ideal force margin |
|---|---:|---:|---:|
| Current full-dynamics route request | 0.2 m/s² | 7.524 kN | +2.568 kN before resistance and grade |
| Existing station-study acceleration setting | 0.8 m/s² | 30.095 kN | −20.003 kN before resistance and grade |
| Illustrative comparison only | 1.0 m/s² | 37.619 kN | −27.527 kN before resistance and grade |

The station-study resistance proxy is 1.720 kN/car at 20 m/s; adding that older, unqualified proxy to the 0.2 m/s² comparison leaves only about 0.848 kN/car before grade. These are necessary force checks at one pose and speed, not a launch profile. Installed powered length, entry/exit overlap, phase and current timing, whole-train group sharing, speed-dependent force/voltage, thermal duty and cooling, resistance and route grades still need a consistent simulation. No launch performance, stopping distance, headway or route feasibility is established here.

## Verification and open gates

[verify.py](verify.py) uses the standard library to check bounded ordinary files, an exact inventory, all original file/source hashes, changed-input identities, retained failures, scalar chamfer volumes and acceleration arithmetic. `--check-current-sources` additionally checks the eight original source inputs against the current repository.

The optional `--replay` reconstructs original source paths in a temporary tree and executes the byte-identical original worker for the selected `256 × 48` cold and warm coupons. It compares complete coupon and identity records exactly, excluding elapsed wall time. The later scalar-volume annotations are checked separately. The retained [selected replay receipt](selected-replay-receipt.json) identifies the actual Python/NumPy/SciPy environment; the original exploratory run did not record external package versions. No current candidate code is imported for this replay.

The positive sampled corner coupons do **not** close local-peak mesh convergence, the full temperature range, independently validated 3D fields and end effects, measured material data, manufacturing/retention, native clearance, actual transient electrical control, thermal duty, whole-train sharing or system integration. They do not resolve the current return-rail saturation and unavailable static lift support. No price, cost saving, localisation percentage or complete design is inferred.

[Readable original findings](executed/findings.md) · [Latest original roll-up](executed/results.json) · [Original prior failures](executed/prior-failures.json) · [Conditional current-boundary data](executed/current-boundary-diagnostic.json) · [Replay instructions](reproduction.txt)
