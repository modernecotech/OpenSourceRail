"""Door package keeps canonical component ownership and engineering holds."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import pytest
from engineering.vehicle_parts import catalogue
from engineering.station_rail.common import identity

spec=importlib.util.spec_from_file_location('door_module',Path(__file__).parents[1]/'engineering/vehicle_parts/door_module.py')
door=importlib.util.module_from_spec(spec);spec.loader.exec_module(door)


@pytest.fixture(scope='module')
def bundle():
    return catalogue.build(root=Path(catalogue.__file__).resolve().parents[2])


def reseal(bundle):
    bundle['evaluation_id']=identity({k:v for k,v in bundle.items() if k not in ('evaluation_id','bundle_id')})
    bundle['bundle_id']=identity(dict(candidate_id=bundle['candidate_id'],evaluation_id=bundle['evaluation_id']))


def test_counted_ownership_and_no_reference_fleet_or_mass_inheritance(bundle):
    value=door.compile_module(bundle)
    assert value['candidate_id']=='907da3680bcbd01ffe1223652443e4e34a9f581e201385917a99edf4150bd90a'
    assert value['parent_candidate_id']=='756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3'
    assert {p['assembly_id'] for p in value['parts']}==set(door.ASSEMBLIES)
    assert all(p['quantity_per_train']==12*p['quantity_per_opening'] for p in value['parts'])
    assert value['fleet'] is None and value['city_cost'] is None
    assert value['installed_mass_kg_per_opening'] is None
    assert value['engineering_accepted'] is value['manufacturing_release'] is False
    assert all(p['installed_transform_m'] is None for p in value['parts'])
    assert value['module_id']==identity({k:v for k,v in value.items() if k!='module_id'})


def test_stock_commands_use_known_dimensions_and_local_frame_without_holes(bundle):
    value=door.compile_module(bundle);stock=value['representative_stock']
    assert stock['drawing_data']['hole_coordinates_m'] is None
    assert stock['drawing_data']['approved_tolerances'] is None
    boxes=[x for x in stock['solidcraft_commands']['commands'] if x['command']=='solid.box']
    assert len(boxes)==1
    assert {k:boxes[0]['params'][k] for k in ('length','width','height')}==dict(length=3000.,width=220.,height=8.)
    assert boxes[0]['params']['corner']==[0.,0.,0.]
    assert stock['stock_only'] is True and stock['installed_placement_verified'] is False
    assert all(q['observed_result'] is None and q['approved_limit'] is None for p in value['parts'] for q in p['inspection_plan'])


def test_dropped_physical_part_cannot_be_hidden_by_resealing(bundle):
    wrong=deepcopy(bundle)
    wrong['parts']=[p for p in wrong['parts'] if p['id']!=door.REPRESENTATIVE]
    reseal(wrong)
    with pytest.raises(ValueError,match='Counted BOM differs'):door.compile_module(wrong)


def test_mixed_candidate_and_bad_expansion_rejected(bundle):
    for field,value in [('candidate_id','f'*64),('quantity_per_train',1)]:
        wrong=deepcopy(bundle);part=next(p for p in wrong['parts'] if p['id']==door.REPRESENTATIVE)
        part[field]=value;reseal(wrong)
        with pytest.raises(ValueError,match='Mixed candidate'):door.compile_module(wrong)


def test_unknown_mass_keeps_complete_totals_unknown(bundle):
    unknown=deepcopy(bundle)
    part=next(p for p in unknown['parts'] if p['id']==door.REPRESENTATIVE)
    part['mass_each_kg']={c:None for c in ('low','base','high')}
    part['mass_basis']=dict(kind='unknown',description='Test missing weighing/stock evidence')
    reseal(unknown);value=door.compile_module(unknown)
    for case in ('low','base','high'):
        assert value['nominal_mass'][case]['complete_nominal_kg_per_opening'] is None
        assert value['nominal_mass'][case]['complete_nominal_kg_per_train'] is None
        assert value['nominal_mass'][case]['known_subtotal_kg_per_opening']>0
        assert door.REPRESENTATIVE in value['nominal_mass'][case]['unknown_part_ids']
