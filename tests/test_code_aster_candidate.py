"""Candidate handoff contracts, independent numerical checks and integrity."""
import json
from pathlib import Path
import pytest

from engineering.design_search.craft_backends import code_aster_candidate as candidate


def definition():
    return dict(candidate_id='a'*64,component_geometry_id='b'*64,
        geometry=dict(product_name='sample',volume_m3=.12,
            bounds_m=dict(min=[.2,-.1,.05],max=[1.4,.3,.3])),
        material=dict(E_Pa=70e9,nu=.33,density_kg_m3=2700),
        boundary=dict(load_axis='x',fixed_side=0,loaded_side=1,force_N=[1500.,0.,0.]),
        mesh_size_m=.13)


def observables(force=1500., displacement=2e-7):
    return dict(reactions=[dict(DX=-force,DY=0.,DZ=0.)],
        tip={component:[dict(CMP=component,MOYENNE=value)] for component,value in
             [('DX',displacement),('DY',0.),('DZ',0.)]},
        energy=[dict(ENTITE='TOUT',TOTALE=.5*force*displacement)])


def test_candidate_requires_explicit_component_material_support_and_load():
    good=definition()
    assert candidate.validate_definition(good)==good
    broken=definition();broken['boundary']['fixed_side']=True
    with pytest.raises(ValueError,match='Opposite end faces'):
        candidate.validate_definition(broken)
    broken=definition();broken['material']['E_Pa']=None
    with pytest.raises(ValueError,match='Finite positive'):
        candidate.validate_definition(broken)
    broken=definition();broken['boundary']['force_N']=[0.,0.,0.]
    with pytest.raises(ValueError,match='Nonzero'):
        candidate.validate_definition(broken)


def test_code_aster_deck_uses_meshed_loaded_area_and_declared_material():
    request=dict(definition(),force_N=[1500.,0.,0.])
    deck=candidate.render_comm(request,dict(face_groups={'LOADED':dict(area_m2=.1)}))
    assert 'FX=15000.0' in deck
    assert 'E=70000000000.0' in deck
    assert "GROUP_MA='FIXED'" in deck and "GROUP_MA='LOADED'" in deck
    assert 'result = MECA_STATIQUE' in deck


def test_candidate_numerical_check_recomputes_all_force_and_work_components():
    checked=candidate.check_observables(observables(),[1500.,0.,0.])
    assert checked['numerical_screen_passed']
    assert checked['force_relative_residual']==0
    assert checked['energy_work_relative_residual']==0
    failed=observables();failed['reactions'][0]['DY']=150.
    assert not candidate.check_observables(failed,[1500.,0.,0.])['numerical_screen_passed']
    failed=observables();failed['energy'][0]['TOTALE']*=1.2
    assert not candidate.check_observables(failed,[1500.,0.,0.])['numerical_screen_passed']
    failed=observables();failed['tip']['DX'][0]['CMP']='DY'
    with pytest.raises(ValueError,match='component differs'):
        candidate.check_observables(failed,[1500.,0.,0.])


def test_refusal_must_bind_same_candidate_and_exact_step(tmp_path):
    step=tmp_path/'sample.step';step.write_bytes(b'exact step')
    receipt=dict(candidate_id='a'*64,component_geometry_id='b'*64,
        source_step_sha256=candidate.box.digest(step),source_format='STEP',
        handoff_status='held',step_extension_dispatch='rejected',
        direct_geometry_open='rejected',fieldcraft_binary_sha256='c'*64,
        physical_accepted=False)
    path=tmp_path/'refusal.json';path.write_text(json.dumps(receipt))
    assert candidate.validate_refusal(path,step,'a'*64,'b'*64)==receipt
    with pytest.raises(ValueError,match='differs'):
        candidate.validate_refusal(path,step,'d'*64,'b'*64)
    with pytest.raises(ValueError,match='differs'):
        candidate.validate_refusal(path,step,'a'*64,'d'*64)
    step.write_bytes(b'changed step')
    with pytest.raises(ValueError,match='differs'):
        candidate.validate_refusal(path,step,'a'*64,'b'*64)
