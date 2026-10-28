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
