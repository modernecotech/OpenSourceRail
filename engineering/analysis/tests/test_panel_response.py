"""Independent plate patches, native verification, equilibrium and fault envelopes."""
from pathlib import Path
from copy import deepcopy
import json,math,sys
import numpy as np
import pytest
ROOT=Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT),str(ROOT/'design/component-catalogue/src')]
from engineering.panel_response.plate import stiffness,solve,grid,single_clip_envelope
from engineering.panel_response.verification import strip
from engineering.panel_response.study import contracts,verify
from engineering.design_consistency.demonstrators import panel_bay
CONFIG=json.loads((ROOT/'engineering/composite_panels/config/development.json').read_text())


def test_constant_curvature_patch_and_three_rigid_modes():
    hx=.2;hy=.3;D=np.diag([100.,120.,30.]);S=np.ones(2)*1e6
    k,f=stiffness(hx,hy,lambda x,y:(D,S));points=np.array([[0,0],[hx,0],[hx,hy],[0,hy]])
    for dx,dy,c in [(0,0,1),(1,0,0),(0,1,0)]:
        u=np.array([[c+dx*x+dy*y,dx,dy]for x,y in points]).ravel();assert np.linalg.norm(k@u)<1e-8
    eigen=np.linalg.eigvalsh(k);assert np.count_nonzero(abs(eigen)<1e-7)==3
    u=np.array([[x*x/2,x,0]for x,y in points]).ravel();assert u@k@u==pytest.approx(D[0,0]*hx*hy,rel=1e-8)
    assert f[::3].sum()==pytest.approx(hx*hy)


def test_strip_convergence_and_thin_plate_locking_control():
    a=strip(count=20);b=strip(count=40)
    assert b['analytical_relative_error']<a['analytical_relative_error']and b['analytical_relative_error']<.002
    thin=strip(count=40,thickness=.002);assert thin['analytical_relative_error']<.002


def test_actual_trim_area_and_linear_force_displacement_balance():
    model=panel_bay(CONFIG);a=solve(model,mesh_size=.15);b=solve(model,mesh_size=.15,pressure_pa=4000)
    c=model['panel_parameters'];area=c['width_m']*c['height_m']-sum((d-x)*(e-y)for x,y,d,e in c['holes'])
    assert a['loaded_area_m2']==pytest.approx(area,abs=1e-10)
    assert a['force_balance_relative_error']<1e-6 and a['free_residual_relative_error']<1e-6
    assert b['maximum_deflection_m']==pytest.approx(2*a['maximum_deflection_m'],rel=1e-8)
    assert a['external_work_j']==pytest.approx(2*a['plate_strain_energy_j'],rel=1e-8)
    assert sum(r for rail in a['rails']for r in rail['bracket_reaction_n'])==pytest.approx(-a['applied_force_n'])


def test_rank_one_all_clip_losses_match_an_independent_direct_reassembly():
    model=panel_bay(CONFIG);envelope=single_clip_envelope(model,mesh_size=.15)
    assert envelope['case_count']==model['support_network']['panel_attachment_count']
    direct=solve(model,mesh_size=.15,failed_clip=envelope['worst']['failed_clip'])
    assert direct['maximum_deflection_m']==pytest.approx(envelope['worst']['maximum_deflection_m'],rel=1e-8)
    assert next(a for a in direct['attachments']if not a['active'])['force_n']==0
    assert not direct['production_released']and direct['unknown_checks']


@pytest.mark.parametrize('kind',['curve','placement','unknown_clip','pressure','potting_overlap'])
def test_inapplicable_geometry_and_invalid_loads_are_rejected(kind):
    model=panel_bay(CONFIG);kwargs={}
    if kind=='curve':model=panel_bay(CONFIG,crown=.05,aperture=False)
    elif kind=='placement':model['parts'][0]['placement']['translation_m']=[1,0,0]
    elif kind=='unknown_clip':kwargs['failed_clip']='invented-clip'
    elif kind=='potting_overlap':model=panel_bay(CONFIG,span=.35)
    else:kwargs['pressure_pa']=float('nan')
    with pytest.raises(ValueError):solve(model,mesh_size=.2,**kwargs)


def test_retained_native_geometry_and_all_response_cases_are_bound_and_unreleased():
    output=ROOT/'engineering/panel_response/examples';verify(output)
    summary=json.loads((output/'summary.json').read_text());assert summary['native_formulation_screen_passed']and summary['verified_designs']==[]
    for row in summary['cases']:
        loss=json.loads((output/(row['name']+'-clip-loss-envelope.json')).read_text())
        assert loss['case_count']==row['clip_count']and row['failed_clip']==loss['worst']['failed_clip']
        assert row['refinement_relative_difference']<.03 and not row['qualified']
    native=json.loads((output/'cad/verification.json').read_text());assert len(native['records'])==len(summary['cases'])
    assert all(r['native_reopened']and r['step_volume_reconciled']and not r['material_overlaps']for r in native['records'])
