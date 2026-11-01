# Interrupted architecture reachability closure

The current architecture campaign has 3 interrupted reachability questions among 509 evaluations. A conservative off-power stopping bound proves 3 of these scenarios cannot reach the next commanded power window or destination. 0 remain unresolved by this bound.

The original time histories remain interrupted at their declared runtime/step limit. No limit or stored trajectory was changed. This supplement records separate evaluation identities linked to the exact candidate, requirement, case, source evaluation and trace index. The inference is conditional on the recorded terminal state; energy balance does not provide a rigorous position/speed error enclosure. An outward comparison margin prevents equality or near-boundary rounding from establishing infeasibility.

## Necessary bound

For forward speed, nonnegative headwind and quadratic drag, the opposing force is at least `F_floor = m*g*(rolling + uphill_grade) + constant_drag + k*headwind²`. When that floor is positive, work/energy gives `s_stop ≤ (m + rotating_equivalent_mass)*v²/(2*F_floor)` and momentum gives `t_stop ≤ (m + rotating_equivalent_mass)*v/F_floor`. Rotating mass contributes to inertia; gravity and rolling load use translation mass only.

The bound is applied only outside commanded powered windows. It checks the nearest future powered-window start as well as the destination, so an accessible booster cannot be ignored. A nonpositive floor, a powered tail or an energy-invalid source remains unresolved.

| Cars | Source runtime | Tail position | Tail speed | Latest stop position | Minimum shortfall to next target | Disposition |
|---:|---:|---:|---:|---:|---:|---|
| 4 | 600.0 s | 2546.717 m | 0.608 m/s | 2554.178 m | 445.822 m | infeasible-under-declared-demand-model |
| 6 | 600.0 s | 2546.717 m | 0.608 m/s | 2554.178 m | 445.822 m | infeasible-under-declared-demand-model |
| 8 | 600.0 s | 2546.717 m | 0.608 m/s | 2554.178 m | 445.822 m | infeasible-under-declared-demand-model |

The three P3 rows differ in formation but share the same declared per-car mass and motion state. Their result is conditional on the campaign's command windows and accounted-mass hypothesis. Changing the power commands, speed, route or hardware creates another evaluation/configuration. No available motor force, installed equipment, actual stopping performance, engineering acceptance or operating approval is established.

Reproduce with `python3 -m engineering.design_search.architecture_reach_closure build` and `python3 -m engineering.design_search.architecture_reach_closure verify`.

[Exact evaluations](result.json) · [Source and payload receipt](manifest.json) · [Parent architecture study](../v06-architecture/README.md)
