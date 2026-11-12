import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('engineering.design_search.craft_backends.linear_load_reuse',Path(__file__).parents[1]/'engineering/design_search/craft_backends/linear_load_reuse.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def test_execution_requires_explicit_admission_before_any_native(monkeypatch,tmp_path):
    called=[];monkeypatch.setattr(m.native,'mcp',lambda *a,**k:called.append(1))
    with pytest.raises(ValueError,match='Explicit coordinator'):m.run({},tmp_path/'run',root=tmp_path)
    assert called==[]


def test_changed_plan_refused_before_any_native(monkeypatch,tmp_path):
    called=[];monkeypatch.setattr(m.native,'mcp',lambda *a,**k:called.append(1))
    with pytest.raises(ValueError,match='Sealed'):m.run({'plan_id':'x'},tmp_path/'run',root=tmp_path,coordinator_admitted=True)
    assert called==[]


def test_field_resources_are_explicit(monkeypatch,tmp_path):
    observed=[]
    monkeypatch.setattr(m.fem,'deck',lambda *a:'MESH*BOUNDARYREST')
    monkeypatch.setattr(m.fem,'commands',lambda *a:[{'command':'solve.static'}])
    def mcp(*args,**kw):observed.append(kw);return {'execution':'failed'},[]
    monkeypatch.setattr(m.native,'mcp',mcp)
    with pytest.raises(ValueError,match='did not complete'):m._field({}, {},tmp_path/'fine',3072)
    assert observed[0]['memory_mb']==3072 and observed[0]['timeout_s']==120
