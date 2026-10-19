"""Exact assembly/civil/vehicle interface for existing coupled research adapters.

This reconciles represented mass and ledger inputs. It does not run a passage or
substitute synthetic LM3 body/contact data for a Baghdad vehicle specification.
"""
import math
import numpy as np

from osr_mech.vehicle_mass_properties import combined_inertia
from engineering.twin_workflow import core
from engineering.continuous_design import civil_kit
from engineering.integration_programme.battery import power_ledger
from . import baseline, models, evaluate, reactions

ADAPTERS={
    'spatial-passage':'engineering.civil_exploration.spatial_vehicle.run_spatial',
    'flexible-carbody':'engineering.integration_programme.flexible_vehicle.FlexibleVehicle',
    'controller-battery-thermal':'engineering.integration_programme.native_spatial.NativeSpatialLoop',
    'cad-analysis-correspondence':'engineering.integration_programme.correspondence.audit',
    'mass-inertia':'osr_mech.vehicle_mass_properties.combined_inertia',
    'power':'engineering.integration_programme.battery.power_ledger',
    'civil-reactions':'engineering.assembly_design.reactions.envelope',
}
PASSAGE_GATES=(
    'adopted-axle-and-suspension-map','native-cad-to-analysis-correspondence',
    'complete-six-car-entry-and-exit','time-step-convergence','deck-spatial-convergence',
    'rail-mesh-convergence','carbody-modal-convergence','contact-domain-and-wheel-unloading',
    'reaction-and-energy-ledger-reconciliation','clearance-and-ride-criteria',
    'curving-braking-wind-and-degraded-cases','calibrated-bearing-ground-and-contact-laws',
    'target-controller-timing-and-physical-interfaces',
)


def _revision(value,label):
    if value.get('revision')!=core.digest({k:v for k,v in value.items() if k!='revision'}):
        raise ValueError(label+' revision differs')


def _vector(value,label):
    if not isinstance(value,list) or len(value)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in value):
        raise ValueError('finite XYZ '+label+' required')
    return np.asarray(value,float)


def mass_properties(parts,allocations):
    """Reuse the existing rotated tensor/parallel-axis aggregation once per part."""
    rows=[];seen=set()
    for allocation in allocations:
        if not allocation.get('id') or allocation['id'] in seen:raise ValueError('unique installed allocation identity required')
        seen.add(allocation['id']);translation=_vector(allocation.get('translation_m'),'placement')
        rotation=np.asarray(allocation.get('rotation'),float)
        if rotation.shape!=(3,3) or not np.isfinite(rotation).all() or not np.allclose(rotation.T@rotation,np.eye(3),atol=1e-10) or not np.isclose(np.linalg.det(rotation),1.):
            raise ValueError('proper installed rotation required')
        for part in parts:
            p=part['properties'];point=rotation@_vector(p['cg_m'],'part centroid')+translation
            if type(p['mass_kg']) not in (int,float) or not math.isfinite(p['mass_kg']) or p['mass_kg']<=0:
                raise ValueError('positive finite represented part mass required')
            rows.append(dict(id=allocation['id']+'/'+part['id'],mass_kg=p['mass_kg'],
                **{axis+'_m':float(point[i]) for i,axis in enumerate('xyz')},
                inertia_tensor_kg_m2=p['inertia_tensor_kg_m2'],rotation_matrix=rotation.tolist()))
    total=sum(r['mass_kg'] for r in rows)
    if total<=0:raise ValueError('nonempty installed mass allocation required')
    cg={axis:sum(r['mass_kg']*r[axis+'_m'] for r in rows)/total for axis in 'xyz'}
    return dict(mass_kg=total,cg_m=[cg[a] for a in 'xyz'],**combined_inertia(rows,cg,None),
        included_part_instance_ids=[r['id'] for r in rows],
        uncertainty='Material, purchased-envelope and placement uncertainty remain unqualified')


