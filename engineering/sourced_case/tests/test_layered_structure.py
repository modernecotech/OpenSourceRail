"""Material distinctions, physical revision and numerical method regressions."""
from copy import deepcopy
from pathlib import Path
import gzip
import json
import math
import pytest
import numpy as np

from engineering.sourced_case import layered_structure as s
from engineering.component_registry import validate_registry

ROOT=Path(__file__).resolve().parents[3]
CACHE=Path('/home/hayder/.local/state/opensourcerail/reference-cell-native-20261028/vehicles')

@pytest.fixture(scope='module')
def vehicle():
    if (CACHE/'V1.json.gz').exists():
        value=json.loads(gzip.decompress((CACHE/'V1.json.gz').read_bytes()))
    else:
        from engineering.reference_cell.vehicles import evaluate
        value=evaluate('V1',root=ROOT)
    s._vehicle(value)
    return value


def test_primary_manufacturer_data_grade_and_direction():
    sources=s.primary_sources(ROOT);core=next(x for x in sources['documents'] if x['id']=='gurit-kerdyn80')
    assert core['core_G_0deg_Pa']==18e6 and core['core_G_90deg_Pa']==16e6
    assert core['through_thickness_compressive_E_Pa']==74e6 and core['longitudinal_axial_E_Pa'] is None
    assert core['design_strength_allowable_Pa'] is None
    assert all(len(x['raw_sha256'])==64 and x['raw_bytes']>200000 for x in sources['documents'])


def test_parallel_axis_couple_and_core_shear():
    section=s.layered_section([dict(z_m=-.025,thickness_m=.003,E_Pa=20e9),dict(z_m=.025,thickness_m=.003,E_Pa=20e9)],.047,2.,16e6)
    assert section['composite_to_independent_EI_ratio']>800
    assert section['core_longitudinal_E_Pa'] is None
    assert section['core_shear_stiffness_N']==pytest.approx(16e6*2*.05**2/.047)
    assert section['EI_Nm2']==pytest.approx(2*20e9*2*(.003**3/12+.003*.025**2))


def test_published_hexcel_benchmark_not_vehicle_acceptance():
    b=s.benchmarks()
    assert b['benchmark_pass']
    assert .0428<b['independent_analytical_deflection_m']<.0430
    assert max(r['relative_error'] for r in b['finite_element_runs'])<1e-8
    assert abs(b['computed_simplified_D_Nm2']-5869.6)<.1


def test_timoshenko_stiffness_symmetry_rigid_modes():
    K=s.timoshenko_stiffness(2.,5000.,2e6)
    assert np.allclose(K,K.T)
    assert np.linalg.norm(K@np.array([1.,0.,1.,0.]))<1e-8
    assert np.linalg.norm(K@np.array([0.,1.,2.,1.]))<1e-8


def test_finite_bearing_compliance_energy_and_equilibrium():
    r=s.beam_response(2.,5000.,2e6,[(1.,-1500.)],bearing_patches=[dict(a_m=0.,b_m=.1,kn_N_m=1e7),dict(a_m=1.9,b_m=2.,kn_N_m=1e7)],divisions=16)
    assert r['numerical_valid'] and abs(r['force_balance_residual_N'])<1e-6 and abs(r['moment_balance_residual_Nm'])<1e-6
    assert r['maximum_deflection_m']>0 and r['strain_energy_J']>0
    assert r['approved_deflection_limit_m'] is None


def test_actual_inventory_preserves_gaps_and_laminate_identity(vehicle):
    rows,panels=s.inventory(vehicle)
    assert len(panels)==8
    assert all(p['width_m']==pytest.approx(2.65) and p['length_m']==pytest.approx(4.18) for p in panels)
    assert all(p['core_G_Pa']==16e6 for p in panels)
    assert any(patch['actual_vertical_gap_m']>.02 for p in panels for patch in p['bearing_patches'])
    assert all(p['section']['core_longitudinal_E_Pa'] is None for p in panels)
    assert any(b['status']=='missing-counted-bond-layer' for p in panels for b in p['bond_audit'])
    assert all('hypothesis' in f['basis'] for p in panels for f in p['faces'])


def test_model_property_change_is_evaluation_not_geometry(vehicle):
    a=s.request(vehicle,root=ROOT,face_E_GPa_hypothesis=17.)
    b=s.request(vehicle,root=ROOT,face_E_GPa_hypothesis=20.)
    assert a['candidate_id']==b['candidate_id'] and a['request_id']!=b['request_id']


