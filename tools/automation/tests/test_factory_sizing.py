"""Physical factory demand, release gates and schedule/cash provenance checks."""
from copy import deepcopy
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tomllib
import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/automation'))
from factory_sizing import size_factory
from project_twin import apply_resource_cpm


def assumptions():
    return tomllib.loads((ROOT/'lib/templates/baghdad-factory.toml').read_text())


def tasks():
    rows=[dict(manufacturing_uid='baseline',asset_id='SYS',asset_type='system',package_id='baseline',
               line='',work_center='controls',duration_days=5,predecessor_uids='',sequence=0),
          *[dict(manufacturing_uid=line+'-civil',asset_id=line,asset_type='track-section',package_id='civil',
                 line=line,work_center=line+'-civil',duration_days=1683,predecessor_uids='',sequence=1)
            for line in ('line-1','line-2')]]
    for line in ('line-1','line-2'):
        for n in range(10):
            asset=f'{line}-RS-{n:02d}';previous='baseline'
            for s in assumptions()['stage']:
                uid=asset+':'+s['package']
                rows.append(dict(manufacturing_uid=uid,asset_id=asset,asset_type='rolling-stock',line=line,
                    package_id=s['package'],work_center='old pool',duration_days=1,predecessor_uids=previous,
                    product_family='metro-6car',sequence=10,evidence_required='ITP'))
                previous=uid
    return rows


def test_full_fleet_is_sized_to_infrastructure_without_identifier_changes():
    rows=tasks();ids={r['manufacturing_uid']:r['asset_id'] for r in rows}
    p=size_factory(rows,{},assumptions())
    assert p['factory_ready_working_day']==390
    assert p['total_trainsets']==20 and p['vehicle_modules']==120
    assert p['stock_finish_working_day']<=p['infrastructure_target_working_day']==1682
    assert {r['manufacturing_uid']:r['asset_id'] for r in rows}==ids
    apply_resource_cpm(rows,p['resource_capacity'],p['resource_ready_days'])
    actual=max(r['planned_finish_day'] for r in rows if r['asset_type']=='rolling-stock')
    assert actual==p['stock_finish_working_day']
    kits=[r for r in rows if r['package_id']=='rs-10-material-kit']
    first=next(r for r in kits if r['asset_id']=='line-1-RS-00')
    prototype=next(r for r in rows if r['asset_id']==first['asset_id'] and r['package_id']=='rs-50-dynamic-commissioning')
    assert first['planned_start_day']==390
    assert all(r['planned_start_day']>prototype['planned_finish_day'] for r in kits if r!=first)
    assert p['plant_cost_envelope_usd']==pytest.approx(sum(p['cost_allowances_usd'].values()))
    assert p['exclusive_test_path_capacity_trainsets_per_year']>=p['minimum_steady_output_trainsets_per_year']
    assert not p['engineering_release']


def test_factory_rejects_infeasible_dates_family_and_missing_flow():
    for change in ('date','family','stage','availability','phase'):
        rows=tasks();c=assumptions()
        if change=='date':
            for row in rows:
                if row['asset_type']=='track-section':row['duration_days']=500
        if change=='family':rows[-1]['product_family']='light-metro-3car'
        if change=='stage':c['stage'].pop()
        if change=='availability':c['factory']['productive_availability']=1.1
        if change=='phase':c['construction_phase'][0]['days']=59
        with pytest.raises(ValueError):size_factory(rows,{},c)


def test_parallel_acceptance_bays_cannot_invent_shared_test_track_capacity():
    c=assumptions();c['factory']['exclusive_track_hours_per_trainset']=10000
    with pytest.raises(ValueError,match='test-track path capacity'):
        size_factory(tasks(),{},c)


def test_dispatch_priority_preserves_physical_identity():
    rows=[dict(manufacturing_uid='a',asset_id='A',duration_days=4,sequence=1,work_center='crew',dispatch_priority=2),
          dict(manufacturing_uid='b',asset_id='B',duration_days=4,sequence=1,work_center='crew',dispatch_priority=1)]
    apply_resource_cpm(rows,{'crew':1})
    assert rows[1]['planned_start_day']==0 and rows[0]['planned_start_day']==4
    assert [r['asset_id'] for r in rows]==['A','B']


def test_published_baghdad_factory_reconciles_actual_fleet_space_budget_and_sources():
    directory=ROOT/'cities/catalogue/west-asia/Iraq/Baghdad/engineering/factory'
    p=json.loads((directory/'summary.json').read_text())
    deliveries=list(csv.DictReader((directory/'deliveries.csv').open()))
    assert len(deliveries)==len({r['trainset'] for r in deliveries})==p['total_trainsets']==sum(f['trainset_count'] for f in __import__('tomllib').loads((directory.parents[1]/'design.toml').read_text())['fleets'])
    assert sum(int(r['cars']) for r in deliveries)==p['total_trainsets']*6
    assert max(int(r['working_day']) for r in deliveries)==p['stock_finish_working_day']<=p['infrastructure_target_working_day']
    assert p['readiness_months_from_ntp']==18
    assert p['budgeted_plant_direct_usd']>=p['plant_cost_envelope_usd']
    assert p['incremental_plant_capex_with_epc_usd']>0
    assert p['planning_site_m2']>p['process_and_support_floor_m2']>0
    assert p['original_lines_civil_complete_before_factory_ready']==[line for line,day in p['original_infrastructure_deadlines'].items() if day<p['factory_ready_working_day']]
    assert p['lines_civil_complete_before_factory_ready']==[]
    for relative,digest in p['sources_sha256'].items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest
    funding=json.loads((directory.parents[2]/'finance/baghdad-programme.json').read_text())
    assert funding['factory']['planning_build_working_days']==390
    assert funding['factory']['cost_usd']==p['budgeted_plant_direct_usd']
    assert funding['factory']['epc_usd']==p['budgeted_plant_epc_usd']


def test_independent_test_paths_are_sized_and_fully_priced_for_shorter_civil_window():
    rows=tasks();c=assumptions();c['factory']['exclusive_track_hours_per_trainset']=400
    plan=size_factory(rows,{},c)
    assert plan['test_tracks']>c['factory']['test_tracks']
    assert plan['test_tracks']<=c['factory']['maximum_test_tracks']
    assert plan['exclusive_test_path_capacity_trainsets_per_year']>=plan['minimum_steady_output_trainsets_per_year']
    assert plan['cost_allowances_usd']['test_tracks']==pytest.approx(plan['test_tracks']*c['factory']['test_track_length_m']/1000*c['cost_envelope']['test_track_allowance_usd_km'])

def test_generic_opening_waits_for_the_physical_test_path_limit():
    rows=tasks();c=assumptions();c['factory']['maximum_test_tracks']=2;c['factory']['exclusive_track_hours_per_trainset']=100
    for row in rows:
        if row['asset_type']=='track-section':row['duration_days']=500
    p=size_factory(rows,{},c,allow_civil_delay=True)
    assert p['test_tracks']<=2
    assert p['factory_ready_working_day']==390
    assert p['test_path_limited_integrated_delay']
    assert p['original_infrastructure_target_working_day']==499
    assert p['stock_finish_working_day']<=p['integrated_target_working_day']
    assert p['integrated_target_working_day']>p['original_infrastructure_target_working_day']
    assert p['minimum_steady_output_trainsets_per_year']<=p['exclusive_test_path_capacity_trainsets_per_year']
