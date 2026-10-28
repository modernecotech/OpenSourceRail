"""Unapproved physical-test requests for the new segmented-fin reference cells."""
from copy import deepcopy
from pathlib import Path
from engineering.design_search import test_readiness,railway_bundle
from . import ROOT,FLAGS,identity,digest


def build(b,*,root=ROOT):
    railway_bundle.validate(b)
    definitions=test_readiness.definitions(root);protocols=[]
    subject=dict(candidate_id=b['candidate_id'],bundle_definition_id=b['definition_id'],body_candidate_id=b['body_candidate_id'],
        motor_component_id=b['propulsion_component_id'],support_component_id=b['support_component_id'],
        brake_definition_id=b['brake_definition']['brake_definition_id'],requirement_revision=b['requirement_revision'])
    for old in definitions['protocols']:
        p=deepcopy(old);p['subject_binding']=deepcopy(subject)
        p['protocol_revision_required']='SEGMENTED-FIN-EQUIPPED-CELL-1'
        p['planning_context']=dict(formation=b['architecture_case']['physical_definition']['formation'],
            actual_secondary_segments=b['route_secondary_segments_at_front_zero_m'],actual_axles=b['route_axle_offsets_from_leading_nose_m'],
            mass_interval_kg_per_car=b['mass_interval_kg_per_car'],complete_installed_mass_kg=None,
            inherited_legacy_motor_protocol_acceptance=False)
        p['native_dispatch_allowed']=False;p['evidence_request_id']=identity(p);protocols.append(p)
    value=dict(schema='osr-segmented-reference-cell-test-programme/1',revision='SEGMENTED-FIN-EQUIPPED-CELL-1',
        **subject,protocols=protocols,approved_numeric_limits=None,approved_procedure=None,
        executed_physical_tests=0,physical_records=[],native_dispatch_allowed=False,
        source_sha256={test_readiness.DEFINITIONS:digest(Path(root)/test_readiness.DEFINITIONS),
            'engineering/reference_cell/qualification.py':digest(__file__)},
        scope='Candidate-bound planning requests; actual segmented-fin, material, brake, site and operating procedures need independent approval',**FLAGS)
    value['evaluation_id']=identity(value);return value
