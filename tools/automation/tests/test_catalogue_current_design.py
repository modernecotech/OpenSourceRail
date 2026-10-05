"""Catalogue changes preserve inventories, physical lead times and cost identities."""
from copy import deepcopy
import importlib.util
import math
from pathlib import Path
import sys
import tomllib

import pytest

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'tools/automation'),str(ROOT/'design/city-generation/src')]

def load(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'tools/automation'/file)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

alignment=load('catalogue_alignment','rework-city-alignment.py')
depots=load('line_depots','apply-city-depot-scope.py')
from factory_sizing import configure_factory, size_factory
from osr_scenario.network_readme import _workforce_payroll_usd, _driverless_workforce_breakdown
from types import SimpleNamespace


def test_seed_preserves_controlled_ring_missing_from_route_cache():
    d={'city':{'slug':'test','population':1},'lines':[{'name':'radial','shape':'radial'},{'name':'ring','shape':'ring'}]}
    geo={'features':[{'properties':{'name':name},'geometry':{'type':'LineString','coordinates':coords}} for name,coords in
        [('radial',[[1,9],[2,8]]),('ring',[[1,9],[2,9],[2,8],[1,9]])]]}
    grid=dict(height=10,width=10,cell_m=1,bbox_north=10,bbox_west=0,m_per_deg_lat=1,m_per_deg_lon=1)
    seed=alignment.seed_from_geometry(d,geo,grid,{'lines':[{'name':'radial','anchor_ids':[1]}]})
    assert [r['name'] for r in seed['lines']]==['radial','ring']
    assert seed['lines'][1]['cells'][0]==seed['lines'][1]['cells'][-1]
    assert seed['lines'][1]['anchor_ids']==[]


def test_last_cell_centre_roundtrip_does_not_step_outside_grid():
    grid=dict(height=3,width=3,cell_m=20,bbox_north=10,bbox_west=0,m_per_deg_lat=20,m_per_deg_lon=20)
    d={'city':{'slug':'test','population':1},'lines':[{'name':'L','shape':'radial'}]}
    geo={'features':[{'properties':{'name':'L'},'geometry':{'type':'LineString','coordinates':[[.5,9.5],[2.5+1e-12,7.5-1e-12]]}}]}
    r=alignment.seed_from_geometry(d,geo,grid,{'lines':[]})
    assert r['lines'][0]['cells']==[[0,0],[2,2]]
    assert r['coordinate_basis']=='cell-centre-index-v1'


def test_closed_ring_has_real_curves_and_exact_closure():
    c=tomllib.loads(alignment.CONFIG.read_text())
    pts=[(0,0),(0,5000),(5000,5000),(5000,0),(0,0)]
    sampled,controls,_,_=alignment.smooth_run(pts,False,c)
    assert alignment.geometry.distance(sampled[0],sampled[-1])<1e-5
    assert any(r['kind']!='tangent' for r in controls)
    assert all(r.get('radius_m',math.inf)>=300 for r in controls)
    assert sum(r['length_m'] for r in controls)<20000


def test_unacceptable_curve_retains_original_geometry_and_open_gate():
    c=tomllib.loads(alignment.CONFIG.read_text());c['core']=dict(south=-1,north=10,west=-1,east=10)
    seed=dict(grid_cell_m=20,grid_height=10,grid_width=10,lines=[dict(name='ring',shape='Ring',cells=[[1,1],[1,2],[2,2],[2,1],[1,1]])])
    grid=dict(bbox_north=10,bbox_west=0,m_per_deg_lat=20,m_per_deg_lon=20)
    routes,r=alignment.rework(seed,grid,c)
    assert routes==seed
    run=r['lines'][0]['core_runs'][0]
    assert run['geometry_basis']=='retained-raster-requires-geometry-review'
    assert not run['controls']
    assert run['analytical_length_m']==run['original_length_m']


