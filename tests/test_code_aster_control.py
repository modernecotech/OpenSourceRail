"""Checks for the explicit one-box native handoff gate."""
import json
import pytest

from engineering.design_search.craft_backends import code_aster_control as control


def test_native_observables_require_equilibrium_and_work_balance():
    displacement=1000/(70e9*.06)
    native={'reactions':[{'DX':-1000.,'DY':0.,'DZ':0.}],
            'tip':[{'CMP':'DX','MOYENNE':displacement}],
            'energy':[{'ENTITE':'TOUT','TOTALE':500*displacement}]}
    checked=control.check_observables(native)
    assert checked['numerical_screen_passed']
    assert checked['force_relative_residual']==0
    assert checked['energy_relative_residual']==0
    native['reactions'][0]['DX']=-900.
    assert not control.check_observables(native)['numerical_screen_passed']
    native['reactions'][0]['DX']=-1000.
    native['energy'][0]['TOTALE']*=1.2
    assert not control.check_observables(native)['numerical_screen_passed']


def test_native_observables_refuse_missing_or_ambiguous_fields():
    with pytest.raises(ValueError,match='Exactly one'):
        control.check_observables({'reactions':[]})
    with pytest.raises(ValueError,match='Expected native'):
        control.check_observables({'reactions':[{'DX':-1000.,'DY':0.,'DZ':0.}],
                                   'tip':[{'CMP':'DY','MOYENNE':1e-7}],
                                   'energy':[{'ENTITE':'TOUT','TOTALE':1e-4}]})


def test_handoff_rejects_symlink_and_reused_output_before_native_execution(tmp_path):
    step=tmp_path/'box.step'
    step.write_text('STEP test placeholder')
    link=tmp_path/'link.step'
    link.symlink_to(step)
    with pytest.raises(ValueError,match='Regular exact STEP'):
        control.run_box(link,tmp_path/'output',candidate_id='box',image='example/aster:current')
    output=tmp_path/'output'
    output.mkdir()
    with pytest.raises(ValueError,match='Fresh private'):
        control.run_box(step,output,candidate_id='box',image='example/aster:current')


def test_fallback_refuses_a_different_step_or_candidate(tmp_path):
    step=tmp_path/'box.step'
    step.write_text('STEP test placeholder')
    receipt=tmp_path/'fieldcraft.json'
    receipt.write_text(json.dumps(dict(candidate_id='different',source_step_sha256='bad',
        source_format='STEP',handoff_status='held',step_extension_dispatch='rejected',
        direct_geometry_open='rejected',physical_accepted=False,
        component_geometry_id='component',fieldcraft_binary_sha256='hash')))
    with pytest.raises(ValueError,match='not bound'):
        control.run_box(step,tmp_path/'fresh',candidate_id='box',image='example/aster:current',
                        fieldcraft_rejection=receipt)
    assert not (tmp_path/'fresh').exists()