def test_counted_physical_revision_mass_ancestry_and_finite_contacts(vehicle):
    revised=s.revision(vehicle,root=ROOT)
    validate_registry(revised['registry'])
    assert revised['candidate_id']!=vehicle['candidate_id']
    assert revised['registry']['parent_candidate_id']==vehicle['candidate_id']
    assert revised['per_car_mass_properties']['mass_upper_bound_kg']>vehicle['per_car_mass_properties']['mass_upper_bound_kg']
    assert revised['per_car_occurrences']>vehicle['per_car_occurrences']
    assert revised['requirements']==vehicle['requirements']
    assert all(revised[k] is False for k in s.FLAGS)
    rows,panels=s.inventory(revised)
    assert all(p['width_m']==pytest.approx(2.65) for p in panels)
    assert all(patch['unfilled_gap_m']<1e-8 and patch['counted_support_stack'] for p in panels for patch in p['bearing_patches'])
    assert all(b['finite_bond_thickness_fits_without_solid_overlap'] for p in panels for b in p['bond_audit'])
    assert all(b['adhesive_shear_allowable_Pa'] is None for p in panels for b in p['bond_audit'])
    s._vehicle(revised)


def test_source_guard_and_invalid_resources(vehicle):
    with pytest.raises(ValueError):s.request(vehicle,root=ROOT,divisions=100)
    with pytest.raises(ValueError):s.request(vehicle,root=ROOT,core_direction='isotropic74MPa')
    with pytest.raises(ValueError):s.request(vehicle,root=ROOT,maximum_seconds=241)
    forged=deepcopy(vehicle);forged['candidate_id']='0'*64
    with pytest.raises(ValueError):s.request(forged,root=ROOT)


def test_layer_geometry_refuses_collapse():
    with pytest.raises(ValueError):s.layered_section([dict(z_m=0.,thickness_m=.003,E_Pa=20e9),dict(z_m=.001,thickness_m=.003,E_Pa=20e9)],.05,2.,16e6)


def test_point_offset_moment_conserves_external_load():
    r=s.beam_response(2.,5000.,2e6,[(0.,-500.)],supports=(.3,1.7),point_moments=[(0.,125.)],divisions=12)
    assert r['numerical_valid']
    assert abs(r['moment_balance_residual_Nm'])<1e-7
    assert abs(r['force_balance_residual_N'])<1e-7


def _failed_package(vehicle,folder):
    import io,tarfile
    r=s.request(vehicle,root=ROOT);folder.mkdir()
    (folder/'input.json').write_bytes(s.encoded(r))
    with tarfile.open(folder/'sources.tar','w') as archive:
        for name in r['source_sha256']:
            data=(ROOT/name).read_bytes();item=tarfile.TarInfo(name);item.size=len(data);archive.addfile(item,io.BytesIO(data))
    (folder/'stdout.log').write_text('')
    (folder/'stderr.log').write_text('retained test failure; no numerical solve')
    result=dict(schema='osr-layered-structure-failed/1',request_id=r['request_id'],candidate_id=r['candidate_id'],execution='failed',reason='mocked explicit failed worker',**s.FLAGS)
    (folder/'result.json').write_bytes(s.encoded(result))
    manifest=dict(schema='osr-layered-structure-package/1',request_id=r['request_id'],candidate_id=r['candidate_id'],source_sha256=r['source_sha256'],
        files={p.name:dict(sha256=s.digest(p),bytes=p.stat().st_size) for p in folder.iterdir()},**s.FLAGS)
    manifest['package_id']=s.identity(manifest);(folder/'manifest.json').write_bytes(s.encoded(manifest))
    return manifest


def test_portable_failed_execution_is_not_numerical_success(vehicle,tmp_path):
    folder=tmp_path/'failed';_failed_package(vehicle,folder)
    report=s.verify(folder,root=ROOT,require_current_source=False)
    assert report['execution']=='failed' and report['recorded_source_payload_verified']
    assert not report['current_source_verified'] and not report['current_numerical_recomputed']
    assert not report['full_body_or_physical_acceptance']
    (folder/'stdout.log').write_text('tampered')
    with pytest.raises(ValueError,match='payload'):s.verify(folder,root=ROOT,require_current_source=False)


def test_archive_duplicate_rejected_even_when_outer_hashes_resealed(vehicle,tmp_path):
    import io,tarfile
    folder=tmp_path/'duplicate';manifest=_failed_package(vehicle,folder)
    name=next(iter(manifest['source_sha256']));data=(ROOT/name).read_bytes()
    with tarfile.open(folder/'sources.tar','a') as archive:
        item=tarfile.TarInfo(name);item.size=len(data);archive.addfile(item,io.BytesIO(data))
    manifest['files']['sources.tar']=dict(sha256=s.digest(folder/'sources.tar'),bytes=(folder/'sources.tar').stat().st_size)
    manifest.pop('package_id');manifest['package_id']=s.identity(manifest);(folder/'manifest.json').write_bytes(s.encoded(manifest))
    with pytest.raises(ValueError,match='archive inventory'):s.verify(folder,root=ROOT,require_current_source=False)