@pytest.mark.parametrize('family',['tram-2car','light-metro-3car','metro-4car','metro-6car'])
def test_line_depots_cover_whole_fleet_and_price_energy_once(family):
    profile=tomllib.loads((ROOT/'lib/templates/rolling-stock.toml').read_text())['profiles'][family]
    d=dict(fleets=[dict(line='a',trainset_count=7),dict(line='b',trainset_count=101)],
        stations=[dict(id='A',line='a',s_m=0),dict(id='B',line='b',s_m=0)],depots=[])
    config=tomllib.loads(depots.CONFIG.read_text());capex=tomllib.loads((ROOT/'lib/templates/capex-costs.toml').read_text())
    energy=tomllib.loads((ROOT/'lib/templates/energy-sites.toml').read_text())['tiers']['depot-main']
    r=depots.depot_plan(d,profile,config,capex,energy)
    assert r['number_of_depots']==2 and r['full_fleet_storage_slots']==108
    for site,count in zip(r['sites'],[7,101]):
        assert site['storage_slots']==count
        assert site['storage_tracks']*config['depots']['positions_per_track']>=count
        assert site['storage_track_m']==count*(profile['length_m']+10)
        assert site['workshop_bays']*260*16*.7>=count*400
        assert not site['site_accepted'] and not site['physical_release']
    assert sum(i['scope']=='depot-pv' for i in r['items'])==2
    assert sum(i['scope']=='depot-stationary-storage' for i in r['items'])==2
    assert r['gross_reference_cost_usd']==sum(round(sum(i['cost_usd'] for i in r['items'] if i['line']==line)) for line in ['a','b'])


def test_station_cover_uses_all_service_hours_and_pay_grades():
    d={'stations':[{},{}]}
    stats=SimpleNamespace(revenue_fleet=8,line_count=2,route_km=10,unique_station_count=2,depot_count=2)
    w=_driverless_workforce_breakdown(design=d,stats=stats,service_hours_per_day=20.5,total_trainsets=10,annual_train_km=100000,daily_paid_trips_high=1000)
    assert w['station_platform']==math.ceil(2*2*20.5*365/1520)
    c=tomllib.loads(depots.CONFIG.read_text())
    expected=math.fsum(n*1000*12*c['wage_multipliers'][role]*1.35 for role,n in w.items())
    assert _workforce_payroll_usd(w,1000)==pytest.approx(expected)
    assert min(c['wage_multipliers'].values())>=1.5
    assert c['wage_multipliers']['admin_training']>c['wage_multipliers']['station_platform']


def test_detailed_depot_prices_use_city_quantities_instead_of_legacy_flat_allowances():
    from osr_scenario.network_readme import compute_stats, _rich_capex_section, _fmt_usd
    city=ROOT/'cities/catalogue/west-africa/Nigeria/Aba-Ng'
    design=tomllib.loads((city/'design.toml').read_text())
    scenario=tomllib.loads((city/'aba-ng.toml').read_text())
    stats=compute_stats(design,scenario,design['city']['population'])
    energy=SimpleNamespace(solar_plant_kw=0.0,solar_plant_capex_usd=0.0)
    text='\n'.join(_rich_capex_section(design,design['costs'],stats,energy))
    section=text.split('### Depots')[1].split('### Rolling stock')[0]
    assert 'Storage slots' in section and 'Workshop bays' in section
    for site in design['depots']:
        assert f"| {site['line']} | {site['storage_slots']} | {site['train_length_m']:g} | {site['workshop_bays']} | {_fmt_usd(site['reference_cost_usd'])} |" in section
    assert _fmt_usd(sum(site['reference_cost_usd'] for site in design['depots'])) in section
    assert 'Healthy trainsets stable' not in section


@pytest.mark.parametrize('family',['tram-2car','light-metro-3car','metro-4car','metro-6car'])
def test_factory_uses_family_modules_and_explicit_small_city_delay(family):
    base=tomllib.loads((ROOT/'lib/templates/city-factory.toml').read_text())
    profile=tomllib.loads((ROOT/'lib/templates/rolling-stock.toml').read_text())['profiles'][family]
    config=configure_factory(base,'Test',family,profile)
    assert config['factory']['trainset_bay_length_m']==profile['length_m']+24
    assert base['factory']['family']=='metro-6car'  # independent city configurations
    tasks=[dict(manufacturing_uid='civil',asset_id='line',asset_type='track-section',line='line',package_id='civil',work_center='civil',duration_days=100,predecessor_uids='',sequence=1)]
    for n in range(3):
        previous='civil';asset='RS-'+str(n)
        for stage in config['stage']:
            uid=asset+stage['package']
            tasks.append(dict(manufacturing_uid=uid,asset_id=asset,asset_type='rolling-stock',line='line',package_id=stage['package'],work_center='old',duration_days=1,predecessor_uids=previous,product_family=family,sequence=10,evidence_required='ITP'))
            previous=uid
    with pytest.raises(ValueError,match='cannot precede'):size_factory(deepcopy(tasks),{},config)
    p=size_factory(tasks,{},config,allow_civil_delay=True)
    assert p['total_trainsets']==3 and p['vehicle_modules']==3*profile['cars']
    assert p['factory_ready_working_day']==390 and p['readiness_months_from_ntp']==18
    assert p['stock_finish_working_day']>100
    assert not p['engineering_release']
