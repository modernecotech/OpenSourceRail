"""Independent limits, real CalculiX output and resealed-input rejection."""
from copy import deepcopy
import json
from pathlib import Path
import os
import shutil

import pytest

from engineering.equipped_vehicle.structures import analytical,deck,parse_dat,run_structural_fixture,verify_structural_fixture,_inventory
from engineering.equipped_vehicle import ROOT

EVIDENCE=Path(os.environ.get('OSR_EVIDENCE_ROOT',str(ROOT)))


def test_analytical_limit_matches_independent_retained_laminate_fixture():
    reference=json.loads((EVIDENCE/'engineering/trip_dynamics/fixtures/structures/analytical-laminate.json').read_bytes())
    a=analytical()
    assert a['D11_N_m']==pytest.approx(reference['D_N_m'][0][0])
    assert a['EI_N_m2']==pytest.approx(reference['EI_N_m2'])
    assert a['tip_deflection_m']==pytest.approx(reference['tip_deflection_analytical_m'])
    assert a['first_frequency_hz']==pytest.approx(reference['first_frequency_analytical_hz'],rel=1e-5)
    assert a['mass_kg']==reference['material_mass_kg']


def test_each_composite_ply_has_explicit_orientation_and_summed_force_is_fixed():
    text,mesh=deck(8)
    assert text.count('.001,,PLY,O0')==2 and text.count('.001,,PLY,O90')==2
    loads=text.split('*CLOAD\n',1)[1].split('*NODE PRINT',1)[0].splitlines()
    assert sum(float(line.split(',')[2]) for line in loads)==pytest.approx(-.1)
    assert mesh['element_count']==16 and len(mesh['tip_nodes'])==5
    for bad in (True,0,12,32):
        with pytest.raises(ValueError):deck(bad)


def test_unavailable_native_tool_stays_unknown(tmp_path):
    result=run_structural_fixture(tmp_path/'absent',ccx=tmp_path/'missing-ccx',root=EVIDENCE)
    assert result['method_screen']=='unknown' and result['execution_status']=='not-run' and result['rows']==[]
    assert verify_structural_fixture(tmp_path/'absent',root=EVIDENCE)['method_screen']=='unknown'


@pytest.fixture(scope='module')
def native(tmp_path_factory):
    if shutil.which('ccx') is None:pytest.skip('Native CalculiX absent; scheduled native worker installs it')
    path=tmp_path_factory.mktemp('native-composite')/'run'
    result=run_structural_fixture(path,root=EVIDENCE)
    return path,result


def test_native_composite_refinement_and_reactions_pass_the_method_fixture(native):
    path,result=native
    assert result['method_screen']=='pass'
    assert result['refinement']['accuracy_improves_or_small']
    assert len(result['rows'])==2 and all(r['numerical_validity']=='valid' for r in result['rows'])
    assert all(r['tip_relative_error']<.01 and r['frequency_relative_error']<.01 and r['force_balance_residual_N']<1e-6 for r in result['rows'])
    assert result['complete_equipped_vehicle'] is result['physical_accepted'] is False
    assert verify_structural_fixture(path,root=EVIDENCE)['method_screen']=='pass'


def test_parser_does_not_replace_static_displacement_with_modal_amplitude(native):
    path,result=native;row=result['rows'][0]
    parsed=parse_dat((path/'mesh-8/coupon.dat').read_text(),row['mesh'])
    assert -.003<parsed['mean_tip_displacement_z_m']<-.002
    assert 2.<parsed['frequencies_hz'][0]<3.


def test_resealed_wrong_laminate_input_still_cannot_pass(native,tmp_path):
    source,_=native;copy=tmp_path/'copy';shutil.copytree(source,copy)
    path=copy/'mesh-8/coupon.inp';path.write_text(path.read_text().replace('.001,,PLY,O90','.001,,PLY,O0'))
    manifest=json.loads((copy/'manifest.json').read_bytes());manifest['files_sha256']=_inventory(copy,('manifest.json',))
    (copy/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError,match='input differs'):verify_structural_fixture(copy,root=EVIDENCE)
