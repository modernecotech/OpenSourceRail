"""One provisional constraint contract for reduced and refined load cases.

Unknown capacities stay open. Missing, negative or nonfinite demands cannot
pass a declared screen. These limits are research assumptions, not approval.
"""
import math


def evaluate(demands, limits, *, span_m, pier_height_m, axial_resistance_n, context=None):
    thresholds = {
        'relative_deflection': span_m * limits['relative_deflection_span_ratio'],
        'settlement': limits['settlement_m'],
        'gross_elastic_stress': limits['gross_elastic_stress_pa'],
        'pier_gross_elastic_stress': limits['gross_elastic_stress_pa'],
        'pier_drift': pier_height_m * limits['pier_drift_ratio'],
        'planning_axial_resistance': axial_resistance_n,
        'max_lift_mass': limits['max_lift_mass_kg'],
    }
    violations = []
    for metric, limit in thresholds.items():
        value = demands.get(metric)
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError('missing/invalid research demand: ' + metric)
        if limit is not None:
            if type(limit) not in (int, float) or not math.isfinite(limit) or limit <= 0:
                raise ValueError('invalid provisional limit: ' + metric)
            if value > limit:
                violations.append({**(context or {}), 'metric': metric, 'value': value,
                                   'provisional_limit': limit, 'ratio': value / limit})
    return violations


def convergence(levels, metrics, tolerance=.05):
    """Compare the last two meshes; normalize tiny zero responses explicitly."""
    checks = {}
    for metric in metrics:
        values = [r[metric] for r in levels]
        if any(not math.isfinite(v) or v < 0 for v in values):
            raise ValueError('invalid convergence observable: ' + metric)
        change = abs(values[-1] - values[-2]) / max(values[-1], values[-2], 1e-12)
        checks[metric] = dict(relative_change=change, passed=change <= tolerance)
    return dict(checks=checks, passed=all(r['passed'] for r in checks.values()), relative_limit=tolerance)
