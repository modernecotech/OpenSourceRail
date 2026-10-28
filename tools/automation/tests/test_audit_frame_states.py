"""Small independent action/objectivity checks; no native factorization."""
from pathlib import Path
import importlib.util
import numpy as np
import pytest
SCRIPT=Path(__file__).resolve().parents[1]/'audit-frame-states.py'
spec=importlib.util.spec_from_file_location('audit_frame_states',SCRIPT);a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)


def test_element_action_energy_is_work_conjugate():
    K=np.array([[4.,-2.],[-2.,3.]]);u=np.array([.2,-.1]);f,E=a.element_action(K,u)
    assert np.allclose(f,[1.,-.7]) and E==pytest.approx(.135)


def test_contact_action_does_not_hide_offsets_or_energy():
    B=np.array([[1.,-1.,.4],[0.,1.,-.3],[.2,0.,1.]]);k=np.array([2.,3.,4.]);u=np.array([.1,.2,-.1])
    f,E=a.contact_action(B,k,u)
    assert np.allclose(f,B.T@np.diag(k)@B@u)
    assert E==pytest.approx(u@f/2) and E>=0


def test_global_rigid_modes_have_exact_translation_rotation():
    nodes=np.array([[0.,0.,0.],[2.,3.,4.]])
    modes=a.rigid_modes(nodes).reshape(2,6,6)
    assert np.allclose(modes[:,:3,:3],np.broadcast_to(np.eye(3),(2,3,3)))
    assert np.allclose(modes[1,:3,5],[-3.,2.,0.])
    assert np.allclose(modes[:,3:,3:],np.broadcast_to(np.eye(3),(2,3,3)))


def test_no_fresh_factorization_or_solver_call_in_audit_source():
    import ast
    tree=ast.parse(SCRIPT.read_text());forbidden={'solve','spsolve','splu','factorized','run'}
    for node in ast.walk(tree):
        if isinstance(node,ast.Call):
            assert not isinstance(node.func,ast.Name) or node.func.id not in forbidden
            assert not isinstance(node.func,ast.Attribute) or node.func.attr not in forbidden
