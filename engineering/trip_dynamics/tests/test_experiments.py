from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path

import pytest

from engineering.trip_dynamics import experiments as e


@pytest.fixture(scope='module')
def retained_root():
    root=Path(os.environ.get('OSR_SOURCE_ROOT',e.ROOT))
    if not (root/'docs/design-engine/vehicle-optimisation/summary.json').is_file():
        pytest.skip('set OSR_SOURCE_ROOT for sparse checkout retained inputs')
    return root


@pytest.fixture(scope='module')
def catalogue(retained_root):
    return e.catalogue(retained_root)


@pytest.mark.parametrize('job_request',[
    {}, {'action':'experiment','parameters':{},'output':'/tmp/escape'},
    {'action':'shell','parameters':{}}, {'action':[],'parameters':{}},
    {'action':'experiment','parameters':{'max_speed_m_s':100}},
    {'action':'experiment','parameters':{'mode':'exploration'}},
    {'action':'experiment','parameters':{'distance_m':0}},
    {'action':'experiment','parameters':{'temperature_C':40}},
    {'action':'experiment','parameters':{'mechanical_step_s':.01}},
    {'action':'experiment','parameters':{'load_case':'asymmetric'}},
    {'action':'experiment','parameters':{'distance_m':True}},
    {'action':'fixture','parameters':{'fixture':'Code_Aster'}},
    {'action':'verify','parameters':{'path':'/etc/passwd'}},
    {'action':'validate-modal','parameters':{'model_file':'/etc/passwd'}},
    {'action':'validate-map','parameters':{'model_data':{},'vehicle_id':None}},
])
def test_untrusted_parameters_reject_before_output_creation(tmp_path,job_request):
    with pytest.raises((ValueError,TypeError)):
        e.execute(job_request,tmp_path/'never',tmp_path/'not-a-source-repo')
    assert not (tmp_path/'never').exists()


def test_catalogue_preserves_selected_mass_scope_and_material_options(catalogue):
    assert len(catalogue['vehicles'])==5
    rows=catalogue['vehicles']
    assert rows[0]['comparison_aw3_kg_per_car']==pytest.approx(37618.5915003343)
    assert {x['body_family']for x in rows[1:]}=={'retained-frame','6061-T6-envelope',
        '6082-T6-deep-stringers','6005A-T5-wide-stringers'}
    assert catalogue['requested_gfrp_optimisation']['status']=='unknown'
    assert catalogue['fixed_targets']['target_is_candidate_performance'] is False
    for row in rows:
        if row['comparison_aw3_mass_band_kg']:
            assert row['comparison_aw3_kg_per_car']==max(row['comparison_aw3_mass_band_kg'])
        assert row['installed_empty_kg_per_car'] is None
        assert row['cg_m'] is None and row['inertia_kg_m2'] is None
        assert row['physical_accepted'] is False


def test_actual_evidence_selected_variant_uses_own_upper_band_and_no_fallback(tmp_path,retained_root,catalogue,monkeypatch):
    chosen=catalogue['vehicles'][1]
    def no_native(*a,**kw):raise AssertionError('evidence must never run ideal Chrono')
    monkeypatch.setattr(e,'_benchmark',no_native)
    result=e.execute({'action':'experiment','parameters':dict(mode='evidence',vehicle_id=chosen['vehicle_id'],
        distance_m=1500,load_case='empty',temperature_C=50,mechanical_step_s=.0005)},tmp_path/'job',retained_root)
    assert result['execution_status']=='refused'
    assert result['vehicle_id']==chosen['vehicle_id']==result['scenario']['candidate_id']
    assert result['scenario_id']!=result['vehicle_id']
    assert result['comparison_mass_context']['AW3_kg_per_car']==pytest.approx(28066.715270147215)
    assert result['result']['kinematic_target']['total_comparison_mass_kg']==pytest.approx(6*(28066.715270147215-12000))
    assert result['result']['dynamic_execution']=='not-run'
    assert result['result']['distance_travelled_m']==0
    assert all(v['status']=='unevaluated' and v['value'] is None for v in result['result']['requested_outputs'].values())
    assert not (tmp_path/'job/trace.png').exists()
    for item in result['outputs']:
        assert sha256((tmp_path/'job'/item['path']).read_bytes()).hexdigest()==item['sha256']


