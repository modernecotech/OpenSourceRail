"""Small parser/integrity tests; these synthetic values are not FEM evidence."""
from copy import deepcopy
import json
import numpy as np
import pytest
from tools.engineering_gallery.fem import (check_seal, exterior_triangles,
    original_tail, sealed, validate_field)


def field():
    xyz=[[0.,0.,0.],[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],
         [.5,0.,0.],[.5,.5,0.],[0.,.5,0.],[0.,0.,.5],[.5,0.,.5],[0.,.5,.5]]
    mesh=dict(nodes={str(i+1):v for i,v in enumerate(xyz)},elements={"20":list(range(1,11))})
    f=dict(points=np.array(xyz),node_label=np.arange(1,11),element_label=np.array([20]),
        displacement=np.zeros((10,3)),has_result=np.ones(10),von_mises=np.ones(10),
        connectivity=np.arange(10),offsets=np.array([10]),types=np.array([24]))
    return f,mesh


def test_full_native_field_and_quadratic_surface():
    f,m=field();v=validate_field(f,m)
    assert v["all_nodes_have_result"] and v["nodes"]==10 and v["cells"]==1
    assert len(exterior_triangles(m))==16


@pytest.mark.parametrize("fault",["missing-result","nan","node","xyz","cell","connectivity","probe"])
def test_no_silent_unknown_or_changed_field(fault):
    f,m=field();probe=None
    if fault=="missing-result":f["has_result"][0]=0
    elif fault=="nan":f["displacement"][0,0]=float("nan")
    elif fault=="node":f["node_label"][0]=99
    elif fault=="xyz":f["points"][0,0]=.01
    elif fault=="cell":f["element_label"][0]=21
    elif fault=="connectivity":f["connectivity"][0]=1
    else:probe=([0.,0.,0.],[0.,0.,1.])
    with pytest.raises(ValueError):validate_field(f,m,expected_probe=probe)


def test_tail_and_seal_cannot_hide_changed_physics(tmp_path):
    commands=[dict(command=n,params={"step":"Research"} if n=="solve.static" else {}) for n in
        ["file.open","model.load.create","model.step.create","model.check","solve.static","solve.probe","results.reactions","model.info"]]
    p=tmp_path/"stdin.jsonl"
    p.write_text(json.dumps(dict(method="tools/call",params=dict(arguments=dict(commands=commands))))+"\n")
    assert original_tail(p)==commands
    commands[4]["params"]["step"]="Other"
    p.write_text(json.dumps(dict(method="tools/call",params=dict(arguments=dict(commands=commands))))+"\n")
    with pytest.raises(ValueError):original_tail(p)
    v=sealed(dict(a=1));check_seal(v);v["a"]=2
    with pytest.raises(ValueError):check_seal(v)
