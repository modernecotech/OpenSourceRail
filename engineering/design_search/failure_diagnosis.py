"""Typed observations drive geometry, model or evidence work separately."""
from engineering.station_rail.common import identity


def diagnose(candidate,*,rigidity=None,native=None,interfaces=None):
    facts=[];actions=[]
    if rigidity and rigidity['mechanism_count']:
        facts.append(dict(kind='conditional-design-failure',question='Declared pin-jointed load path has unconstrained motions',mechanisms=rigidity['mechanism_count']))
        actions.append(dict(operator='triangulate-underfloor',kind='physical-topology',reason='Close real axial load paths below passenger openings without adding ground restraints'))
    elif native and native.get('numerical_validity') in ('unknown','outside_linear_domain'):
        facts.append(dict(kind='model-domain-or-numerical',question='Resolve numerical validity before treating the displacement as physical performance'))
        actions.append(dict(operator=None,kind='evaluator-development',reason='Independent residual/domain check; nonlinear kinematics or a different structural formulation may be required'))
    if interfaces and interfaces.get('compatibility_status')=='fail':
        facts.append(dict(kind='interface-incompatibility',question='Repair the identified typed port, function, opening or assembly incompatibility'))
    actions += [dict(operator='integrate-roof-functions',kind='independent-design-experiment',reason='Compare shared roof/PV/channel manufacture against separate replaceable components; no inference from an invalid model'),
        dict(operator='redistribute-rib-layout',kind='physical-layout',reason='Explore different member positions and load introductions while preserving aperture keepouts'),
        dict(operator=None,kind='full-body-evaluator',reason='Develop validated laminate/shell/joint, buckling, fatigue, mode and thermal models for this exact new topology')]
    r=dict(schema='osr-generative-diagnosis/1',candidate_id=candidate['candidate_id'],definition_id=candidate['definition_id'],findings=facts,actions=actions,
        provisional_target_rejection=False,integrated_suitability='unknown');r['diagnosis_id']=identity(r);return r