def build(policy,cassette,bearing,kit,vehicle,allocations,children,*,expected_sources):
    """Validate exact interfaces and produce an openly held integration contract."""
    current=baseline.sources()
    if expected_sources!=current:raise ValueError('integration source snapshot stale')
    source_revision=core.digest(current);_revision(vehicle,'vehicle')
    if vehicle.get('architecture')!=policy['architecture'] or vehicle.get('architecture')!='baghdad-six-car':
        raise ValueError('integration architecture differs')
    if not vehicle.get('context_id') or len(vehicle.get('cars',[]))!=6 or len(set(vehicle['cars']))!=6:
        raise ValueError('exact six-car context required')
    for candidate,kind in ((cassette,'service-cassette'),(bearing,'bearing-seat')):
        if candidate['kind']!=kind or core.digest(candidate)!=core.digest(models.build(policy,kind,candidate['variables'])):
            raise ValueError('integration candidate/geometry revision stale')
    if not allocations or len(allocations)!=6 or {a.get('body_id') for a in allocations}!=set(vehicle['cars']):
        raise ValueError('one explicit cassette allocation for each configured car required')
    if any(a.get('candidate_revision')!=cassette['revision'] or a.get('architecture')!=vehicle['architecture'] or a.get('context_id')!=vehicle['context_id'] for a in allocations):
        raise ValueError('installed allocation revision/architecture/context differs')
    expected={'cassette':cassette['revision'],'bearing':bearing['revision'],'civil-kit':core.digest(kit),'software':core.digest(evaluate.control_source('branch'))}
    if set(children)!=set(expected):raise ValueError('complete exact physical and software child set required')
    child_states={}
    for name,revision in expected.items():
        child=children[name]
        if any(child.get(k)!=value for k,value in dict(candidate_revision=revision,architecture=vehicle['architecture'],context_id=vehicle['context_id'],source_revision=source_revision).items()):
            raise ValueError('child exact revision/context/source differs: '+name)
        if child.get('result_sha256')!=core.digest(child.get('result')) or child['result'].get('candidate_revision')!=revision:
            raise ValueError('child result binding differs: '+name)
        evidence=child.get('mandatory_evidence')
        if not evidence or any(e.get('candidate_revision')!=revision or e.get('state') not in ('passed','failed','hold') for e in evidence):
            raise ValueError('revision-bound mandatory child evidence required')
        states=[e['state'] for e in evidence]+[child['result'].get('state')]
        if child['result'].get('failed_checks'):states.append('failed')
        if child['result'].get('held_checks'):states.append('hold')
        if any(child['result'].get(flag) is True for flag in core.FLAGS):
            raise ValueError('research child asserts an unsupported release: '+name)
        if any(s in ('failed','rejected') for s in states):child_states[name]='failed'
        elif any(s not in ('passed','screened-with-open-design-requirements') for s in states):child_states[name]='hold'
        else:child_states[name]='passed'
    # Caller-provided passing summaries cannot override current mandatory physics.
    current_cassette=evaluate.evaluate(policy,cassette)
    if current_cassette['failed_checks']:child_states['cassette']='failed'
    elif current_cassette['held_checks'] and child_states['cassette']!='failed':child_states['cassette']='hold'
    installed=mass_properties(cassette['contract']['parts'],allocations)
    local=mass_properties(cassette['contract']['parts'],[dict(id='cassette-local',translation_m=[0.,0.,0.],rotation=np.eye(3).tolist())])
    facts=baseline.facts(policy);a=policy['pilots']['bearing-seat']['assumptions']
    train=reactions.revisioned(dict(architecture=vehicle['architecture'],mass_cases_kg=[m+installed['mass_kg'] for m in facts['train.mass_cases']],
        cars=a['train_cars'],car_length_m=facts['train.car_length'],tracks=a['tracks'],span_m=a['span_m'],gravity_m_s2=a['gravity_m_s2'],
        permanent_factor=a['vertical_factor'],variable_factor=a['vertical_factor']))
    seat=reactions.revisioned(dict(candidate_revision=bearing['revision'],mass_kg=sum(p['properties']['mass_kg'] for p in bearing['contract']['parts'])))
    force=reactions.envelope(kit,train,seat,expected_kit_revision=core.digest(kit),expected_train_revision=train['revision'])
    powers=[];heat_rows=[];thermal_complete=True
    for allocation in allocations:
        if type(allocation.get('power_w')) not in (int,float) or not math.isfinite(allocation['power_w']):
            raise ValueError('finite electrical power allocation required')
        powers.append(dict(id=allocation['id'],power_w=allocation['power_w']))
        terms=[allocation.get(k) for k in ('heat_w','mechanical_output_w','storage_rate_w')]
        known=all(type(v) in (int,float) and math.isfinite(v) for v in terms)
        thermal_complete &= known
        residual=allocation['power_w']-sum(terms) if known else None
        if known and abs(residual)>1e-9*max(1.,abs(allocation['power_w'])):raise ValueError('power/heat/mechanical/storage ledger does not reconcile')
        heat_rows.append(dict(id=allocation['id'],heat_w=terms[0],mechanical_output_w=terms[1],storage_rate_w=terms[2],residual_w=residual))
    failed=[name for name,state in child_states.items() if state=='failed'];held=[name for name,state in child_states.items() if state=='hold']
    result=dict(schema='osr-baghdad-assembly-integration/1',architecture=vehicle['architecture'],context_id=vehicle['context_id'],
        source_revision=source_revision,vehicle_revision=vehicle['revision'],candidate_revisions=expected,
        installed_allocation_revision=core.digest(allocations),installed_allocations=allocations,
        local_cassette_properties=local,gross_added_properties=installed,
        removal_credit_mass_kg=0.,net_vehicle_cg_m=None,net_vehicle_inertia_kg_m2=None,
        mass_change_basis='Gross addition only; complete baseline vehicle CG/inertia and exact removed-scope ledger absent. No removal or lightening credit',
        electrical_ledger=power_ledger(powers),thermal_ledger=dict(entries=heat_rows,reconciled=True if thermal_complete else None),
        force_ledger=force,current_cassette_screen=current_cassette,child_states=child_states,disqualified_children=failed+held,
        required_reassessments=[dict(domain=domain,candidate_revision=revision,load_revision=force['revision'],state='hold')
            for domain,revision in (('bearing-resistance',bearing['revision']),('complete-civil-kit',core.digest(kit)),('vehicle-mounts-and-axle-map',vehicle['revision']))],
        interface_consistent=True,children_eligible=not failed and not held,
        admitted_for_system_simulation=False,state='failed' if failed else 'hold',
        existing_adapters=ADAPTERS,full_passage_acceptance={name:dict(state='hold',evidence=None) for name in PASSAGE_GATES},
        open_requirements=['Adopt six-car placement, mass/axle/suspension and power/heat maps',
            'Reconcile owned CAD, rail/bearing/ground properties with existing spatial adapter inputs',
            'Execute complete train passage with time, spatial, rail and modal convergence; synthetic LM3 identities are not Baghdad equivalence'],
        scope='Exact represented-part gross-addition sensitivity and provisional ledger interface; complete baseline allocation, net changes, adapter correspondence and coupled passage are unverified',
        full_train_passage_executed=False,digital_specification_complete=False,**core.FLAGS)
    if current!=baseline.sources():raise ValueError('integration sources changed during evaluation')
    result['revision']=core.digest(result)
    return result


