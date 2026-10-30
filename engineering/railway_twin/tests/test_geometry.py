from copy import deepcopy
import json
import math
import os

import pytest

from engineering.railway_twin import geometry as g


def occurrence(name, part, shift=(0.,0.,0.)):
    part=dict(part,volume_m3=part['volume_m3'],mass_kg=part['volume_m3']*1000,material='research-material')
    return dict(id=name,component_definition_id='b'*64,system='fixture-stock',translation_m=list(shift),
                geometry=part,scope='nominal-stock',mass_kg=part['mass_kg'])


def scene():
    return dict(schema='osr-railway-twin-scene/1',candidate_id='a'*64,complete_installed_geometry=False,occurrences=[
        occurrence('box',dict(kind='box',at_m=[0.,0.,0.],size_m=[1.,2.,3.],volume_m3=6.),(12.,3.,4.)),
        occurrence('rhs',dict(kind='oriented-RHS',start_m=[0.,0.,0.],end_m=[2.,0.,0.],width_m=.2,height_m=.3,wall_m=.01,volume_m3=2*(.2*.3-.18*.28))),
        occurrence('annulus',dict(kind='annular-cylinder',at_m=[0.,0.,0.],axis=[0.,1.,0.],radius_m=.1,inner_radius_m=.05,length_m=.4,volume_m3=math.pi*(.1**2-.05**2)*.4),(3.,1.,2.)),
        occurrence('drilled',dict(kind='box',at_m=[0.,0.,0.],size_m=[1.,1.,.1],holes=[dict(axis='z',x_m=.3,y_m=.4,diameter_m=.1)],volume_m3=.1-math.pi*.05**2*.1),(4.,1.,0.))])


def test_analytic_stock_properties_and_world_translation():
    result=g.validate_scene(scene());rows={r['id']:r for r in result['occurrences']}
    assert rows['box']['centroid_m']==[12.5,4.,5.5]
    assert rows['box']['bounds_min_m']==[12.,3.,4.]
    assert rows['annulus']['volume_m3']==pytest.approx(math.pi*.0075*.4)
    assert rows['rhs']['bounds_min_m']==pytest.approx([0.,-.1,-.15])
    assert rows['drilled']['centroid_m'][0]>4.5
    assert result['complete_installed_geometry'] is False and result['physical_accepted'] is False


@pytest.mark.parametrize('mutation',[
    lambda x:x['occurrences'].append(deepcopy(x['occurrences'][0])),
    lambda x:x['occurrences'][0]['geometry'].update(size_m=[2.,2.,3.]),
    lambda x:x['occurrences'][0].update(mass_kg=0),
    lambda x:x.update(complete_installed_geometry=True),
    lambda x:x.update(physical_accepted=True),
])
def test_invalid_or_mixed_quantity_scene_rejected(mutation):
    value=scene();mutation(value)
    with pytest.raises(ValueError):g.validate_scene(value)


def test_declared_density_cannot_hide_an_inconsistent_mass():
    value=scene();value['occurrences'][0]['geometry']['density_kg_m3']=100.
    with pytest.raises(ValueError,match='volume and declared density'):g.validate_scene(value)


def test_genuine_ifc_roundtrip_with_boolean_hole_and_hollow_stock(tmp_path):
    value=scene();receipt=g.write_ifc(value,tmp_path)
    assert (tmp_path/g.IFC_NAME).read_bytes().startswith(b'ISO-10303-21;')
    result=g.verify_ifc(value,tmp_path,receipt)
    assert result['native_reopened'] and result['occurrence_count']==4
    assert result['maximum_relative_volume_error']<.002


def reseal(receipt,path):
    changed=deepcopy(receipt);changed['sha256']=g._hash(path)
    changed['receipt_id']=g._identity({k:v for k,v in changed.items() if k!='receipt_id'})
    return changed


def test_equal_volume_moved_ifc_is_rejected_even_after_receipt_reseal(tmp_path):
    import ifcopenshell
    value=scene();receipt=g.write_ifc(value,tmp_path);path=tmp_path/g.IFC_NAME
    f=ifcopenshell.open(str(path));obj=next(o for o in f.by_type('IfcBuildingElementProxy') if o.Name=='box')
    obj.ObjectPlacement.RelativePlacement.Location.Coordinates=(13.,3.,4.)
    f.write(str(path))
    with pytest.raises(ValueError,match='placement differs'):g.verify_ifc(value,tmp_path,reseal(receipt,path))


