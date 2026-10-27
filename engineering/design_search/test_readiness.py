"""Bind unexecuted wheel/LIM test specifications to one numerical candidate.

Records and numeric acceptance limits are unavailable. This is a test programme,
not a qualification importer or native-evaluator admission. The retained Q01
authenticator remains a reference; its magnetic-support protocols cannot qualify
a wheel/LIM article. A built revision needs its own propagated physical identity.
"""
from copy import deepcopy
from pathlib import Path
import json

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest, identity
from . import railway_bundle, requirement_policy

PRODUCER='engineering/design_search/test_readiness.py'
DEFINITIONS='engineering/design_search/data/wheel-LIM-test-program.json'
FLAGS=dict(physical_accepted=False,engineering_accepted=False,configuration_adopted=False,
           manufacturing_release=False,operating_release=False)


def definitions(root=ROOT):
    value=json.loads((Path(root)/DEFINITIONS).read_bytes())
    if value.get('schema')!='osr-wheel-LIM-test-program-definitions/1' or value.get('native_dispatch_allowed') is not False or value.get('physical_accepted') is not False:
        raise ValueError('Explicit unexecuted wheel/LIM programme required')
    rows=value['protocols']
    if len(rows)!=10 or {p['id'] for p in rows}!={f'T{i:02}' for i in range(1,11)}:
        raise ValueError('All ten required test families must remain present')
    for row in rows:
        if row['executed'] is not False or row['physical_accepted'] is not False or row['status']!='planned-inputs-absent':
            raise ValueError('Planning definitions cannot assert execution or physical acceptance')
        if any(row[k] is not None for k in ('approved_limits','approved_procedure_revision',
                 'approved_sample_matrix_and_repetitions','approved_uncertainty_budget','article_configuration_sha256','independent_review')):
            raise ValueError('Approved procedures and limits require the external qualification workflow')
        if any(row[k] for k in ('raw_measurement_files','article_serials','material_batches')):
            raise ValueError('Physical records cannot be inserted into planning definitions')
        channels=row['measured_channels']
        if not isinstance(channels,list) or not channels or any(not isinstance(c,dict) or any(not isinstance(c.get(k),str) or not c[k].strip() for k in ('name','unit')) for c in channels):
            raise ValueError('Nonempty typed channels and units required')
        names=[c['name'] for c in channels]
        if len(names)!=len(set(names)) or (row['id']!='T10' and names.count('time_s')!=1):
            raise ValueError('Distinct named measurement/record channels and units required')
        if not row['load_duty_environment'] or not row['acceptance_criteria'] or row['subject_selector'] not in ('body','motor','railway'):
            raise ValueError('Required conditions, criterion derivations and subject scope missing')
        if any(any(not isinstance(c.get(k),str) or not c[k].strip() for k in ('observable','unit','derivation_required')) for c in row['acceptance_criteria']):
            raise ValueError('Typed criterion observables, units and derivation needs required')
        if any(c['limit'] is not None or c['approval_status']!='unassigned' for c in row['acceptance_criteria']):
            raise ValueError('Planning targets cannot become approved acceptance criteria')
    return value


