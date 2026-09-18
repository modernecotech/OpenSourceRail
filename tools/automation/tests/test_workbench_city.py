import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location('workbench_city', ROOT / 'tools/automation/workbench_city.py')
CITY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CITY)


def write(root, name, data):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


def test_city_routes_require_matching_project_company_and_feedback(tmp_path):
    design = tmp_path / 'city/design.toml'
    write(tmp_path, 'city/operations/supervision.json', {'erp_project':'P1','company':'Operator'})
    write(tmp_path, 'var/erpnext/operating-twins.json', {'snapshots':[
        {'city':'other','project':'P1','company':'Operator'},
        {'city':'test','project':'P1','company':'Wrong'},
    ]})
    result = CITY.city_summary(tmp_path, 'test', design, 'other')
    assert result['erp']['state'] == 'unavailable'
    assert 'tasks' not in result['erp']['routes']
    assert not result['control_available']
    assert result['supervision']['state'] == 'unavailable'
    row = {'city':'test','project':'P1','company':'Operator','observed_at':'2020-01-01T00:00:00Z'}
    write(tmp_path, 'var/erpnext/operating-twins.json', {'snapshots':[row]})
    result = CITY.city_summary(tmp_path, 'test', design, 'test')
    assert result['erp']['routes']['tasks'] == '/app/task?project=P1'
    assert result['erp']['stale'] is True
    assert result['control_available']
    write(tmp_path, 'var/erpnext/operating-twins.json', {'snapshots':[row,row]})
    assert CITY.city_summary(tmp_path, 'test', design, 'test')['erp']['state'] == 'ambiguous'


def test_prepared_package_never_implies_live_or_physical_deployment(tmp_path):
    write(tmp_path, 'build/supervision/test/simulation/package.json',
          {'city':'test','environment':'simulation','equipment':[{'site_id':'ST-1'}]})
    design = tmp_path / 'city/design.toml'
    result = CITY.city_summary(tmp_path, 'test', design, 'test')
    assert result['supervision'] == {'state':'prepared','sites':['ST-1'],'preferred_site':'ST-1','equipment_count':1}
    assert CITY.city_summary(tmp_path, 'test', design, 'test', 'physical')['supervision']['sites'] == []


def test_factory_sorting_does_not_change_preferred_vehicle_and_profile_is_checked(tmp_path):
    design = tmp_path / 'city/design.toml'
    write(tmp_path, 'build/supervision/test/simulation/package.json',
          {'city':'test','environment':'simulation','equipment':[
              {'site_id':'T-PLANT-001','equipment_type':'factory-lm3-mfg-020'},
              {'site_id':'T-RS-001','equipment_type':'vehicle-bms'}]})
    summary = lambda: CITY.city_summary(tmp_path, 'test', design, 'test')['supervision']
    assert summary()['sites'][0] == 'T-PLANT-001'
    assert summary()['preferred_site'] == 'T-RS-001'
    write(tmp_path, 'city/operations/supervision.json', {'preferred_supervision_site':'T-PLANT-001'})
    assert summary()['preferred_site'] == 'T-PLANT-001'
    write(tmp_path, 'city/operations/supervision.json', {'preferred_supervision_site':'OTHER-CITY-RS-001'})
    assert summary()['preferred_site'] is None


def test_isolated_city_configuration_cannot_pick_up_primary_records(tmp_path):
    design=tmp_path/'city/design.toml'
    write(tmp_path,'city/operations/supervision.json',{'erp_project':'PRIMARY'})
    write(tmp_path,'var/erpnext/operating-twins.json',{'snapshots':[{'city':'test','project':'PRIMARY'}]})
    write(tmp_path,'example/profiles/test.json',{'erp_project':'EXAMPLE','company':'Example'})
    write(tmp_path,'example/twins.json',{'snapshots':[{'city':'test','project':'EXAMPLE','company':'Example'}]})
    write(tmp_path,'example/supervision/test/simulation/package.json',{'city':'test','environment':'simulation','equipment':[{'site_id':'EXAMPLE-ST'}]})
    result=CITY.city_summary(tmp_path,'test',design,'test',feedback_path=tmp_path/'example/twins.json',
        supervision_root=tmp_path/'example/supervision',profiles_root=tmp_path/'example/profiles')
    assert result['erp']['project']=='EXAMPLE'
    assert result['supervision']['sites']==['EXAMPLE-ST']