@pytest.mark.parametrize('identifier',['unknown','', 'f'*64])
def test_unknown_vehicle_does_not_fall_back_to_canonical(tmp_path,retained_root,identifier):
    with pytest.raises(ValueError,match='catalogue'):
        e.execute({'action':'experiment','parameters':{'vehicle_id':identifier}},tmp_path/'job',retained_root)
    assert not (tmp_path/'job').exists()


def test_modal_upload_reports_missing_equipped_properties_without_following_sources(tmp_path,retained_root,catalogue):
    secret=tmp_path/'unread-source';secret.write_text('not part of uploaded model')
    data={'source_sha256':{str(secret):'0'*64}}
    result=e.execute({'action':'validate-modal','parameters':{
        'vehicle_id':catalogue['canonical_vehicle_id'],'model_data':data}},tmp_path/'job',retained_root)
    assert result['execution_status']=='refused'
    assert 'equipped load-case mass/CG/inertia is unknown' in result['result']['reason']
    assert not result['result']['accepted_for_dynamics']
    assert not (tmp_path/'job/unread-source').exists()


def test_synthetic_and_foreign_maps_never_get_candidate_credit(tmp_path,retained_root,catalogue):
    from engineering.trip_dynamics.tests.test_magnetic_maps import fixture,reseal
    value=fixture()
    request={'action':'validate-map','parameters':{'vehicle_id':catalogue['canonical_vehicle_id'],'model_data':value}}
    result=e.execute(request,tmp_path/'foreign',retained_root)
    assert result['execution_status']=='refused' and 'identity mismatch' in result['result']['reason']
    value['identity']['candidate_id']=catalogue['canonical_vehicle_id']
    for row in value['rows']:row['identity']=deepcopy(value['identity'])
    request['parameters']['model_data']=reseal(value)
    result=e.execute(request,tmp_path/'synthetic',retained_root)
    assert result['execution_status']=='refused' and 'synthetic/manufactured' in result['result']['reason']
    assert not result['result']['accepted_for_dynamics']


def test_unavailable_native_benchmark_fails_without_substitute(tmp_path,retained_root,monkeypatch):
    monkeypatch.setattr(e,'_probe_chrono',lambda root:dict(available=False,reason='test missing native environment',fallback=False))
    result=e.execute({'action':'experiment','parameters':{'mode':'benchmark'}},tmp_path/'job',retained_root)
    assert result['execution_status']=='failed'
    assert 'missing native' in result['result']['reason']
    assert not result['physical_accepted'] and not (tmp_path/'job/trace.png').exists()


def test_laminate_fixture_executes_analytical_not_code_aster(tmp_path,retained_root):
    result=e.execute({'action':'fixture','parameters':{'fixture':'laminate'}},tmp_path/'job',retained_root)
    assert result['execution_status']=='completed'
    assert result['result']['executed'] and not result['result']['code_aster_executed']
    assert not result['result']['engineering_accepted']


def test_existing_job_and_symlink_output_refused(tmp_path,retained_root):
    (tmp_path/'used').mkdir();(tmp_path/'used/kept').write_text('retained')
    (tmp_path/'alias').symlink_to(tmp_path/'used',target_is_directory=True)
    for path in [tmp_path/'used',tmp_path/'alias']:
        with pytest.raises(ValueError,match='fresh|ordinary'):
            e.execute({'action':'probe','parameters':{}},path,retained_root)
    assert (tmp_path/'used/kept').read_text()=='retained'


def test_setup_uses_fixed_private_tools_with_per_job_logs_and_existing_chrono(tmp_path,retained_root,monkeypatch):
    from engineering.trip_dynamics import setup_tools
    destinations=[]
    def install(path):
        destinations.append(path)
        return dict(global_environment_modified=False,micromamba='pinned-private-mamba')
    monkeypatch.setattr(setup_tools,'install',install)
    calls=[]
    def ensure(root,micromamba,logs):
        calls.append((root,micromamba,logs))
        return dict(created=False,reused=True)
    monkeypatch.setattr(setup_tools,'ensure_chrono',ensure)
    monkeypatch.setattr(e,'_probe_chrono',lambda root:dict(available=True,fallback=False,solver_id='a'*64))
    result=e.execute({'action':'setup-tools','parameters':{}},tmp_path/'job',retained_root)
    assert destinations==[retained_root/'build/trip-dynamics/tools']
    assert calls==[(retained_root,'pinned-private-mamba',tmp_path/'job')]
    assert result['result']['global_environment_modified'] is False
    assert result['result']['chrono_environment_installed'] is False
    assert result['result']['existing_private_chrono']['available'] is True