def test_equal_volume_changed_ifc_profile_is_rejected_after_reseal(tmp_path):
    import ifcopenshell
    value=scene();receipt=g.write_ifc(value,tmp_path);path=tmp_path/g.IFC_NAME
    f=ifcopenshell.open(str(path));obj=next(o for o in f.by_type('IfcBuildingElementProxy') if o.Name=='box')
    profile=obj.Representation.Representations[0].Items[0].SweptArea
    profile.XDim=2.;profile.YDim=1.
    f.write(str(path))
    with pytest.raises(ValueError,match='actual primitive geometry differs'):g.verify_ifc(value,tmp_path,reseal(receipt,path))


def test_ifc_material_or_release_cannot_be_forged_by_resealing(tmp_path):
    import ifcopenshell
    import ifcopenshell.api
    value=scene();receipt=g.write_ifc(value,tmp_path);path=tmp_path/g.IFC_NAME
    f=ifcopenshell.open(str(path));obj=f.by_type('IfcBuildingElementProxy')[0]
    pset=next(r.RelatingPropertyDefinition for r in obj.IsDefinedBy if r.RelatingPropertyDefinition.Name=='OSR_Research_Identity')
    ifcopenshell.api.run('pset.edit_pset',f,pset=pset,properties={'physical_accepted':True})
    f.write(str(path))
    with pytest.raises(ValueError,match='identity, material, mass or scope differs'):g.verify_ifc(value,tmp_path,reseal(receipt,path))


def test_missing_native_tool_is_explicit_not_a_format_substitute(tmp_path,monkeypatch):
    monkeypatch.setattr(g,'_native_command',lambda script:None)
    receipt=g.export_native(scene(),tmp_path)
    assert receipt['execution']=='not-run' and not list(tmp_path.iterdir())
    assert g.verify_native(scene(),tmp_path,receipt)['execution']=='not-run'
    forged=deepcopy(receipt);forged['physical_accepted']=True
    with pytest.raises(ValueError):g.verify_native(scene(),tmp_path,forged)


def test_flatpak_native_command_uses_absolute_scoped_case_path(tmp_path, monkeypatch):
    monkeypatch.setattr(g.shutil, 'which', lambda name: '/usr/bin/flatpak' if name == 'flatpak' else None)
    script = tmp_path / 'native-worker.py'
    command = g._native_command(script)
    assert command == ['/usr/bin/flatpak', 'run', '--filesystem=' + str(tmp_path.resolve()),
                       '--command=FreeCADCmd', 'org.freecad.FreeCAD', str(script.resolve())]


def test_translated_repeated_ifc_instances_keep_distinct_occurrence_placements(tmp_path):
    value=scene();first=deepcopy(value['occurrences'][0]);first['id']='same-box-another-car'
    first['translation_m']=[29.5,3.,4.];value['occurrences'].append(first)
    receipt=g.write_ifc(value,tmp_path)
    assert g.verify_ifc(value,tmp_path,receipt)['occurrence_count']==5
    import ifcopenshell
    f=ifcopenshell.open(str(tmp_path/g.IFC_NAME))
    boxes=[obj for obj in f.by_type('IfcBuildingElementProxy') if obj.Name in ('box','same-box-another-car')]
    assert boxes[0].Representation.id()==boxes[1].Representation.id()


@pytest.mark.skipif(os.environ.get('OSR_RUN_NATIVE_TWIN_TEST')!='1',reason='Explicit actual FreeCAD test invocation required')
@pytest.mark.parametrize('single',[False,True])
def test_actual_native_world_placement_roundtrip_for_translated_box_rhs_and_cylinder(tmp_path,single):
    value=scene()
    if single:value['occurrences']=value['occurrences'][:1]
    receipt=g.export_native(value,tmp_path)
    assert receipt['execution']=='completed'
    assert (tmp_path/'railway-twin.FCStd').is_file()
    assert (tmp_path/'railway-twin.step').read_bytes().startswith(b'ISO-10303-21;')
    assert g.verify_native(value,tmp_path,receipt)['native_reopened']
    actual=json.loads((tmp_path/'native-result.json').read_bytes())
    assert any(row['bounds_min_m']==pytest.approx([12.,3.,4.]) for row in actual['STEP_solids'])
    assert len(actual['STEP_solids'])==(1 if single else 4)
