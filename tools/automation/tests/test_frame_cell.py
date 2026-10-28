from pathlib import Path
from copy import deepcopy
import importlib.util,io,tarfile,gzip
import pytest
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('frame_cell_current',ROOT/'tools/automation/frame-cell.py');x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x)
h,c,f=x.common(ROOT)
from engineering.component_registry import make_part,make_occurrence,make_registry,summary


def seal(v):v.pop('evaluation_id',None);v['evaluation_id']=h.identity(v);return v


def fixture():
    def part(name,function,width=.1):
        return make_part(name,'A',[function],dict(kind='box',dimensions_m=[1.,width,.1],net_volume_m3=width*.1),None,
            dict(calculated_kg=width*10,lower_bound_kg=width*10,upper_bound_kg=width*10,evidence_state='calculated'),dict(method='test-only'))
    p=part('old-stock','primary-body');q=part('changed-stock','primary-body',.12);a=part('additional-stock','primary-body');battery=part('battery','auxiliary-power');brake=part('brake','running-gear')
    def registry(new,parent=None):
        rows=[]
        for car in range(1,7):
            for name,part in [('retained-stock',q if new else p),('battery',battery),('brake',brake)]+([('arbitrary-addition-no-prefix',a)] if new else []):
                T=[[1.,0.,0.,17.5*(car-1)],[0.,1.,0.,0.],[0.,0.,1.,1.],[0.,0.,0.,1.]]
                rows.append(make_occurrence(f'car-{car}/'+name,part,'car-'+str(car),T,'vehicle/test'))
        parts={z['physical_definition_id']:z for z in ([q,a,battery,brake] if new else [p,battery,brake])}
        return make_registry('frame' if new else 'parent',list(parts.values()),rows,['primary-body','auxiliary-power','running-gear'],parent,assemblies=[dict(id='car-'+str(i),parent_id=None) for i in range(1,7)])
    reg=registry(False);old=seal(dict(candidate_id=reg['candidate_id'],vehicle_id='V4',registry=reg,summary=summary(reg),requirements=dict(cars=6),functional_requirements=reg['required_functions'],interfaces=dict(fixed=True),architecture=dict(passive=True),**x.FLAGS))
    reg2=registry(True,old['candidate_id']);new=deepcopy(old);new.update(candidate_id=reg2['candidate_id'],registry=reg2,summary=summary(reg2),frame_refinement=dict(parent_candidate_id=old['candidate_id'],parent_vehicle_evaluation_id=old['evaluation_id'],new_occurrences_per_car=1,changed_stock=[dict(occurrence_local_name='retained-stock',parent_part_definition_id=p['physical_definition_id'],new_part_definition_id=q['physical_definition_id'],before_dimensions_m=[1.,.1,.1],after_dimensions_m=[1.,.12,.1],new_position_m=[0.,0.,1.])]))
    seal(new);source=seal(dict(candidate_id='old-physical-evidence-context',**x.FLAGS));power=seal(dict(candidate_id=old['candidate_id'],body_candidate_id=old['candidate_id'],actual_registry_id=reg['registry_id'],source_derivation=source,source_derivation_body_candidate_id=source['candidate_id'],source_derivation_evaluation_id=source['evaluation_id'],hardware_counts_per_car=dict(EPC=3,battery=16),**x.FLAGS))
    e=seal(dict(candidate_id=old['candidate_id'],vehicle=old,summary=old['summary'],complete_source_power_case=power,body_revision_derivation=dict(derivation_id='old-derivation'),catalogue=dict(id='actual-product'),replacements=[dict(candidate_id=old['candidate_id'])],**x.FLAGS))
    return e,old,new


def test_actual_declared_stock_rebound_and_services_unchanged_no_prefix_contract():
    e,old,new=fixture();proof=x.boundary(old,new,h)
    assert len(proof['changed_occurrence_ids'])==6 and len(proof['added_occurrence_ids'])==6
    assert proof['protected_nonbody_occurrences']==12 and proof['exact_protected_parts_and_poses']
    result,record=x.derive(e,old,new,h,helper_sha256='a'*64)
    h.sealed(result);h.sealed(record,'derivation_id')
    assert result['candidate_id']==new['candidate_id'] and h.encoded(result['vehicle'])==h.encoded(new)
    assert result['replacements']==e['replacements'] and result['catalogue']==e['catalogue']
    power=result['complete_source_power_case'];h.sealed(power)
    assert power['actual_registry_id']==new['registry']['registry_id']
    assert power['source_derivation']==e['complete_source_power_case']['source_derivation']
    assert power['hardware_counts_per_car']==e['complete_source_power_case']['hardware_counts_per_car']
    assert result['frame_equipment_ancestry']['parent_body_revision_derivation']==e['body_revision_derivation']
    assert result['fitment_screens']['accepted'] is False
    assert result['dependency_invalidation']['inherited_assembly_access_and_body_joint_outcomes_current'] is False