def _tiny_locked_root(root):
    folder=root/'engineering/trip_dynamics';folder.mkdir(parents=True)
    packages=[]
    for name in ('python','pychrono'):
        url='https://conda.anaconda.org/'+('projectchrono' if name=='pychrono' else 'conda-forge')+'/linux-64/'+name+'-1.0-test.conda'
        packages.append(dict(name=name,version='1.0',build='test',url=url,sha256=sha256(name.encode()).hexdigest(),md5='a'*32))
    (folder/'solver-environment.json').write_text(json.dumps({'packages':packages}))
    (folder/'environment-linux-64.lock').write_text('@EXPLICIT\n'+'\n'.join(x['url']+'#'+x['md5']for x in packages)+'\n')
    return packages


def _tiny_environment(root,packages):
    prefix=root/'build/trip-dynamics/environment/chrono'
    metadata=prefix/'conda-meta';metadata.mkdir(parents=True)
    for package in packages:
        relative='bin/python3.12' if package['name']=='python' else 'lib/python3.12/site-packages/pychrono/_core.so'
        data=package['name'].encode();path=prefix/relative;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        row={**package,'paths_data':{'paths':[dict(_path=relative,sha256_in_prefix=sha256(data).hexdigest())]}}
        (metadata/(package['name']+'.json')).write_text(json.dumps(row))
    (prefix/'bin/python').write_bytes(b'python');(prefix/'bin/python').chmod(0o755)
    return prefix


def test_locked_chrono_create_uses_exact_explicit_file_private_prefix_and_no_user_config(tmp_path,monkeypatch):
    from engineering.trip_dynamics import setup_tools as tools
    packages=_tiny_locked_root(tmp_path)
    mamba=tmp_path/'micromamba';mamba.write_text('test executable');mamba.chmod(0o755)
    calls=[]
    def run(command,**kwargs):
        calls.append((command,kwargs));_tiny_environment(tmp_path,packages)
        kwargs['stdout'].write(b'mocked package manager test only\n')
        return type('Process',(),{'returncode':0})()
    monkeypatch.setattr(tools.subprocess,'run',run)
    monkeypatch.setenv('CONDA_PREFIX','do-not-use-user-prefix')
    monkeypatch.setenv('MAMBA_ROOT_PREFIX','do-not-use-user-root')
    result=tools.ensure_chrono(tmp_path,mamba,tmp_path/'job')
    command,settings=calls[0]
    assert command==[str(mamba),'create','--no-rc','--no-env','--root-prefix',
        str(tmp_path/'build/trip-dynamics/environment/mamba-root'),'--prefix',
        str(tmp_path/'build/trip-dynamics/environment/chrono'),'--file',
        str(tmp_path/'engineering/trip_dynamics/environment-linux-64.lock'),'--yes']
    assert settings['timeout']==1000
    assert not any(k.startswith(('CONDA_','MAMBA_'))for k in settings['env'])
    assert result['created'] and not result['reused'] and result['package_count']==2
    assert not result['global_environment_modified'] and not result['code_aster_installed']
    assert (tmp_path/'job/chrono-setup-stdout.txt').read_bytes().startswith(b'mocked')


def test_matching_locked_environment_reused_without_package_manager_or_rewrites(tmp_path,monkeypatch):
    from engineering.trip_dynamics import setup_tools as tools
    packages=_tiny_locked_root(tmp_path);prefix=_tiny_environment(tmp_path,packages)
    before={p.relative_to(prefix).as_posix():(p.read_bytes(),p.stat().st_mtime_ns)for p in prefix.rglob('*')if p.is_file()}
    def no_create(*a,**kw):raise AssertionError('matching environment must not execute package manager')
    monkeypatch.setattr(tools.subprocess,'run',no_create)
    result=tools.ensure_chrono(tmp_path,tmp_path/'unused-mamba',tmp_path/'logs')
    after={p.relative_to(prefix).as_posix():(p.read_bytes(),p.stat().st_mtime_ns)for p in prefix.rglob('*')if p.is_file()}
    assert before==after and result['reused'] and not result['created']
    assert not (tmp_path/'logs').exists()