def snapshot(policy=None):
    """Reproducible provisional interface for the closure report, not an admission."""
    from . import contracts
    from osr_mech.family_definition import family_definition
    policy=policy or baseline.validate(core.read(baseline.DATA));prototype=contracts.prototype_configuration()
    def candidate(kind):
        variables={name:values[0] for name,values in policy['pilots'][kind]['domains'].items()}
        if kind=='bearing-seat':variables['bearing_family']='uk-spherical-candidate'
        return models.build(policy,kind,variables)
    cassette=candidate('service-cassette');bearing=candidate('bearing-seat');kit=civil_kit.build(civil_kit.defaults())
    cars=family_definition('metro-6car')['cars'];context=prototype['id']
    vehicle=reactions.revisioned(dict(architecture=policy['architecture'],context_id=context,cars=[c['id'] for c in cars],
        prototype_revision=prototype['revision'],base_cg_m=None,base_inertia_kg_m2=None,
        basis='Six-car planning length/frame only; complete vehicle allocation and actual mount datums not adopted'))
    a=policy['pilots']['service-cassette']['assumptions']
    allocations=[dict(id=car['id']+'/service-cassette',body_id=car['id'],candidate_revision=cassette['revision'],architecture=policy['architecture'],context_id=context,
        translation_m=[car['centre_x_m'],0.,0.],rotation=np.eye(3).tolist(),power_w=a['lv_voltage_v']*a['branch_current_a'],
        heat_w=None,mechanical_output_w=None,storage_rate_w=None,
        status='Provisional one-per-car origin placement for sensitivity only; actual mounting and power/heat maps require adoption') for car in cars]
    sources=baseline.sources();source_revision=core.digest(sources)
    results={'cassette':evaluate.evaluate(policy,cassette),'bearing':evaluate.evaluate(policy,bearing),
        'civil-kit':dict(candidate_revision=core.digest(kit),state='hold',reason='Complete structural and ground acceptance absent'),
        'software':dict(candidate_revision=core.digest(evaluate.control_source('branch')),state='passed',trial=evaluate.control_trial())}
    revisions={'cassette':cassette['revision'],'bearing':bearing['revision'],'civil-kit':core.digest(kit),'software':core.digest(evaluate.control_source('branch'))}
    children={name:dict(candidate_revision=revisions[name],architecture=policy['architecture'],context_id=context,source_revision=source_revision,
        result=result,result_sha256=core.digest(result),mandatory_evidence=[dict(candidate_revision=revisions[name],state='hold',scope='Native physical/interface or target integration evidence still required')]) for name,result in results.items()}
    return build(policy,cassette,bearing,kit,vehicle,allocations,children,expected_sources=sources)