def build(bundle, *, root=ROOT):
    railway_bundle.validate(bundle);root=Path(root);data=definitions(root)
    if bundle['family_id'] not in ('P1','P4') or bundle['motor_definition'].get('family')!='double-sided-slotted-LIM':
        raise ValueError('This programme covers explicit P1/P4 wheel and station-LIM candidates; another propulsion family requires its own protocol revision')
    if digest(root/PRODUCER)!=digest(__file__):
        raise ValueError('Executing test-programme producer differs from source root')
    subject=dict(numerical_parent_bundle_id=bundle['bundle_id'],bundle_definition_id=bundle['definition_id'],
                 body_candidate_id=bundle['body_candidate_id'],support_component_id=bundle['support_component_id'],
                 motor_component_id=bundle['propulsion_component_id'],brake_definition_id=bundle['brake_definition']['brake_definition_id'],
                 requirement_revision=bundle['requirement_revision'])
    policy=requirement_policy.catalogue()
    links={
        'T01':['physical.clearance','safety.independent_stop'],
        'T02':['safety.structural_integrity','physical.temperature'],
        'T03':['safety.structural_integrity','physical.clearance'],
        'T04':['safety.structural_integrity','physical.clearance'],
        'T05':['functional.integrated_service','physical.temperature'],
        'T06':['physical.temperature','functional.integrated_service'],
        'T07':['safety.independent_stop'],
        'T08':['functional.integrated_service','accessibility.boarding_egress'],
        'T09':['safety.structural_integrity','physical.clearance','accessibility.boarding_egress'],
        'T10':['target.whole_life_cost']}
    protocols=[]
    for template in data['protocols']:
        p=deepcopy(template)
        p['subject_binding']=deepcopy(subject)
        p['requirement_policy_links']=[dict(id=n,category=policy['criteria'][n]['category']) for n in links[p['id']]]
        p['article_binding']=dict(as_built_candidate_id=None,article_configuration_sha256=None,
            as_built_revision_required=True,canonical_propagation_required_for_physical_changes=True,
            numerical_parent_is_not_an_as_built_record=True)
        p['planning_context']=dict(cars=bundle['cars'],car_length_m=bundle['car_length_m'],
            architecture_family_id=bundle['family_id'],unweighed_architecture_equipment=deepcopy(bundle['unweighed_architecture_equipment']),
            station_spacing_m=bundle['architecture_case']['physical_definition']['route']['station_spacing_m'],
            normal_people_per_car=46,crowd_structural_control_per_car=160,
            headway_s=bundle['requirements']['target_headway_s'],speed_cap_m_s=bundle['requirements']['speed_cap_m_s'],
            complete_installed_mass_kg=None,approved_operating_limits=False)
        if p['id']=='T05':
            p['coordinate_definition']=dict(position='Secondary longitudinal start relative to fixed primary, not route leading-nose position',
                forces='Primary-fixed longitudinal/transverse/vertical axes',
                conversion_to_train_route='Requires actual installed secondary transforms, car offsets and wayside section locations')
        elif p['id']=='T08':
            p['coordinate_definition']=dict(position='Train leading-nose route chainage; authenticated localisation/datum and uncertainty required')
        p['unaccepted_record_template']=dict(schema='osr-wheel-LIM-test-record-template/1',
            numerical_parent_bundle_id=bundle['bundle_id'],protocol_id=p['id'],
            as_built_candidate_id=None,procedure_revision=None,article_serials=[],material_batches=[],
            provenance_kind='unexecuted-template',raw_file=None,samples=[],calibrations=[],
            approved_limits=[],independent_attestations=[],accepted=False)
        p['native_dispatch_allowed']=False
        p['evidence_request_id']=identity(p)
        protocols.append(p)
    value=dict(schema='osr-candidate-wheel-LIM-test-programme/1',candidate_id=bundle['candidate_id'],
        body_candidate_id=bundle['body_candidate_id'],bundle_definition_id=bundle['definition_id'],
        requirement_revision=bundle['requirement_revision'],revision=data['revision'],protocols=protocols,
        shared_evidence_requirements=data['shared_evidence_requirements'],
        retained_design_bounds=data['numerical_bounds_only'],catalogue_data_is_not_delivered_lot_evidence=True,
        source_catalogue_values_independently_reverified=False,
        qualification_workflow=data['qualification_workflow'],requirement_policy_id=policy['policy_id'],
        qualification_admission='Held: current wheel/LIM subject/protocol adapter and external authentication/approved criteria required',
        executed_physical_tests=0,approved_numeric_limits=0,complete_equipped_vehicles=0,
        data_availability_provenance='Project-owner declaration2026-10-27: physical records unavailable; numerical design and required-test identification authorised',
        native_dispatch_allowed=False,source_sha256={PRODUCER:digest(root/PRODUCER),DEFINITIONS:digest(root/DEFINITIONS),
            requirement_policy.PRODUCER:digest(Path(requirement_policy.__file__))},**FLAGS)
    value['evaluation_id']=identity(value)
    return value


def verify(value,bundle,*,root=ROOT):
    if value!=build(bundle,root=root):
        raise ValueError('Test programme differs from exact candidate, current definitions or unexecuted status')
    return dict(verified=True,evaluation_id=value['evaluation_id'],executed_physical_tests=0,
                native_dispatch_allowed=False,physical_accepted=False)