@pytest.mark.parametrize('corruption',['package','runtime','partial'])
def test_existing_mismatch_is_preserved_not_removed_or_repaired(tmp_path,monkeypatch,corruption):
    from engineering.trip_dynamics import setup_tools as tools
    packages=_tiny_locked_root(tmp_path);prefix=_tiny_environment(tmp_path,packages)
    if corruption=='package':
        path=prefix/'conda-meta/python.json';row=json.loads(path.read_text());row['version']='foreign';path.write_text(json.dumps(row))
    if corruption=='runtime':(prefix/'bin/python3.12').write_bytes(b'foreign interpreter')
    if corruption=='partial':(prefix/'conda-meta/python.json').unlink()
    before={p.relative_to(prefix).as_posix():p.read_bytes()for p in prefix.rglob('*')if p.is_file()}
    monkeypatch.setattr(tools.subprocess,'run',lambda *a,**kw:pytest.fail('must not install into mismatched environment'))
    with pytest.raises(ValueError,match='differ'):
        tools.ensure_chrono(tmp_path,tmp_path/'unused-mamba',tmp_path/'logs')
    assert before=={p.relative_to(prefix).as_posix():p.read_bytes()for p in prefix.rglob('*')if p.is_file()}


def test_explicit_lock_must_agree_with_sha256_package_pins(tmp_path):
    from engineering.trip_dynamics import setup_tools as tools
    _tiny_locked_root(tmp_path)
    lock=tmp_path/'engineering/trip_dynamics/environment-linux-64.lock'
    lock.write_text(lock.read_text().replace('#'+'a'*32,'#'+'f'*32,1))
    with pytest.raises(ValueError,match='disagrees'):
        tools.ensure_chrono(tmp_path,tmp_path/'unused-mamba',tmp_path/'logs')
    assert not (tmp_path/'build').exists()


def test_private_tool_install_reuses_exact_executable_and_refuses_mismatch(tmp_path,monkeypatch):
    import io,tarfile
    from engineering.trip_dynamics import setup_tools as tools
    source=tmp_path/'source';source.mkdir();out=tmp_path/'tools';out.mkdir()
    pins={}
    for key,name,member in [('getdp','getdp-3.5.0-Linux64c.tgz','getdp-3.5.0-Linux64/bin/getdp'),
                            ('micromamba','micromamba-2.9.0-0.tar.bz2','bin/micromamba')]:
        path=out/name;data=('pinned-'+key).encode()
        with tarfile.open(path,'w:gz' if key=='getdp' else 'w:bz2') as archive:
            info=tarfile.TarInfo(member);info.size=len(data);info.mode=0o755;archive.addfile(info,io.BytesIO(data))
        pins[key]=dict(bytes=path.stat().st_size,sha256=sha256(path.read_bytes()).hexdigest(),url='https://example.invalid/not-used')
    (source/'solver-environment.json').write_text(json.dumps(pins));monkeypatch.setattr(tools,'__file__',str(source/'setup_tools.py'))
    tools.install(out)
    binary=out/'getdp-3.5.0-Linux64/bin/getdp';before=(binary.read_bytes(),binary.stat().st_mtime_ns)
    (out/'micromamba-2.9.0-0.tar.bz2').rename(out/'micromamba-pinned.tar.bz2')
    monkeypatch.setattr(tools.urllib.request,'urlopen',lambda *a,**kw:pytest.fail('matching retained pinned archive must reuse offline'))
    tools.install(out);assert before==(binary.read_bytes(),binary.stat().st_mtime_ns)
    binary.write_bytes(b'foreign binary')
    with pytest.raises(ValueError,match='leaving it unchanged'):tools.install(out)
    assert binary.read_bytes()==b'foreign binary'
