"""Independent cut-stock controls and receipt/presentation regressions."""
from copy import deepcopy
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
import gzip
import json
import math
import shutil
import sys

import pytest

try:
    from engineering.ferrite_maglev import body_stiffness as b
except ImportError:
    spec=spec_from_file_location('engineering.ferrite_maglev.body_stiffness',Path(__file__).with_name('body_stiffness.py'))
    b=module_from_spec(spec);sys.modules[spec.name]=b;spec.loader.exec_module(b)


@pytest.fixture(scope='module')
def derived():return b.derivation()


def test_exact_gfrp_mass_and_hole_control(derived):
    # Direct independent rectangle and cylindrical cut volumes, two17m tubes.
    area=.14*.22-(.14-.024)*(.22-.024)
    volume=34*area-768*math.pi*.013**2/4*.012
    spacer=384*math.pi*(.025**2-.013**2)/4*.116
    assert derived['current_gfrp_tube_mass_kg']==pytest.approx(volume*1900,rel=1e-12)
    assert derived['current_spacer_mass_kg']==pytest.approx(spacer*7850,rel=1e-12)
    assert derived['actual_wall_penetrations']==768 and derived['actual_bolt_axes']==384
    assert len(derived['source_crush_spacers'])==384
    assert json.loads(b.encoded(derived))==derived


def test_independent_quadrature_control(derived):
    # Independently transformed/smooth-integrated values supplied by a separate
    # arithmetic review. The retained prior uses a slightly coarser Simpson rule.
    expected=[15884338.0691273,33222811.5205361,39744180.4356445,45048338.8227237,49446151.2011034]
    for value,target in zip(derived['variants'],expected):
        assert value['axial']['body_and_coupler_series_stiffness_n_m']==pytest.approx(target,rel=2e-11)
    assert derived['gfrp_existing_axial']['drilled_body_and_coupler_series_stiffness_n_m']==pytest.approx(expected[0],rel=1e-6)


def test_conservative_full_mass_deltas(derived):
    expected=[0.,65.317220870,247.052640590,426.652860310,604.117880031]
    for value,delta in zip(derived['variants'],expected):
        assert value['incremental_stock_and_spacer_mass_kg']==pytest.approx(delta,abs=1e-8)
        assert value['full_aw3_car_mass_kg']==pytest.approx(26200+delta,abs=1e-8)
        assert value['full_train_mass_kg']==6*value['full_aw3_car_mass_kg']
        assert value['directly_replaced_control_mass_kg']==pytest.approx(643.841707934,abs=1e-8)


def test_longer_spacers_retain_outer_stack(derived):
    for value,length in zip(derived['variants'],[.116,.134,.132,.130,.128]):
        stock=value['stock'];assert stock['spacer_length_m']==pytest.approx(length)
        for p in stock['crush_spacers']:
            assert abs(p['at_m'][1]+p['size_m'][2]/2)==pytest.approx(1.1)
            assert p['size_m'][2]==pytest.approx(length)
            assert p['holes'][0]['length_m']==pytest.approx(length)
        assert stock['outer_envelope_unchanged'] and stock['external_bolt_stack_unchanged']


def test_candidate_changes_only_mass_and_lumped_stiffness(derived):
    reference=b.moving_train.candidate_assumptions(b.moving_train.load())[0]
    for variant in derived['variants']:
        a=b.candidate(variant)
        assert {k for k in reference if reference[k]!=a[k]}<={'car_mass_kg','coupler_stiffness_n_m'}
        assert a['inertia_roll_kg_m2']==reference['inertia_roll_kg_m2']
        assert a['inertia_pitch_kg_m2']==reference['inertia_pitch_kg_m2']
        assert not variant['automatic_adoption'] and not variant['joined_body_accepted']


def test_heavier_joint_load_cases_stay_open(derived):
    assert [v['within_existing_hardpoint_mass_target'] for v in derived['variants']]==[True,True,False,False,False]
    for variant in derived['variants']:
        assert variant['existing_hardpoint_mass_target_kg']==26400
        assert variant['mass_ratio_to_existing_hardpoint_target']==variant['full_aw3_car_mass_kg']/26400


@pytest.mark.parametrize('bad',['hole','spacer'])
def test_incomplete_installed_grid_rejected(bad):
    value=b.assembled_body.definition()
    if bad=='hole':next(p for p in value['parts'] if p['id'].startswith('frame/lower-stringer-') and p.get('holes'))['holes'].pop()
    else:value['parts']=[p for p in value['parts'] if p['id']!='hardpoint/1/00/bolt-0/crush-spacer']
    with pytest.raises(ValueError):b._stock(value)


