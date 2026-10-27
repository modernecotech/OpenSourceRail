"""Explicit route revision of a canonical, fixed-contract railway bundle.

The earlier bounded 2 km experiment retains its source/evaluation contract.
A different corridor rematerializes its architecture, motor coverage and brake
identity while preserving unchanged vehicle stock and its unresolved equipment.
"""
from copy import deepcopy
from math import isfinite
from pathlib import Path
from engineering.station_rail import ROOT, vehicle
from engineering.station_rail.common import digest, identity
from . import railway_bundle, railway_architecture as architecture

PRODUCER = 'engineering/design_search/route_bundle.py'


def materialize(body, *, family='P1', root=ROOT, distance_m=2000.):
    if type(distance_m) not in (int, float) or not isfinite(distance_m) or distance_m not in (1500., 2000.):
        raise ValueError('Explicit positive finite 1500/2000 m reference-route distance required')
    base = railway_bundle.materialize(body, family=family, root=root)
    if distance_m == 2000.:
        return base
    if family not in ('P1', 'P4'):
        raise ValueError('Route closure evaluator currently supports P1 and separate P4 research')
    reference = vehicle.build(root)
    reference.update(body_candidate_id=body['candidate_id'], propulsion_component_id=base['propulsion_component_id'])
    old = base['architecture_case']
    case = architecture._configuration(family, base['cars'], float(distance_m), old['requirements']['speed_cap_m_s'],
                                      old['knobs'], base['architecture_specification'], reference)
    for name in ('propulsion_definition_id', 'component_substitutions'):
        case['physical_definition'][name] = deepcopy(old['physical_definition'][name])
    candidate_id = identity(case['physical_definition'])
    case['candidate_id'] = candidate_id
    case['capability_composition'] = architecture.capabilities.composition(family, candidate_id, case['requirement_revision'])
    case['parent_case_ids'] = [old['case_id']]
    case['generation'] = old['generation'] + 1
    case['case_id'] = identity({k: v for k, v in case.items() if k != 'case_id'})
    result = deepcopy(base)
    result.update(candidate_id=candidate_id, bundle_id=candidate_id, architecture_case=case,
                  parent_bundle_id=base['bundle_id'], revision_reason='Explicit 1500 m route and installed station-motor coverage revision')
    # Geometry and torque/pressure hypotheses remain unchanged. The new plant
    # identity binds them to this corridor; no qualification is inherited.
    brake = result['brake_definition']
    brake['candidate_id'] = candidate_id
    brake['brake_definition_id'] = identity({k: v for k, v in brake.items() if k != 'brake_definition_id'})
    result['source_sha256'][PRODUCER] = digest(Path(root) / PRODUCER)
    result['definition_id'] = identity({k: v for k, v in result.items() if k != 'definition_id'})
    return railway_bundle.validate(result)
