"""Real IfcTester IDS, retained native tessellation and deliberately corrupted IFC."""
from copy import deepcopy
import pytest
from engineering.assembly_design import structural_bay as s,baseline,bim
from engineering.twin_workflow import core


@pytest.fixture
def candidate():
    p=core.read(baseline.DATA);p['pilots']['structural-bay']=s.PILOT
    return s.build(p,next(s.candidates(p)))


def mesh(candidate):
    return dict(parts=[dict(id=p['id'],vertices=[[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]],faces=[[0,1,2]]) for p in candidate['contract']['parts']])


def test_ifc_ids_reopen_all_required_information_and_stable_ids(tmp_path,candidate):
    receipt=bim.export(candidate,None,tmp_path,meshdata=mesh(candidate))
    assert receipt['state']=='information-only' and receipt['ids_verified']
    assert 'fixture' in receipt['mesh_basis']
    assert receipt['part_count']==30
    check=bim.verify(candidate,tmp_path/'assembly.ifc',ids_path=tmp_path/'requirements.ids')
    assert check['state']=='information-pass' and check['identity_match']
    assert all(check[k] is False for k in core.FLAGS)


@pytest.mark.parametrize('mutation',('missing-property','stale-revision','wrong-name','wrong-id','wrong-material'))
def test_ifctester_rejects_deliberate_information_mutations(tmp_path,candidate,mutation):
    import ifcopenshell
    import ifcopenshell.util.element
    bim.export(candidate,None,tmp_path,meshdata=mesh(candidate))
    model=ifcopenshell.open(str(tmp_path/'assembly.ifc'));product=model.by_type('IfcBuildingElementProxy')[0]
    if mutation=='wrong-material':
        next(r for r in product.HasAssociations if r.is_a('IfcRelAssociatesMaterial')).RelatingMaterial.Name='wrong-material'
    elif mutation=='wrong-name':product.Name='wrong-part'
    elif mutation=='wrong-id':product.GlobalId=ifcopenshell.guid.new()
    else:
        pset=next(r.RelatingPropertyDefinition for r in product.IsDefinedBy if r.is_a('IfcRelDefinesByProperties'))
        if mutation=='missing-property':pset.HasProperties=[p for p in pset.HasProperties if p.Name!='QAState']
        else:next(p for p in pset.HasProperties if p.Name=='CandidateRevision').NominalValue= model.create_entity('IfcLabel','stale')
    path=tmp_path/'tampered.ifc';model.write(str(path))
    assert bim.verify(candidate,path,ids_path=tmp_path/'requirements.ids')['state']=='failed'


def test_mesh_identity_finiteness_and_indexes_rejected(tmp_path,candidate):
    value=mesh(candidate);value['parts'][0]['id']='missing'
    with pytest.raises(ValueError,match='identity'):bim.export(candidate,None,tmp_path/'identity',meshdata=value)
    value=mesh(candidate);value['parts'][0]['vertices'][0][0]=float('nan')
    with pytest.raises(ValueError,match='coordinates'):bim.export(candidate,None,tmp_path/'nan',meshdata=value)
    value=mesh(candidate);value['parts'][0]['faces']=[[0,1,300]]
    with pytest.raises(ValueError,match='faces'):bim.export(candidate,None,tmp_path/'faces',meshdata=value)


def test_real_native_geometry_to_ifc_ids_and_stale_cad_revision_guard(tmp_path,candidate):
    from engineering.continuous_design import study_confirmation
    definition=tmp_path/'definition.json';core.write(definition,candidate['contract'])
    proof,state,error=study_confirmation.native(definition,tmp_path/'cad')
    if state=='hold':pytest.skip('Native tool unavailable: '+str(error))
    assert state=='passed',error
    cad=tmp_path/'cad/candidate.FCStd'
    receipt=bim.export(candidate,cad,tmp_path/'bim')
    assert receipt['mesh_basis']=='retained native CAD tessellation'
    assert receipt['source_cad_sha256']==core.sha(cad)
    check=bim.verify(candidate,tmp_path/'bim/assembly.ifc',ids_path=tmp_path/'bim/requirements.ids')
    assert check['state']=='information-pass'
    changed=deepcopy(candidate);changed['contract']['revision']='other'
    with pytest.raises(ValueError,match='exact candidate'):bim.export(changed,cad,tmp_path/'stale')


def test_ifc_guid_scopes_part_identity_to_architecture_and_family():
    assert bim.global_id('mount-bolt-0','baghdad/structural-bay')!=bim.global_id('mount-bolt-0','baghdad/service-cassette')
    assert bim.global_id('mount-bolt-0','baghdad/structural-bay')==bim.global_id('mount-bolt-0','baghdad/structural-bay')