def test_service_hardware_edit_rejected_before_any_solver():
    e,old,new=fixture();new['frame_refinement']['changed_stock'][0]['after_dimensions_m']=[2.,.12,.1];seal(new)
    with pytest.raises(ValueError,match='dimensions differ'):x.boundary(old,new,h)


def test_undeclared_structural_change_rejected():
    e,old,new=fixture();new['frame_refinement']['changed_stock']=[];seal(new)
    with pytest.raises(ValueError,match='Undeclared'):x.boundary(old,new,h)


def test_wrong_new_count_and_ancestor_evidence_rejected():
    e,old,new=fixture();new['frame_refinement']['new_occurrences_per_car']=2;seal(new)
    with pytest.raises(ValueError,match='stock coverage'):x.boundary(old,new,h)
    e,old,new=fixture();e['vehicle']=deepcopy(old);e['vehicle']['extra']='wrong';seal(e['vehicle']);seal(e)
    with pytest.raises(ValueError,match='exact native ancestor'):x.derive(e,old,new,h,helper_sha256='a'*64)


def test_no_self_release_in_ancestry():
    e,old,new=fixture();e['catalogue']['operating_release']=True;seal(e)
    with pytest.raises(ValueError,match='cannot grant release'):x.derive(e,old,new,h,helper_sha256='a'*64)


def archive(path,entries):
    with tarfile.open(path,'w:gz') as tar:
        for name,data,kind in entries:
            info=tarfile.TarInfo(name);info.type=kind;info.size=len(data) if kind==tarfile.REGTYPE else 0
            if kind==tarfile.SYMTYPE:info.linkname='/outside'
            tar.addfile(info,io.BytesIO(data) if kind==tarfile.REGTYPE else None)


@pytest.mark.parametrize('entries',[
    [('../escape',b'x',tarfile.REGTYPE)],
    [('/absolute',b'x',tarfile.REGTYPE)],
    [('symlink',b'',tarfile.SYMTYPE)],
    [('duplicate',b'a',tarfile.REGTYPE),('duplicate',b'b',tarfile.REGTYPE)],
])
def test_publication_rejects_traversal_links_duplicate_members(tmp_path,entries):
    a=tmp_path/'bad.tar.gz';archive(a,entries);dest=tmp_path/'output';dest.mkdir()
    with pytest.raises(ValueError,match='Unsafe/duplicate'):x.safe_unpack(a,dest)
    assert not (tmp_path/'escape').exists()


def test_archive_limits_and_inert_archived_source(tmp_path,monkeypatch):
    a=tmp_path/'source.tar.gz';archive(a,[('helper-source.py',b'raise RuntimeError("must never execute")',tarfile.REGTYPE)])
    dest=tmp_path/'out';dest.mkdir();x.safe_unpack(a,dest)
    assert (dest/'helper-source.py').read_bytes().startswith(b'raise RuntimeError')
    monkeypatch.setattr(x,'MAX_RAW',4);new=tmp_path/'new';new.mkdir()
    with pytest.raises(ValueError,match='budget'):x.safe_unpack(a,new)


def test_publication_rejects_extra_payload_before_source_or_code_replay(tmp_path):
    (tmp_path/'unexpected').write_text('x')
    with pytest.raises(ValueError,match='Closed publication inventory'):x.verify_publication(tmp_path,root=ROOT)


def test_closed_names_include_native_metadata_and_full_ifc():
    assert len(x.names())<64
    assert {'ancestor-native/manifest.json','frame-native/manifest.json','ifc/V4.ifc','ifc/V4.ifc.receipt.json','helper-source.py'}<=x.names()


