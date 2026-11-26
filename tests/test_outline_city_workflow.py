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
    network=value['network_planning']
    assert network['status']=='bounded-retained-corridor-fallback'
    assert network['applicability']['river_name']=='الفرات'
    assert network['applicability']['ring_status']=='no-linked-ring'
    assert network['retained_station_access']
    assert network['metropolitan_search']['assembly']=='from-empty-retained-corridor-library'
    assert network['metropolitan_search']['applicable_river']=='الفرات'
    assert network['metropolitan_search']['metropolitan_coverage_status'].endswith('evidence-required')
    assert workflow.read_json(folder,'summary.json')['network_planning']==network
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
        if p.is_file() and p.relative_to(folder).as_posix()!='manifest.json')
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


def test_baghdad_service_comparison_replays_and_reprices_same_published_network(tmp_path):
    original_folder=tmp_path/'baghdad-original'/'artifacts'
    original_request=dict(city_slug='baghdad')
    workflow.run(original_request,original_folder)
    original_manifest=workflow.verify(original_folder,replay=True)
    original=workflow.read_json(original_folder,'result.json')
    original_plan=original['planning_base']
    line=original_plan['lines'][0]
    alternative_edits=bundle(original_plan,[dict(kind='set-service',line=line['id'],
        headway_s=300.,dwell_s=35.)])
    alternative_edits['seed_id']=original_plan['outline_context']['seed']['seed_id']
    alternative_request=dict(city_slug='baghdad',
        base_seed_id=original_plan['outline_context']['seed']['seed_id'],
        edit_bundle=alternative_edits)
    alternative_folder=tmp_path/'baghdad-alternative'/'artifacts'
    workflow.run(alternative_request,alternative_folder)
    alternative_manifest=workflow.verify(alternative_folder,replay=True)
    alternative=workflow.read_json(alternative_folder,'result.json')

    assert original_manifest['source_sha256']==alternative_manifest['source_sha256']
    assert original['source_outline_evaluation_id']==alternative['source_outline_evaluation_id']
    assert original['city']['slug']==alternative['city']['slug']=='baghdad'
    assert original['network_planning']['applicability']['ring_ids']==['line-9']
    assert original['network_planning']['status']=='bounded-retained-corridor-fallback'
    assert alternative['network_planning']['status']=='explicit-scenario'
    assert original['evaluation_id']!=alternative['evaluation_id']
    assert len(original['city_outline']['cost']['scope_totals_usd'])==14
    assert len(alternative['city_outline']['cost']['scope_totals_usd'])==14
    assert original['city_outline']['cost']['whole_life_npv_usd']!=alternative['city_outline']['cost']['whole_life_npv_usd']
    assert alternative['outline_acceptance'] in ('accepted','requires-revision')
    assert all(alternative.get(flag) is False for flag in workflow.FLAGS)
    assert not alternative['business_drafts']['external_transactions_performed']


def test_baghdad_cli_defaults_to_the_dedicated_project(tmp_path, monkeypatch, capsys):
    from engineering.outline import __main__ as cli

    folder = tmp_path / 'baghdad-metropolitan'
    calls = []
    def dedicated(output, root, *, verify):
        calls.append((output, verify))
        if not verify:
            output.mkdir()
            (output / 'metropolitan-network.json').write_text('{}')
        return {'schema': 'osr-baghdad-metropolitan/1'}
    monkeypatch.setattr(cli, '_baghdad_study', dedicated)
    monkeypatch.setattr(cli, '_disk_reserve_hold', lambda *_: False)
    cli.main(['city', '--city', 'baghdad', '--output', str(folder)])
    cli.main(['city-verify', '--output', str(folder)])
    assert calls == [(folder, False), (folder, True)]
    assert all(json.loads(line)['schema']=='osr-baghdad-metropolitan/1'
               for line in capsys.readouterr().out.splitlines())
    with pytest.raises(ValueError, match='explicitly request the original catalogue alignment'):
        workflow.active_baghdad_response({'city_slug': 'baghdad',
                                         'service': {'peak_demand_pphpd': 2500}})


def test_new_city_civil_default_prices_viaducts_and_retains_mapped_comparison():
    from engineering.outline import city_civil
    from engineering.station_rail.common import identity

    req = workflow.normalize({'city_slug': 'samawah'})
    assert req['civil_policy'] == 'elevated'
    explicit = workflow.normalize({'city_slug': 'samawah', 'civil_policy': 'mapped-mixed-comparison'})
    with pytest.raises(ValueError, match='civil policy'):
        workflow.normalize({'city_slug': 'samawah', 'civil_policy': 'unspecified'})
    mapped = {'lines': [{'line_id': 'A', 'route_m': 400., 'shape': 'radial'}],
              'civil_segments': [{'line_id': 'A', 'class': cls, 'from_m': i * 100., 'to_m': (i+1) * 100.}
                                 for i, cls in enumerate(('elevated', 'at-grade', 'bridge', 'tunnel'))]}
    mapped['input_id'] = identity(mapped)
    first = workflow._civil_input(mapped, req['civil_policy'])
    comparison = workflow._civil_input(first, explicit['civil_policy'])
    assert first['ancestry']['parent_input_id'] == mapped['input_id']
    assert len({first['input_id'], comparison['input_id']}) == 2
    assert first['input_id'] == identity({k: v for k, v in first.items() if k != 'input_id'})
    assert city_civil.quantities(first)['class_route_m'] == {'at-grade': 0., 'tunnel': 0., 'elevated': 300., 'bridge': 100.}
    assert city_civil.quantities(comparison) == city_civil.quantities(workflow._civil_input(comparison, explicit['civil_policy']))
    assert city_civil.quantities(comparison)['class_route_m'] == city_civil.quantities(mapped)['class_route_m']
    assert mapped['civil_segments'][1]['class'] == 'at-grade'


def test_legacy_study_summary_preserves_original_architecture_scope(study):
    _, _, current = study
    old = deepcopy(current)
    del old['city_outline']['policy']['civil_policy']
    del old['city_outline']['policy']['supply_preference']
    legacy = workflow.summary(old)
    assert not {'civil_policy', 'supply_preference', 'civil_route_m'} & set(legacy)
    now = workflow.summary(current)
    assert now['civil_policy'] == 'elevated' and now['supply_preference'] == 'catenary-free'
    assert now['civil_route_m']['tunnel'] == now['civil_route_m']['at-grade'] == 0
