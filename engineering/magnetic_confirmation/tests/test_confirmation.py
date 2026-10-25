"""Independent derivative, continuation, contour and retained-packet guards."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import shutil
import sys

import numpy as np
import pytest

from engineering.magnetic_confirmation import analysis as a,constitutive as c
from engineering.magnetic_confirmation import runner as r
from engineering.magnetic_confirmation.formulation import formulation,COUNTS

STEEL=dict(h_a_m=[0.,20.,30.,40.,50.,60.,80.,100.,150.,200.,300.,500.,1000.,2500.,5000.,10000.,15000.,30000.,100000.],j_t=[0.,.05,.09,.17,.3,.45,.7,.88,1.15,1.28,1.39,1.47,1.54,1.62,1.71,1.82,1.9,1.98,2.04])


def independent_B(H):
    H=np.asarray(H);norm=np.linalg.norm(H)
    return H*(4e-7*np.pi+.0025 if norm<1e-6 else 4e-7*np.pi+np.interp(min(norm,100000.),STEEL['h_a_m'],STEEL['j_t'])/norm)


@pytest.mark.parametrize('norm',[0.,.25e-6,.5e-6,2e-6/3,.99e-6,1.01e-6,10.,35.,70.,175.,750.,7500.,45000.,125000.])
def test_corrected_tangent_matches_independent_oblique_central_difference(norm):
    H=norm*np.array([1.,2.,-3.])/np.sqrt(14);step=max(norm,1e-6)*1e-5
    fd=np.column_stack([(independent_B(H+step*np.eye(3)[i])-independent_B(H-step*np.eye(3)[i]))/(2*step) for i in range(3)])
    assert np.linalg.norm(c.tangent(H,STEEL)-fd,ord=2)/np.linalg.norm(fd,ord=2)<1e-5


def test_low_field_fixture_detects_the_historical_spurious_radial_term():
    H=2e-6/3*np.array([1.,2.,-3.])/np.sqrt(14);correct=c.LOW_MU*np.eye(3);old=correct+(.0025-(.0025*np.linalg.norm(H))/1e-6)/1e-12*np.outer(H,H)
    assert np.linalg.norm(old-correct,ord=2)/c.LOW_MU>.14
    assert np.array_equal(c.tangent(H,STEEL),correct)
    assert c.fixture(STEEL)['passed'] and c.fixture(STEEL)['material_curve_validated'] is False


def stages(count=10,failed=None):
    return '\n'.join(f'LOAD {i/10:.3f} INITIAL 1.000000000000000e+00\nCONTINUATION {i/10:.3f} 1 {1. if failed==i else 1e-11:.15e} {1. if failed==i else 1e-11:.15e}\nSTAGE-END {i/10:.3f} 1 {1. if failed==i else 1e-11:.15e} {1. if failed==i else 1e-11:.15e}' for i in range(1,count+1))+'\n'


def test_every_stage_and_full_source_convergence_are_required():
    assert a.parse_stages(stages())['full_source_converged']
    assert not a.parse_stages(stages(9))['full_source_converged']
    assert not a.parse_stages(stages(failed=4))['full_source_converged']
    assert not a.parse_stages(stages().rsplit('STAGE-END',1)[0])['full_source_converged']


@pytest.mark.parametrize('bad',[lambda t:t.replace('LOAD 0.100','LOAD 0.200',1),lambda t:t.replace('CONTINUATION 0.100 1','CONTINUATION 0.100 2',1),lambda t:t.replace(f'{1e-11:.15e} {1e-11:.15e}',f'{1e-11:.15e} {2e-11:.15e}',1),lambda t:t.replace('STAGE-END 0.100 1','STAGE-END 0.100 0',1),lambda t:t.replace('INITIAL 1.000000000000000e+00','INITIAL nan',1)])
def test_malformed_load_iteration_and_residual_proof_refused(bad):
    with pytest.raises(ValueError):a.parse_stages(bad(stages()))


def source():
    value=a.magnets._build(('N35-H8-half-no-yoke','planar-halbach','Arnold-N35UH',dict(segments=8,magnet_volume_m3=.006)))
    return dict(value=value,vehicle_candidate_id=a.VEHICLE_ID,source_sha256={'fixture-data.json':'1'*64})


def mesh():
    value=source()['value'];pm=[region for region in value['regions'] if region['material']==value['grade_id']];steel=next(region for region in value['regions'] if region['group']=='guideway');stock=[]
    for region in [*pm,steel]:
        lo_y,hi_y,lo_z,hi_z=region['bounds_yz_m'];stock.append(dict(id=region['id'],box_m=[-.5,lo_y,lo_z,1.,hi_y-lo_y,hi_z-lo_z]))
    lo_y=min(q['bounds_yz_m'][0] for q in value['regions'])-.15;hi_y=max(q['bounds_yz_m'][1] for q in value['regions'])+.15;lo_z=min(q['bounds_yz_m'][2] for q in value['regions'])-.15;hi_z=max(q['bounds_yz_m'][3] for q in value['regions'])+.15
    return dict(outer_box_m=[-.65,lo_y,lo_z,1.3,hi_y-lo_y,hi_z-lo_z],physical_pm=list(range(100,100+len(pm))),pm_regions=pm,magnetic_stock=stock,nodes=0,tetrahedra=0)


def fields(directory):
    boxes=a.contours(source()['value']);directory.mkdir(parents=True,exist_ok=True)
    for index,(lo,hi) in enumerate(boxes):
        for axis in range(3):
            other=[i for i in range(3) if i!=axis]
            for side in (0,1):
                rows=[]
                for x in np.linspace(lo[other[0]],hi[other[0]],COUNTS[other[0]]+1):
                    for y in np.linspace(lo[other[1]],hi[other[1]],COUNTS[other[1]]+1):
                        p=list(lo);p[axis]=hi[axis] if side else lo[axis];p[other[0]]=x;p[other[1]]=y;rows.append([*p,0.,0.,.3])
                np.savetxt(directory/f'face-{index}-{axis}-{side}.txt',rows)
    np.savetxt(directory/'PM-H.txt',[[0.,0.,-.02,-500000.],[.1,0.,-.02,-490000.]])
    np.savetxt(directory/'steel-B.txt',[[0.,0.,.005,1.],[.1,0.,.005,1.2]])
    return boxes


def test_guarded_closed_air_contour_constant_field_cancels_force_and_moment(tmp_path,monkeypatch):
    monkeypatch.setattr(a,"validate_scalar_coverage",lambda *args:[dict(mathematical_constant_field_fixture=True)])
    boxes=fields(tmp_path);checks=a.validate_contours(tmp_path,boxes,mesh(),source()['value']);assert len(checks)==12
    result=a.analyze(tmp_path,source(),mesh(),boxes,r.legacy)
    for field in result['air_contour_results']:
        assert np.linalg.norm(field['force_N'])<1e-8 and np.linalg.norm(field['moment_Nm'])<1e-8
    assert result['demag_proxy_margin_A_per_m']==pytest.approx(.8*1990000*(1-.0051*60)-500000.)


@pytest.mark.parametrize('damage',['normal-plane','missing','duplicate','nonfinite'])
def test_wrong_or_incomplete_contour_refused(tmp_path,damage):
    boxes=fields(tmp_path);path=tmp_path/'face-0-0-0.txt';data=np.loadtxt(path)
    if damage=='normal-plane':data[0,0]+=.001
    elif damage=='missing':data=data[:-1]
    elif damage=='duplicate':data[-1]=data[0]
    else:data[0,-1]=np.nan
    np.savetxt(path,data)
    with pytest.raises(ValueError):a.validate_contours(tmp_path,boxes,mesh(),source()['value'])


def test_explicit_generator_has_constant_low_field_tangent_and_all_load_stages():
    text=formulation(source()['value'],mesh(),a.contours(source()['value']))
    assert 'dbdh[Steel]=Norm[$1]<1.e-6 ? (mu0+0.0025)*TensorDiag[1,1,1]' in text
    assert 'br[Region[100]]=$load*Vector' in text and '$load=$stage/10.' in text
    assert 'STAGE-END' in text and 'InitSolution[S]' in text and text.count('InitSolution[S]')==1
    assert 'Print[B,OnPlane' in text and text.count('Print[B,OnPlane')==12


@pytest.fixture
def packet(tmp_path,monkeypatch):
    root=tmp_path/'data';root.mkdir();src=source();monkeypatch.setattr(r.legacy,'source_input',lambda _:deepcopy(src));monkeypatch.setattr(r,'source_snapshot',lambda _:dict(src['source_sha256']));monkeypatch.setattr(a,'validate_mesh',lambda *args:dict(fixture_only=True));monkeypatch.setattr(a,'validate_scalar_coverage',lambda *args:[dict(artifact_guard_fixture_only=True)])
    output=tmp_path/'run';output.mkdir();case=output/'coarse';case.mkdir();boxes=fields(case);getdp=tmp_path/'getdp';getdp.write_text('fixture binary identity only')
    request=dict(schema=r.SCHEMA,source=src,source_sha256=dict(src['source_sha256']),getdp=dict(path=str(getdp),sha256=r.file_hash(getdp)),cases=['coarse'],case_settings={'coarse':r.PLAN['coarse']},contours_m=boxes,root=str(root),budget=dict(seconds_per_case=300,numerical_workers=1,max_cases=3),temperature_C=80.,currents_A={},frame=dict(x='travel',y='left',z='up',handedness='right',moment_origin_m=[0.,0.,0.]),**r.FLAGS);request['request_id']=r.identity(request)
    r.write(output/'request.json',request);r.write(output/'source-input.json',src);fixture=c.fixture(STEEL);r.write(output/'jacobian-fixture.json',fixture);(case/'coupon.msh').write_text('fixture mesh; geometry tested separately');(case/'coupon.pro').write_text(formulation(src['value'],mesh(),boxes));(case/'getdp.stdout.log').write_text(stages());(case/'getdp.stderr.log').write_text('')
    r.write(case/'source-input.json',src);record=dict(case='coarse',settings=r.PLAN['coarse'],request_id=request['request_id'],candidate_id=a.VEHICLE_ID,magnet_component_id=a.COMPONENT_ID,mesh=mesh(),solver_returncode=0,execution_status='completed',force_credit=True,full_source_converged=True);r.write(case/'calculation.json',record);execution=dict(command=['fixture'],returncode=0,timed_out=False,elapsed_s=1.);r.write(case/'execution.json',execution)
    row=r._derived(case,request,'coarse');row.update(execution=execution,files_sha256=r.inventory(case));result=dict(schema=r.SCHEMA,request_id=request['request_id'],candidate_id=a.VEHICLE_ID,magnet_component_id=a.COMPONENT_ID,execution_status='completed',rows=[row],comparisons=a.comparisons([row]),jacobian_fixture=fixture,**r.FLAGS);r.write(output/'result.json',result);manifest=dict(schema=r.SCHEMA,request_id=request['request_id'],source_sha256=dict(src['source_sha256']),files_sha256=r.inventory(output),**r.FLAGS);r.write(output/'manifest.json',manifest)
    return output,root


def rehash(output):
    result=json.loads((output/'result.json').read_bytes())
    for row in result['rows']:row['files_sha256']=r.inventory(output/row['case'])
    (output/'result.json').write_bytes(r.encoded(result));manifest=json.loads((output/'manifest.json').read_bytes());manifest['files_sha256']=r.inventory(output,exclude=('manifest.json',));(output/'manifest.json').write_bytes(r.encoded(manifest))


def test_reader_reproduces_stages_force_and_immutable_inventory(packet):
    output,root=packet;assert r.verify(output,root=root)['full_source_cases']==1
    with pytest.raises(Exception):r.write(output/'result.json',dict(changed=True))


@pytest.mark.parametrize('damage',['force','candidate','source','flag','contour','extra-file'])
def test_rehashed_semantic_or_scope_tamper_is_refused(packet,damage):
    output,root=packet;p=output/'result.json';result=json.loads(p.read_bytes())
    if damage=='force':result['rows'][0]['analysis']['air_contour_results'][0]['force_N'][2]=1234.
    elif damage=='candidate':result['candidate_id']='b'*64
    elif damage=='source':
        request=json.loads((output/'request.json').read_bytes());request['source_sha256']['fixture-data.json']='b'*64;request['request_id']=r.identity({k:v for k,v in request.items() if k!='request_id'});(output/'request.json').write_bytes(r.encoded(request))
    elif damage=='flag':result['physical_accepted']=True
    elif damage=='contour':
        path=output/'coarse/face-0-0-0.txt';data=np.loadtxt(path);data[0,0]+=.001;np.savetxt(path,data)
    else:(output/'unlisted.txt').write_text('tamper')
    p.write_bytes(r.encoded(result))
    if damage!='extra-file':rehash(output)
    with pytest.raises(ValueError):r.verify(output,root=root)


def test_actual_mesh_metadata_and_material_group_guards(tmp_path):
    pytest.importorskip('gmsh')
    value=source()['value'];record=r.legacy.mesh_case(value,tmp_path,margin=.15,h=.08,gap_h=.02)
    checked=a.validate_mesh(tmp_path/'coupon.msh',record,value,.15)
    assert checked['tetrahedra']==record['tetrahedra'] and set(checked['physical_tetrahedra'])=={*[str(k) for k in record['physical_pm']],'200','300'}
    changed=deepcopy(record);changed['physical_pm']=[101]
    with pytest.raises(ValueError,match='physical regions'):a.validate_mesh(tmp_path/'coupon.msh',changed,value,.15)
    changed=deepcopy(record);changed['outer_box_m'][0]+=.01
    with pytest.raises(ValueError,match='air-box'):a.validate_mesh(tmp_path/'coupon.msh',changed,value,.15)
    changed=deepcopy(record);changed['nodes']+=1
    with pytest.raises(ValueError,match='node count'):a.validate_mesh(tmp_path/'coupon.msh',changed,value,.15)


def test_rehashed_fixed_temperature_cannot_relabel_eighty_degree_solve(packet):
    output,root=packet;p=output/'request.json';request=json.loads(p.read_bytes());request['temperature_C']=20.;request['request_id']=r.identity({k:v for k,v in request.items() if k!='request_id'});p.write_bytes(r.encoded(request));rehash(output)
    with pytest.raises(ValueError,match='operating point'):r.verify(output,root=root)


def test_case_source_copy_must_match_bound_physical_input(packet):
    output,root=packet;p=output/'coarse/source-input.json';source_data=json.loads(p.read_bytes());source_data['value']['physical_id']='c'*64;p.write_bytes(r.encoded(source_data));rehash(output)
    with pytest.raises(ValueError,match='physical input'):r.verify(output,root=root)


def test_failed_or_interrupted_collection_retains_no_force_credit(packet):
    output,root=packet;p=output/'result.json';result=json.loads(p.read_bytes());case=output/'coarse';execution=dict(command=['fixture'],returncode=-9,timed_out=True,elapsed_s=300.)
    (case/'execution.json').write_bytes(r.encoded(execution));result['rows']=[dict(case='coarse',execution_status='interrupted',force_credit=False,full_source_converged=False,error='Case wall-clock deadline',execution=execution,files_sha256=r.inventory(case))];result['comparisons']=a.comparisons(result['rows']);p.write_bytes(r.encoded(result));rehash(output)
    assert r.verify(output,root=root)['full_source_cases']==0
    result=json.loads(p.read_bytes());result['rows'][0]['force_credit']=True;p.write_bytes(r.encoded(result));rehash(output)
    with pytest.raises(ValueError,match='force credit'):r.verify(output,root=root)


def test_publication_archives_verified_exact_artifacts_with_common_manifest(packet,tmp_path):
    import tarfile
    output,root=packet;public=tmp_path/'public';manifest=r.publish(public,run_dir=output,root=root)
    assert manifest['physical_accepted'] is False and manifest['source_sha256']==source()['source_sha256']
    assert manifest['files_sha256']==r.inventory(public,exclude=('manifest.json',))
    with tarfile.open(public/'artifacts.tar.gz','r:gz') as archive:
        assert all(x.isfile() and x.name.startswith('run/') and '..' not in Path(x.name).parts for x in archive.getmembers())
    assert 'No complete force map' in (public/'README.md').read_text()


def test_deadline_cleanup_kills_worker_and_ignoring_descendant(tmp_path):
    import os,subprocess,time
    if os.name!='posix':pytest.skip('POSIX process-group resource guard')
    target=tmp_path/'descendant.pid';code='import subprocess,sys,time;from pathlib import Path;p=subprocess.Popen([sys.executable,"-c","import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(60)"]);Path(sys.argv[1]).write_text(str(p.pid));time.sleep(60)';process=subprocess.Popen([sys.executable,'-c',code,str(target)],start_new_session=True)
    try:
        deadline=time.monotonic()+3
        while not target.exists() and time.monotonic()<deadline:time.sleep(.01)
        assert target.exists();descendant=int(target.read_text());r._terminate(process)
        deadline=time.monotonic()+2
        while time.monotonic()<deadline:
            p=Path('/proc')/str(descendant)/'stat'
            if not p.exists() or p.read_text().split()[2] in ('Z','X'):break
            time.sleep(.01)
        else:pytest.fail('Numerical descendant survived case deadline')
    finally:
        if process.poll() is None:r._terminate(process)


@pytest.mark.parametrize('damage',['Br','steel','mass'])
def test_rehashed_full_bundle_with_unchanged_claimed_ids_is_refused(damage):
    src=source();value=src['value']
    if damage=='Br':value['materials'][value['grade_id']]['br_20c_t']+=.01
    elif damage=='steel':value['materials']['steel']['j_t'][1]+=.005
    else:value['stock_parts'][0]['mass_kg']+=1.
    raw=deepcopy(value);raw.pop('bundle_sha256');value['bundle_sha256']=a.magnets.identity(raw)
    with pytest.raises(ValueError):a.validate_source(src)


def test_scalar_tables_require_every_physical_element_and_no_foreign_samples(tmp_path):
    pytest.importorskip('gmsh');value=source()['value'];record=r.legacy.mesh_case(value,tmp_path,margin=.15,h=.08,gap_h=.02);centroids=a.tetra_centroids(tmp_path/'coupon.msh',[*record['physical_pm'],200]);pm=np.vstack([centroids[group] for group in record['physical_pm']]);steel=centroids[200];pm_data=np.column_stack([pm,np.full(len(pm),-500000.)]);steel_data=np.column_stack([steel,np.full(len(steel),1.2)])
    np.savetxt(tmp_path/'PM-H.txt',pm_data);np.savetxt(tmp_path/'steel-B.txt',steel_data);assert len(a.validate_scalar_coverage(tmp_path,record))==2
    np.savetxt(tmp_path/'PM-H.txt',pm_data[:-1])
    with pytest.raises(ValueError,match='coverage/count'):a.validate_scalar_coverage(tmp_path,record)
    pm_data[0,0]+=.01;np.savetxt(tmp_path/'PM-H.txt',pm_data)
    with pytest.raises(ValueError,match='centroids'):a.validate_scalar_coverage(tmp_path,record)
