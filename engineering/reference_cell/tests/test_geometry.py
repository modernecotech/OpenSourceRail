"""Small synthetic fixtures test real file reopening, never a railway release."""
from copy import deepcopy
import json

import ifcopenshell
import pytest

from engineering.component_registry import make_part,make_occurrence,make_registry
from engineering.component_registry.materials import catalogue
from engineering.reference_cell import geometry as g
from engineering.reference_cell.vehicles import FLAGS,pose
from engineering.station_rail.common import identity,digest,encoded


@pytest.fixture(scope='module')
def vehicle():
    materials={m['grade_id']:m for m in catalogue()['materials']}
    parts=[]
    for name,shape,grade in (
        ('box',dict(kind='box',dimensions_m=[2.,.3,.1],net_volume_m3=.06),'AL-6082-T6-EXTRUSION'),
        ('tube',dict(kind='tube',dimensions_m=dict(length=.4,outer_radius=.1,inner_radius=.08),net_volume_m3=3.141592653589793*(.1**2-.08**2)*.4),'STEEL-S355-HYPOTHESIS'),
        ('battery',dict(kind='envelope',dimensions_m=[.5,.6,.4],net_volume_m3=None),None)):
        density=None if grade is None else materials[grade]['density_kg_m3']['nominal']
        mass=dict(calculated_kg=None,lower_bound_kg=10.,upper_bound_kg=20.,evidence_state='bounded-estimate') if grade is None else dict(calculated_kg=shape['net_volume_m3']*density,lower_bound_kg=shape['net_volume_m3']*density,upper_bound_kg=shape['net_volume_m3']*density,evidence_state='calculated')
        parts.append(make_part(name,'A',[name],shape,None if grade is None else materials[grade]['material_id'],mass,dict(method='test-fixture-only')))
    occurrences=[make_occurrence('car-1/box-1',parts[0],transform=pose(1.,2.,3.)),
                 make_occurrence('car-1/tube-1',parts[1],transform=pose(3.,1.,.5,'y')),
                 make_occurrence('car-1/battery-1',parts[2],transform=pose(5.,0.,1.)),
                 make_occurrence('car-1/box-2',parts[0],transform=pose(8.,2.,3.))]
    registry=make_registry('Synthetic geometry fixture',parts,occurrences,['box','tube','battery'])
    value=dict(vehicle_id='TEST',candidate_id=registry['candidate_id'],registry=registry,source_sha256={},**FLAGS)
    value['evaluation_id']=identity(value);return value


def reseal(path):
    receipt_path=path.with_suffix('.ifc.receipt.json');receipt=json.loads(receipt_path.read_bytes())
    receipt['file_sha256']=digest(path);receipt['receipt_id']=identity({k:v for k,v in receipt.items() if k!='receipt_id'})
    receipt_path.write_bytes(encoded(receipt))


def test_actual_ifc_reopens_all_occurrences_and_reuses_exact_shapes(vehicle,tmp_path):
    receipt=g.export_ifc(vehicle,tmp_path)
    assert receipt['reopened']['physical_occurrences']==4
    assert receipt['reopened']['unique_part_shapes']==3
    assert receipt['reopened']['purchased_bounding_volume_m3']==pytest.approx(.12)
    assert receipt['reopened']['purchased_bounding_volume_is_material_or_mass'] is False
    result=g.verify_ifc(vehicle,tmp_path)
    assert result['verified'] and result['actual_reopened']
    assert result['native_reuse_eligible'] is False
    assert all(result[key] is False for key in FLAGS)


@pytest.mark.parametrize('mutation', ['placement','depth','material','mapping','occurrence','acceptance'])
def test_resealed_wrong_geometry_material_or_identity_is_rejected(vehicle,tmp_path,mutation):
    g.export_ifc(vehicle,tmp_path);path=tmp_path/'TEST.ifc';file=ifcopenshell.open(str(path))
    product=next(p for p in file.by_type('IfcBuildingElementProxy') if p.Tag=='car-1/box-1')
    if mutation=='placement':product.ObjectPlacement.RelativePlacement.Location.Coordinates=(2.,2.,3.)
    elif mutation=='depth':file.by_type('IfcExtrudedAreaSolid')[0].Depth*=1.2
    elif mutation=='material':file.by_type('IfcMaterial')[0].Name='Invented grade'
    elif mutation=='mapping':product.Representation.Representations[0].Items[0].MappingTarget.Scale=2.
    elif mutation=='occurrence':product.Tag='missing-occurrence'
    else:
        pset=next(p for p in file.by_type('IfcPropertySet') if p.Name=='OSR_Candidate')
        next(p for p in pset.HasProperties if p.Name=='physical_accepted').NominalValue=file.create_entity('IfcText','True')
    file.write(str(path));reseal(path)
    with pytest.raises(ValueError):g.verify_ifc(vehicle,tmp_path)


def test_fresh_immutable_output_and_mixed_registry_are_required(vehicle,tmp_path):
    g.export_ifc(vehicle,tmp_path)
    with pytest.raises(ValueError):g.export_ifc(vehicle,tmp_path)
    different=deepcopy(vehicle);different['candidate_id']='a'*64
    different['evaluation_id']=identity({k:v for k,v in different.items() if k!='evaluation_id'})
    with pytest.raises(ValueError):g.verify_ifc(different,tmp_path)


def test_missing_native_tool_preserves_hold_without_fabricated_cad(vehicle,tmp_path,monkeypatch):
    monkeypatch.setattr(g,'_native_command',lambda script:None)
    result=g.export_native(vehicle,tmp_path/'native')
    assert result['execution']=='not-run'
    assert result['physical_accepted'] is False
    assert not list((tmp_path/'native').iterdir())


@pytest.mark.parametrize('options',[dict(timeout_s=241),dict(memory_bytes=100),dict(cars=(7,)),dict(cars=(1,1))])
def test_native_resources_and_actual_car_scope_are_bounded(vehicle,tmp_path,options):
    with pytest.raises(ValueError):g.export_native(vehicle,tmp_path/'native',**options)
