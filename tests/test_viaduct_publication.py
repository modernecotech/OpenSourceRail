from copy import deepcopy
from pathlib import Path
import json,shutil
import pytest
from engineering.station_rail.common import identity
from engineering.design_search.craft_backends import viaduct_publication as p,native


def reseal(folder):
    m=p.load(folder/'manifest.json');m['files_sha256']=p.inventory(folder)
    m['manifest_id']=identity({k:v for k,v in m.items() if k!='manifest_id'})
    (folder/'manifest.json').write_text(json.dumps(m))


@pytest.fixture
def copy_publication(tmp_path):
    target=tmp_path/'publication';shutil.copytree(p.ROOT/p.OUTPUT,target)
    return target


def test_selected_publication_replays_without_native_tools(monkeypatch):
    def forbidden(*a,**kw):raise AssertionError('Public record verification must not launch a native tool')
    monkeypatch.setattr(native,'run',forbidden)
    result=p.verify()
    assert result['case_count']==12 and result['numerical_comparisons']==2
    assert result['fresh_native_solve'] is False and result['physical_accepted'] is False
    value=p.load(p.ROOT/p.OUTPUT/'summary.json')
    assert value['numerically_screened_comparisons']==2
    assert value['complete_installed_bridge_design'] is False
    assert value['default_backends_changed'] is False


def test_resealed_native_step_bytes_cannot_inherit_geometry_checks(copy_publication):
    f=copy_publication/'models/reference_box--reference/assembly.step'
    f.write_bytes(f.read_bytes()+b'\nchanged\n');reseal(copy_publication)
    with pytest.raises(ValueError,match='native CAD differs'):p.verify(copy_publication)


def test_resealed_delivery_cannot_replace_same_candidate_costs(copy_publication):
    f=copy_publication/'delivery/reference_box--reference.json';value=p.load(f)
    value['cost']['cases']['base']['factory_gate_iqd']=0
    value['delivery_evaluation_id']=identity({k:v for k,v in value.items() if k!='delivery_evaluation_id'})
    f.write_text(json.dumps(value));reseal(copy_publication)
    with pytest.raises(ValueError,match='same-candidate delivery|original delivery artifact'):p.verify(copy_publication)


def test_selected_fem_cannot_hide_original_hold_or_change_refinement(copy_publication):
    analysis=p.load(copy_publication/'evidence/workflow/result.json')['analyses']['folded_plate--reference']
    folder=copy_publication/'evidence/fem/folded_plate--reference';value=p.load(folder/'result.json')
    value['refinement']['displacement_relative_change']=0
    value['result_id']=identity({k:v for k,v in value.items() if k!='result_id'})
    (folder/'result.json').write_text(json.dumps(value))
    with pytest.raises(ValueError,match='Derived refinement summary'):p.selected_numerics(folder,analysis)


def test_tessellation_units_and_missing_triangles_are_rejected(copy_publication):
    f=copy_publication/'models/reference_box--reference/assembly.stl'
    data=f.read_bytes();f.write_bytes(data[:-1])
    with pytest.raises(ValueError,match='triangle coverage'):p.stl_bounds(f)


@pytest.mark.parametrize('relative',['evidence/private-verification.json','evidence/workflow/manifest.json','evidence/cad/freecad-reference/resource.json'])
def test_resealed_outer_manifest_cannot_change_original_execution_receipts(copy_publication,relative):
    f=copy_publication/relative;value=p.load(f);value['test_replacement']='different original receipt'
    f.write_text(json.dumps(value));reseal(copy_publication)
    with pytest.raises(ValueError,match='receipt differs|seal differs|reference execution differs'):p.verify(copy_publication)


def test_recorded_plots_are_portable_and_refuse_overwrite(tmp_path):
    import subprocess,sys
    folder=p.ROOT/p.OUTPUT;output=tmp_path/'replot'
    script=folder/'presentation/render-recorded-plots.py'
    subprocess.run([sys.executable,str(script),'--output',str(output)],cwd=tmp_path,check=True,capture_output=True)
    from PIL import Image
    for name in ('mass-factory-cost.png','fem-deflection.png'):
        with Image.open(output/name) as actual,Image.open(folder/name) as recorded:
            assert max(abs(a-b) for a,b in zip(actual.size,recorded.size))<=2
            assert actual.getbbox() is not None  # Matplotlib versions can round a canvas edge by one pixel.
    second=subprocess.run([sys.executable,str(script),'--output',str(output)],cwd=tmp_path,capture_output=True)
    assert second.returncode!=0


@pytest.mark.parametrize('field',['maximum_bbox_error_m','physical_accepted'])
def test_resealed_STL_report_cannot_invent_a_geometric_screen_or_acceptance(copy_publication,field):
    f=copy_publication/'evidence/stl-export-result01.json';value=p.load(f)
    value['case_checks']['reference_box--reference'][field]=1 if field=='maximum_bbox_error_m' else True
    f.write_text(json.dumps(value));reseal(copy_publication)
    with pytest.raises(ValueError,match='bounding-box screen differs|cannot promote'):p.verify(copy_publication)
