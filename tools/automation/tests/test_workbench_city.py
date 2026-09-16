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
    assert result['supervision'] == {'state':'prepared','sites':['ST-1'],'equipment_count':1}
    assert CITY.city_summary(tmp_path, 'test', design, 'test', 'physical')['supervision']['sites'] == []
