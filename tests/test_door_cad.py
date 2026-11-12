"""Primitive CAD checks distinguish material geometry from qualified assembly."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('door_cad',Path(__file__).parents[1]/'engineering/vehicle_parts/door_cad.py')
cad=importlib.util.module_from_spec(spec);spec.loader.exec_module(cad)


def geometry():
    expected=dict(id='header/blank',size_m=[3.,.22,.008],at_m=[0.,0.,0.])
    measured=dict(bodies=[dict(id='header/blank',closed=True,volume_m3=.00528,
        center_of_mass_m=[1.5,.11,.004],bbox_m=dict(min=[0.,0.,0.],max=[3.,.22,.008]))])
    return expected,measured


def test_exact_box_and_import_label_loss_are_separate():
    expected,measured=geometry();r=cad.compare(expected,measured)
    assert r['comparison_passed'] is True and r['native_names_preserved'] is True
    assert r['engineering_accepted'] is r['manufacturing_release'] is False
    measured['bodies'][0]['id']='STEP product'
    with pytest.raises(ValueError,match='identity differs'):cad.compare(expected,measured)
    r=cad.compare(expected,measured,allow_import_label=True)
    assert r['comparison_passed'] is True and r['native_names_preserved'] is False


def test_wrong_units_and_placement_cannot_compensate_for_volume():
    expected,measured=geometry();measured['bodies'][0]['center_of_mass_m'][0]+=1.
    assert cad.compare(expected,measured)['comparison_passed'] is False
    expected,measured=geometry();measured['bodies'][0]['volume_m3']*=1e9
    assert cad.compare(expected,measured)['comparison_passed'] is False


def test_open_or_unmeasured_solid_is_rejected():
    expected,measured=geometry();measured['bodies'][0]['closed']=False
    with pytest.raises(ValueError,match='closed'):cad.compare(expected,measured)
    expected,measured=geometry();measured['bodies'][0]['center_of_mass_m']=None
    with pytest.raises(ValueError,match='centroid'):cad.compare(expected,measured)


def test_missing_or_duplicate_reopen_responses_rejected():
    with pytest.raises(ValueError,match='unique reopen'):cad.reopen_measurements([{'id':1},{'id':2}])
    with pytest.raises(ValueError,match='unique reopen'):cad.reopen_measurements([{'id':1},{'id':2},{'id':3},{'id':3},{'id':5}])
