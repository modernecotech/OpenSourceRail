"""Actual native IFC/IDS/BCF and field adapter negative controls."""
from copy import deepcopy
from hashlib import sha256
import gzip
import io
import json
import shutil
import zipfile
import xml.etree.ElementTree as ET
import pytest
from engineering.ferrite_maglev import bim_field as b


def test_actual_exchange_reopens_volumes_and_rejects_stale_ids(tmp_path):
    result=b.study(tmp_path)
    assert result['study_pass'] and result['exchange']['ids_schema_valid']
    assert result['exchange']['stale_revision_refused']
    assert len(result['exchange']['parts'])>100
    assert all(r['volume_relative_error']<result['exchange']['mesh_volume_relative_tolerance'] for r in result['exchange']['parts'])
    assert len(result['bcf']['schema_validated_members'])==4
    assert len(result['negative_controls'])==4
    assert result['field_result']['state']=='performed-awaiting-independent-inspection'
    assert not result['physical_release'] and not result['manufacturing_release']


def test_field_adapter_requires_exact_guid_revision_unit_and_no_acceptance():
    cfg='a'*64;part=dict(ifc_guid='0abcdefghijklmnopqrstu',simulated_serial='SIM-1')
    work=b.field_plan(cfg,part)
    event=dict(id='SIM-FIELD-1',device_id='sim-tablet',work_id=work['id'],status='performed-awaiting-inspection',readings={'gap':dict(value=8.,unit='mm'),'part-revision':cfg,'ifc-guid':part['ifc_guid']},photos=[])
    assert not b.assess_field(work,event,configuration_sha256=cfg,part=part)['engineering_accepted']
    bad=deepcopy(event);bad['readings']['ifc-guid']='wrong'
    with pytest.raises(ValueError,match='stale'):b.assess_field(work,bad,configuration_sha256=cfg,part=part)


def test_selected_span_endinfills_match_manufacturing_quantities_and_change_native_ifc(tmp_path):
    candidate=b.candidate_magnetics.definition()
    selection=dict(section_id='wider-intermediate',span_m=20.)
    products=b.manufacturing.product_definition(candidate,selection=selection)
    parts=b.exchange_parts(candidate,selection=selection)
    concrete=[part for part in parts if part['id'].startswith('civil/')]
    assert len(concrete)==6
    assert sum(part['volume_m3'] for part in concrete)==pytest.approx(products['beam']['concrete_volume_m3'])
    assert max(part['at_m'][0]+part['size_m'][0] for part in concrete)==20.
    exported=b.export_ifc(tmp_path,candidate,selection=selection)
    assert exported['selected_beam']==selection
    assert exported['ids_pass'] and exported['stale_revision_refused']
    ids=(tmp_path/'candidate.ids').read_bytes();ifc=(tmp_path/'candidate.ifc').read_bytes()
    b._retained_ifc(ifc,ids,candidate,exported,selection=selection)
    with pytest.raises(ValueError,match='beam/span'):
        b._retained_ifc(ifc,ids,candidate,exported,selection=dict(section_id='wider-intermediate',span_m=25.))


def test_exchange_refuses_foreign_selected_beam():
    candidate=b.candidate_magnetics.definition()
    beam=b.candidate_structures.selected_beam(candidate)
    beam['configuration_sha256']='f'*64
    with pytest.raises(ValueError,match='configuration'):
        b.exchange_parts(candidate,beam=beam)


@pytest.fixture(scope='module')
def retained_packet(tmp_path_factory):
    output=tmp_path_factory.mktemp('actual-retained-bim');b.publish(output)
    return output


def reseal(folder,name,data):
    (folder/name).write_bytes(data)
    m=json.loads((folder/'manifest.json').read_bytes());m['files_sha256'][name]=sha256(data).hexdigest()
    (folder/'manifest.json').write_bytes(b.platform.encoded(m))


def study_change(folder,mutate):
    value=json.loads(gzip.decompress((folder/'study.json.gz').read_bytes()));mutate(value)
    reseal(folder,'study.json.gz',gzip.compress(b.platform.encoded(value),mtime=0))


def bcf_change(folder,mutate):
    raw=gzip.decompress((folder/'candidate-issues.bcf.gz').read_bytes())
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:members={n:archive.read(n) for n in archive.namelist()}
    mutate(members);out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,data in members.items():archive.writestr(name,data)
    reseal(folder,'candidate-issues.bcf.gz',gzip.compress(out.getvalue(),mtime=0))


def test_retained_native_exchange_is_actually_reopened(retained_packet):
    result=b.verify(retained_packet)
    assert result['verified'] and result['study_pass'] and result['parts']>100
    assert not result['physical_release'] and not result['engineering_accepted']


