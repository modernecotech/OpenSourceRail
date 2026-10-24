"""Bounded mass/heat/deformation/gap fixed points with explicit unknown states."""
from copy import deepcopy

from .contracts import FLAGS, finite, identity, inventory_summary, mass_properties, validate_candidate

DEFAULT_TOLERANCES=dict(mass_kg=.001,heat_w=.1,temperature_c=.01,deformation_m=1e-6,gap_m=1e-6)


def iterate(candidate,step,*,initial_state=None,tolerances=None,max_iterations=16,relaxation=.5):
    """step(candidate,state) returns state, optional revised candidate, constraints.

    A changed installed mass needs a revised physical inventory. A numerical
    state cannot silently invent cooler/reinforcement stock or zero unknowns.
    """
    validate_candidate(candidate);limits=dict(DEFAULT_TOLERANCES if tolerances is None else tolerances)
    if set(limits)!=set(DEFAULT_TOLERANCES):raise ValueError('all coupling residual dimensions required')
    for key,value in limits.items():finite(value,'positive '+key+' tolerance',True)
    if type(max_iterations) is not int or not 1<=max_iterations<=1000 or not 0<relaxation<=1:raise ValueError('bounded coupling settings required')
    initial=mass_properties(candidate);history=[];active=deepcopy(candidate)
    state=dict(mass_kg=initial['total_mass_kg'],heat_w=0.,temperature_c=40.,deformation_m=0.,gap_m=.008)
    if initial_state is not None:state.update(deepcopy(initial_state))
    binding=dict(candidate_id=candidate['candidate_id'],initial_state=state,tolerances=limits,max_iterations=max_iterations,relaxation=relaxation)
    def result(status,reason):
        value=dict(schema='osr-design-coupling/1',candidate_id=active['candidate_id'],initial_candidate_id=candidate['candidate_id'],
            coupling_status=status,reason=reason,state=state,residual_history=history,iterations=len(history),
            settings=binding,unknown_stock_ids=inventory_summary(active)['unknown_stock_ids'],**FLAGS)
        value['coupling_id']=identity(value);return value
    if not inventory_summary(candidate)['complete_installed_distribution']:return result('unknown','Installed stock has unknown mass/CG/inertia; no zero-stock iteration is permitted.')
    for key in limits:finite(state[key],key)
    for number in range(max_iterations):
        response=step(deepcopy(active),deepcopy(state))
        if response.get('status') in ('unknown','failed','nonconverged'):
            return result(response['status'],response.get('reason','coupled evaluator refused'))
        revised=response.get('candidate',active);validate_candidate(revised);properties=mass_properties(revised)
        if properties['total_mass_kg'] is None:
            active=revised;return result('unknown','Coupling introduced unweighed installed stock.')
        proposed=response.get('state',{})
        if set(proposed)!=set(limits):return result('unknown','Evaluator omitted a coupled state dimension.')
        for key in limits:finite(proposed[key],key)
        if abs(proposed['mass_kg']-properties['total_mass_kg'])>limits['mass_kg']:
            return result('failed','Proposed mass differs from the revised physical inventory.')
        if proposed['gap_m']<=0:return result('failed','Nonpositive physical magnetic gap.')
        constraints=response.get('constraints',[])
        if any(row.get('state') not in ('pass','fail','unknown','not-assessed') for row in constraints):
            return result('unknown','A coupled constraint lacks a typed assessed state.')
        residuals={key:abs(proposed[key]-state[key]) for key in limits}
        history.append(dict(iteration=number+1,candidate_id=revised['candidate_id'],proposed_state=deepcopy(proposed),residuals=residuals,constraints=constraints))
        active=deepcopy(revised)
        if any(row.get('state')=='fail' for row in constraints):return result('failed','A critical coupled constraint failed.')
        if any(row.get('state') in ('unknown','not-assessed') for row in constraints):return result('unknown','A critical coupled constraint is unknown.')
        if all(residuals[key]<=limits[key] for key in limits):
            state=deepcopy(proposed);return result('converged','All declared dimensional residuals meet tolerance.')
        # Installed mass is an exact ledger quantity, not a relaxation variable.
        state={key:proposed[key] if key=='mass_kg' else state[key]+relaxation*(proposed[key]-state[key]) for key in limits}
    return result('nonconverged','Coupling iteration budget exhausted; last iterate is not a passing result.')
