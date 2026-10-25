"""Distinct execution, numerical, engineering and acceptance dispositions."""
import math

from engineering.design_search.contracts import FLAGS


def gate(name, state, reason, **values):
    if state not in {'pass', 'fail', 'unknown'} or not name or not reason:
        raise ValueError('identified explained engineering gate required')
    return dict(id=name, state=state, reason=reason, values=values)


def preflight_result(scenario, vehicle_id, gates):
    """A completed preflight can correctly refuse a dynamic execution."""
    if not gates or len({g['id'] for g in gates}) != len(gates):
        raise ValueError('unique nonempty gate set required')
    for item in gates:
        gate(item['id'], item['state'], item['reason'], **item.get('values', {}))
    failures = [g['id'] for g in gates if g['state'] == 'fail']
    unknowns = [g['id'] for g in gates if g['state'] == 'unknown']
    ready = not (failures or unknowns)
    return dict(schema='osr-trip-evidence-attempt/1', scenario_id=scenario['scenario_id'],
                case_id=scenario['case_id'], vehicle_id=vehicle_id, preflight_execution='executed',
                dynamic_execution='not-run' if not ready else 'ready-not-run',
                numerical_validity='not-assessed', engineering_screen='fail' if failures else 'unknown' if unknowns else 'pass',
                evidence_maturity='definition', launch_authorised=False, post_fault_trajectory_produced=False,
                distance_travelled_m=0., trajectory=None, gates=gates,
                failed_gates=failures, unknown_gates=unknowns,
                explanation='Preflight is not stationary hover, controlled travel or a capture demonstration.', **FLAGS)


def energy_balance(*, dc_J, copper_J, emf_J, field_change_J, cooling_J=0., heat_change_J=None):
    """Port accounting: don't subtract cooling twice from winding electrical work."""
    vals = [dc_J, copper_J, emf_J, field_change_J, cooling_J]
    if any(type(x) not in (int, float) or not math.isfinite(x) for x in vals):
        raise ValueError('finite port energies required')
    residual = dc_J-copper_J-emf_J-field_change_J
    return dict(electrical_residual_J=residual,
                thermal_residual_J=None if heat_change_J is None else copper_J-cooling_J-heat_change_J,
                separated_electrical_and_thermal_ports=True)