@pytest.mark.parametrize('change',['garbage-ifc','part-identity','part-guid','source-dimension','duplicate-property','source-world-frame','property-unit','weak-ids','forged-volume-tolerance','field-tolerance','field-evidence-hash','unexecuted-negative','automatic-handback','bcf-guid','bcf-closed','bcf-traversal','readme-overclaim'])
def test_coherently_rehashed_retained_forgeries_are_rejected(retained_packet,tmp_path,change):
    folder=tmp_path/'packet';shutil.copytree(retained_packet,folder)
    if change=='garbage-ifc':reseal(folder,'candidate.ifc.gz',gzip.compress(b'not an IFC file',mtime=0))
    elif change in {'part-identity','part-guid','source-dimension','duplicate-property','source-world-frame','property-unit'}:
        import ifcopenshell
        f=ifcopenshell.file.from_string(gzip.decompress((folder/'candidate.ifc.gz').read_bytes()).decode())
        obj=f.by_type('IfcBuildingElementProxy')[0]
        if change=='part-identity':obj.Name='forged-source-part'
        elif change=='part-guid':obj.GlobalId='0000000000000000000000'
        elif change=='duplicate-property':
            pset=obj.IsDefinedBy[0].RelatingPropertyDefinition
            pset.HasProperties=tuple(pset.HasProperties)+(f.createIfcPropertySingleValue('ManufacturingRelease',None,f.createIfcLabel('false'),None),)
        elif change=='source-world-frame':f.by_type('IfcGeometricRepresentationContext',include_subtypes=False)[0].WorldCoordinateSystem.Location.Coordinates=(1.,0.,0.)
        elif change=='property-unit':
            prop=next(p for p in obj.IsDefinedBy[0].RelatingPropertyDefinition.HasProperties if p.Name=='AccountedMassKG')
            prop.Unit=f.createIfcSIUnit(None,'MASSUNIT',None,'GRAM')
        else:
            solid=obj.Representation.Representations[0].Items[0]
            while solid.is_a('IfcBooleanResult'):solid=solid.FirstOperand
            solid.Depth*=1.01
        reseal(folder,'candidate.ifc.gz',gzip.compress(f.to_string().encode(),mtime=0))
    elif change=='weak-ids':
        root=ET.fromstring(gzip.decompress((folder/'candidate.ids.gz').read_bytes()));ns={'i':'http://standards.buildingsmart.org/IDS'}
        requirements=root.find('.//i:requirements',ns);requirements.remove(list(requirements)[0])
        reseal(folder,'candidate.ids.gz',gzip.compress(ET.tostring(root),mtime=0))
    elif change=='forged-volume-tolerance':study_change(folder,lambda v:v['exchange'].__setitem__('mesh_volume_relative_tolerance',1.))
    elif change=='field-tolerance':study_change(folder,lambda v:v['work']['readings'][0].__setitem__('max',1000.))
    elif change=='field-evidence-hash':study_change(folder,lambda v:v['field_result'].__setitem__('raw_event_sha256','0'*64))
    elif change=='unexecuted-negative':study_change(folder,lambda v:v['negative_controls'][0].__setitem__('refused',False))
    elif change=='automatic-handback':study_change(folder,lambda v:v['event'].__setitem__('status','accepted'))
    elif change=='readme-overclaim':reseal(folder,'README.md',b'All physical acceptance gates passed. Ready for manufacture.\n')
    elif change=='bcf-guid':
        def alter(members):
            name=next(n for n in members if n.endswith('.bcfv'));root=ET.fromstring(members[name]);root.find('./Components/Selection/Component').set('IfcGuid','0000000000000000000000');members[name]=ET.tostring(root)
        bcf_change(folder,alter)
    elif change=='bcf-closed':
        def alter(members):
            name=next(n for n in members if n.endswith('markup.bcf'));root=ET.fromstring(members[name]);root.find('Topic').set('TopicStatus','Closed');members[name]=ET.tostring(root)
        bcf_change(folder,alter)
    else:bcf_change(folder,lambda members:members.__setitem__('../outside.xml',b'<forged/>'))
    with pytest.raises(ValueError):b.verify(folder)


def test_retained_ifc_decompression_is_bounded_before_native_parser(retained_packet,tmp_path):
    folder=tmp_path/'packet';shutil.copytree(retained_packet,folder)
    reseal(folder,'candidate.ifc.gz',gzip.compress(b' '* (b.LIMITS['candidate.ifc.gz']+1),mtime=0))
    with pytest.raises(ValueError,match='decompression'):b.verify(folder)


def test_retained_ifc_symlink_is_refused_even_when_bytes_match(retained_packet,tmp_path):
    folder=tmp_path/'packet';shutil.copytree(retained_packet,folder);target=folder/'candidate.ifc.gz';target.unlink();target.symlink_to(retained_packet/'candidate.ifc.gz')
    with pytest.raises(ValueError,match='ordinary'):b.verify(folder)