def test_exact_protected_pose_edit_is_rejected_with_valid_resealed_registry():
    e,old,new=fixture();reg=new['registry'];occ=deepcopy(reg['occurrences'])
    next(o for o in occ if o['occurrence_id']=='car-1/battery')['transform'][2][3]+=.001
    r=make_registry(reg['label'],reg['parts'],occ,reg['required_functions'],reg['parent_candidate_id'],reg['assemblies'],reg['materials'])
    new.update(candidate_id=r['candidate_id'],registry=r,summary=summary(r));seal(new)
    with pytest.raises(ValueError,match='non-body hardware change'):x.boundary(old,new,h)


def test_publication_snapshot_includes_manifest_added_files_and_exact_bytes(tmp_path):
    (tmp_path/'manifest.json').write_bytes(b'original-manifest');(tmp_path/'data').write_bytes(b'original')
    original=x.snapshot(tmp_path,h)
    (tmp_path/'data').write_bytes(b'modified');assert x.snapshot(tmp_path,h)!=original
    (tmp_path/'data').write_bytes(b'original');(tmp_path/'extra').write_bytes(b'new');assert x.snapshot(tmp_path,h)!=original
    assert 'manifest.json' in original


@pytest.fixture
def publication_contract(tmp_path,monkeypatch):
    """A tiny transport fixture; mocked replay is not numerical evidence."""
    folder=tmp_path/'publication';folder.mkdir();epoch={'test-fixture.py':'a'*64}
    monkeypatch.setattr(x,'source_map',lambda *args:epoch)
    inner=dict(package_id='b'*64,candidate_id='c'*64,body_candidate_id='d'*64,evaluation_id='e'*64,conditional_arrivals=4,conditional_motion_screens=3,physical_qualification=None,selection_purpose='next-experiment-only')
    summary=dict(inner,**x.FLAGS);h.write(folder/'summary.json',summary)
    archive(folder/'frame-cell.tar.gz',[('manifest.json',h.encoded(inner),tarfile.REGTYPE)])
    check=dict(verified=True,package_id=inner['package_id'],actual_IFC_reopened=True,semantic_replay_executed=True,numerical_native_recomputed=False,cases=1,journeys=9,physical_qualification=None,**x.FLAGS)
    calls=[]
    def actual_interface(output,*,root,replay):
        calls.append(dict(root=root,replay=replay,manifest=h.read(Path(output)/'manifest.json')))
        return dict(check)
    monkeypatch.setattr(x,'verify',actual_interface)
    pub=dict(schema='osr-frame-cell-publication/1',source_sha256=epoch,validation=deepcopy(check),files={n:dict(sha256=x.sha(folder/n),bytes=(folder/n).stat().st_size) for n in ('frame-cell.tar.gz','summary.json')},**x.FLAGS)
    pub['publication_id']=h.identity(pub);h.write(folder/'manifest.json',pub)
    return folder,pub,check,calls


def test_verify_publication_returns_verified_report_after_required_replay(publication_contract):
    folder,pub,check,calls=publication_contract
    result=x.verify_publication(folder,root=ROOT)
    assert result==dict(check,publication_id=pub['publication_id'])
    assert result['verified'] is True and result['semantic_replay_executed'] is True
    assert result['actual_IFC_reopened'] is True and result['journeys']==9
    assert len(calls)==1 and calls[0]['replay'] is True and calls[0]['root']==ROOT
    assert calls[0]['manifest']['package_id']==check['package_id']


def test_verify_publication_still_rejects_inconsistent_replay(publication_contract):
    folder,pub,check,calls=publication_contract
    pub['validation']['journeys']=8;pub.pop('publication_id');pub['publication_id']=h.identity(pub);h.write(folder/'manifest.json',pub)
    with pytest.raises(ValueError,match='actual replay differs'):x.verify_publication(folder,root=ROOT)
    assert len(calls)==1 and calls[0]['replay'] is True


def test_verify_publication_still_rejects_resealed_summary_after_replay(publication_contract):
    folder,pub,check,calls=publication_contract
    summary=h.read(folder/'summary.json');summary['conditional_arrivals']=9;h.write(folder/'summary.json',summary)
    pub['files']['summary.json']=dict(sha256=x.sha(folder/'summary.json'),bytes=(folder/'summary.json').stat().st_size)
    pub.pop('publication_id');pub['publication_id']=h.identity(pub);h.write(folder/'manifest.json',pub)
    with pytest.raises(ValueError,match='summary differs'):x.verify_publication(folder,root=ROOT)
    assert len(calls)==1
