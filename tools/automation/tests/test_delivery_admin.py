"""Native administrative probes must remain bounded, permission gated and read-only."""
import hashlib
from pathlib import Path
import sys
from types import SimpleNamespace
import pytest
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'deployment/erpnext/apps/osr_erpnext'))
from osr_erpnext import delivery_admin

@pytest.fixture
def native(monkeypatch):
    calls=[]
    def throw(message):raise PermissionError(message)
    f=SimpleNamespace(get_roles=lambda:['System Manager'],throw=throw,
        db=SimpleNamespace(sql=lambda query:[('a'*64,)],exists=lambda kind,name:True),
        has_permission=lambda name,permission:True,
        get_list=lambda kind,**kwargs:calls.append((kind,kwargs)) or [dict(name='SYNTHETIC-FIXTURE')])
    monkeypatch.setitem(sys.modules,'frappe',f)
    return f,calls

def test_snapshot_returns_counts_hashes_never_private_values(native):
    f,_=native;result=delivery_admin.recovery_fingerprint()
    assert len(result['records'])==6 and result['read_only'] and not result['operational_release']
    assert all(r==dict(count=1,sha256=hashlib.sha256(('a'*64+'\n').encode()).hexdigest()) for r in result['records'].values())
    assert 'description' in delivery_admin.snapshot_queries()['evidence_tasks']
    assert all('SELECT SHA2' in q and 'ORDER BY name' in q for q in delivery_admin.snapshot_queries().values())

def test_probe_uses_native_permissions_and_bounded_lists(native):
    f,calls=native;f.has_permission=lambda name,permission:name!='File'
    result=delivery_admin.read_probe(2)
    assert len(result['samples'])==2 and not result['proof_of_city_scale']
    assert all(kind!='File' and kw['limit_page_length']==50 for kind,kw in calls)

@pytest.mark.parametrize('value',[0,31,True,1.5,'5'])
def test_probe_repetition_bound(native,value):
    with pytest.raises(ValueError):delivery_admin.read_probe(value)

def test_manager_role_is_required_before_any_native_read(native):
    f,calls=native;f.get_roles=lambda:['Guest']
    with pytest.raises(PermissionError):delivery_admin.recovery_fingerprint()
    with pytest.raises(PermissionError):delivery_admin.read_probe()
    assert not calls
