"""Actual mapped city -> cost -> editable revision -> delivery -> held drafts."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
from uuid import uuid4

import pytest

from engineering.station_rail import ROOT
from engineering.station_rail.common import encoded
from engineering.outline import city_workflow as workflow, publication_cache


@pytest.fixture(scope='module')
def study():
    job=uuid4().hex;folder=Path(ROOT)/'build/city-studies'/job/'artifacts'
    folder.parent.mkdir(parents=True)
    try:
        workflow.run(dict(city_slug='samawah',service=dict(operating_hours_per_day=24,
            operating_days_per_year=330),project=dict(pricing_scenario='china-bulk-buy')),folder)
        yield job,folder,workflow.read_json(folder,'result.json')
    finally:shutil.rmtree(folder.parent)


def bundle(base,edits):
    return dict(schema='osr-priced-planning-edits/1',city=base['city'],
        base_revision_sha256=base['revision_sha256'],seed_id=base['official_seed_id'],
        source_outline_evaluation_id=base['source_outline_evaluation_id'],actor='Regression planner',edits=edits)


def test_complete_study_has_exact_child_bindings_and_source_verified_exports(study):
    _,folder,value=study;m=workflow.verify(folder)
    assert m['evaluation_id']==value['evaluation_id'] and value['outline_acceptance']=='accepted'
    city=value['city_outline'];plan=value['delivery_plan'];base=value['planning_revision']
    assert base['source_cost_evaluation_id']==city['cost']['evaluation_id']
    assert base['outline_context']['city_input_template']==city['geometry_and_service']
    assert plan['city_record_evaluation_id']==city['evaluation_id']
    assert value['business_drafts']['source_plan_id']==plan['plan_id']
    assert len(city['cost']['scope_totals_usd'])==14
    timing=json.loads((folder/'performance.json').read_bytes())
    assert timing['elapsed_s']>0 and timing['cpu_s']>=0
    assert timing['native_solver_jobs']==0 and timing['external_transactions']==0
    assert timing['artifact_payload_bytes']==sum(p.stat().st_size for p in folder.rglob('*')
        if p.is_file() and p.name!='manifest.json')
    assert 'performance.json' in m['files_sha256']
    if timing['peak_rss_bytes'] is not None:assert timing['peak_rss_bytes']>0
    assert all(x is False for k,x in value.items() if k in workflow.FLAGS)
    operations=plan['workforce']['shift_patterns'][-1]
    assert operations['shifts_per_day']==3 and operations['days_per_year']==330
    for c,case in plan['schedule']['cases'].items():
        assert case['capacity_pass']
        assert case['target_met']==(case['finish_workday']<=case['target_workdays'])


def test_iterative_empty_edit_reprices_exactly_and_keeps_parent_study_policy(study):
    job,_,old=study;base=old['planning_revision']
    new,_=workflow.evaluate(dict(city_slug='samawah',base_study_id=job,edit_bundle=bundle(base,[])))
    assert new['city_outline']['cost']['installed_capital_usd']==old['city_outline']['cost']['installed_capital_usd']
    assert new['city_outline']['cost']['whole_life_npv_usd']==old['city_outline']['cost']['whole_life_npv_usd']
    assert new['city_outline']['policy']['operating_days_per_year']==330
    assert new['city_outline']['policy']['project']['pricing_scenario']=='china-bulk-buy'
    assert new['planning_revision']['outline_context']['study_rules']==new['city_outline']['policy']


def test_insufficient_requested_frequency_is_priced_without_automatic_replacement(study):
    job,_,old=study;base=old['planning_revision'];line=base['lines'][0]
    edits=[dict(kind='set-service',line=line['id'],headway_s=300.,dwell_s=35.)]
    value,_=workflow.evaluate(dict(city_slug='samawah',base_study_id=job,edit_bundle=bundle(base,edits)))
    assert value['calculation_complete'] and value['outline_acceptance']=='requires-revision'
    assert value['recommended_alignment_id'] is None
    duty=next(r for r in value['city_outline']['service_evaluation']['line_services'] if r['line_id']==line['id'])
    assert duty['requirements']['headway_s']==300
    assert duty['service']['planning_usable_capacity_pphpd']<duty['requirements']['peak_demand_pphpd']
    assert len(value['city_outline']['cost']['scope_totals_usd'])==14
    assert value['delivery_plan']['cost_reconciliation']['source_capital_usd']==value['city_outline']['cost']['installed_capital_usd']


def test_untracked_resealed_base_and_stale_display_id_cannot_start_a_study(study):
    _,_,value=study;base=deepcopy(value['planning_revision'])
    with pytest.raises(ValueError,match='server-verified'):
        workflow.evaluate(dict(city_slug='samawah',base_plan=base,edit_bundle=bundle(base,[])))
    with pytest.raises(ValueError,match='selected published outline changed'):
        workflow.evaluate(dict(city_slug='samawah',expected_outline_evaluation_id='0'*64))


def test_output_tamper_is_detected_before_reuse(study):
    _,folder,_=study;path=folder/'summary.json';raw=path.read_bytes()
    try:
        path.write_bytes(raw+b' ')
        with pytest.raises(ValueError,match='artifact differs'):workflow.verify(folder)
    finally:path.write_bytes(raw)
