"""Exact constant-duty lumped thermal update; parameters need separate evidence."""
import math


def temperature_step(temperature_C, *, ambient_C, heat_W, capacity_J_K, conductance_W_K, dt_s):
    for value in (temperature_C, ambient_C, heat_W, capacity_J_K, conductance_W_K, dt_s):
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError('finite declared thermal quantities required')
    if min(capacity_J_K, dt_s) <= 0 or min(heat_W, conductance_W_K) < 0:
        raise ValueError('positive thermal capacity/time and nonnegative duty/conductance required')
    if conductance_W_K == 0:
        end = temperature_C+heat_W*dt_s/capacity_J_K
    else:
        equilibrium = ambient_C+heat_W/conductance_W_K
        end = equilibrium+(temperature_C-equilibrium)*math.exp(-conductance_W_K*dt_s/capacity_J_K)
    stored = capacity_J_K*(end-temperature_C)
    return dict(temperature_C=end, generated_heat_J=heat_W*dt_s, stored_heat_change_J=stored,
                rejected_heat_J=heat_W*dt_s-stored, candidate_thermal_validation=False)