@pytest.mark.parametrize('old,new',[('phase_screen_degrees = 5.0','phase_screen_degrees = 6.0'),('material_properties_qualified = false','material_properties_qualified = true'),('steel_wall_m = [0.003, 0.004, 0.005, 0.006]','steel_wall_m = [0.001]')])
def test_relaxed_criterion_or_qualification_rejected(tmp_path,monkeypatch,old,new):
    p=tmp_path/'bad.toml';p.write_text(b.INPUT.read_text().replace(old,new));monkeypatch.setattr(b,'INPUT',p)
    with pytest.raises(ValueError):b.load()


def test_source_paths_bind_actual_geometry_and_tests():
    values=b.sources()
    for p in (b.INPUT,b.TEST,b.assembled_body.INPUT,Path(b.assembled_body.__file__),Path(b.moving_train.__file__)):
        assert p.relative_to(b.ROOT).as_posix() in values


def test_actual_packet_current():
    if not b.OUTPUT.exists():pytest.skip('full five-run packet must be published first')
    result=b.read_summary();assert result['case_count']==5
    assert result['gfrp_control_above_phase_limit']
    assert result['automatic_adoption'] is False and result['selected_candidate_id'] is None


@pytest.mark.parametrize('bad',['readme','summary-phase','raw-phase','truncated-trace','raw-energy','zero-energy','zero-force','force-witness','missing-force-witness','feedback-disconnected','trajectory-distance','raw-release','missing-source'])
def test_rehashed_false_claims_rejected(tmp_path,bad):
    if not b.OUTPUT.exists():pytest.skip('full five-run packet must be published first')
    p=tmp_path/'packet';shutil.copytree(b.OUTPUT,p);m=json.loads((p/'manifest.json').read_text())
    def update(name,raw):
        (p/name).write_bytes(raw);m['files_sha256'][name]=b.digest(raw)
    if bad=='readme':update('README.md',b'All physical manufacturing accepted.\n')
    elif bad=='summary-phase':
        v=b.inflate((p/'study.json.gz').read_bytes());v['cases'][0]['metrics']['maximum_magnetic_phase_spread_degrees']=.1;v['cases'][0]['confirmation_screen_pass']=True;update('study.json.gz',gzip.compress(b.encoded(v),mtime=0))
    elif bad in {'raw-phase','truncated-trace','raw-energy','zero-energy','zero-force','force-witness','missing-force-witness','feedback-disconnected','trajectory-distance','raw-release'}:
        v=b.inflate((p/'gfrp-control.json.gz').read_bytes())
        if bad=='raw-phase':v['maximum_magnetic_phase_spread_degrees']=.1
        elif bad=='truncated-trace':v['trace']=v['trace'][:1];v['maximum_magnetic_phase_spread_degrees']=.1
        elif bad=='raw-energy':v['longitudinal_energy']['relative_residual']=0.
        elif bad=='zero-energy':v['longitudinal_energy']={key:0. for key in v['longitudinal_energy']}
        elif bad=='zero-force':v['peak_coupler_force_n']=0.
        elif bad=='force-witness':v['coupler_step_witness']['midpoint_relative_velocity_m_s'][100][0]+=.001
        elif bad=='missing-force-witness':v.pop('coupler_step_witness')
        elif bad=='feedback-disconnected':v['feedback_enabled']=False
        elif bad=='trajectory-distance':v['trajectory']['inputs']['distance_m']=2000.
        else:v['physical_output_authorised']=True
        update('gfrp-control.json.gz',gzip.compress(b.encoded(v),mtime=0))
        # Keep summary, presentation and checksums mutually coherent. Only the
        # independent plant/trace/ledger/witness checks should reject these.
        runs=[b.inflate((p/(name+'.json.gz')).read_bytes()) for name in b.RUN_NAMES]
        claims=b._summary(b.derivation(),runs);claims.update(source_sha256=b.sources(),source_unchanged_after_execution=True)
        update('study.json.gz',gzip.compress(b.encoded(claims),mtime=0));update('README.md',b.readme(claims));update('overview.svg',b.overview(claims))
    else:m['source_sha256'].pop('engineering/ferrite_maglev/assembled_body.py')
    (p/'manifest.json').write_bytes(b.encoded(m))
    with pytest.raises(ValueError):b.verify(p)
