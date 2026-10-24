"""Bounded portable research-byte verification; optional selected coupon replay."""
from hashlib import sha256
from pathlib import Path,PurePosixPath
import argparse,json,math,os,shutil,stat,subprocess,sys,tempfile,tomllib

BASE=Path(__file__).resolve().parent
MAX_FILE=16*1024*1024
MAX_TOTAL=64*1024*1024
FLAGS=('design_complete','physical_validation','manufacturing_release','physical_release','canonical_adoption')


def canonical(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
def digest(value):return sha256(value).hexdigest()
def safe(name):
    if not isinstance(name,str):raise ValueError('archive relative string path required')
    p=PurePosixPath(name)
    if not name or p.is_absolute() or '..' in p.parts or p.as_posix()!=name:raise ValueError('safe canonical archive path required')
    return p

def ordinary(root,name):
    p=root/safe(name)
    for node in [p,*p.parents]:
        if node==root.parent:break
        st=node.lstat()
        if stat.S_ISLNK(st.st_mode):raise ValueError('archive symlink or symlink ancestor refused')
    st=p.lstat()
    if not stat.S_ISREG(st.st_mode) or st.st_size>MAX_FILE:raise ValueError('bounded ordinary archive file required')
    with p.open('rb') as stream:data=stream.read(MAX_FILE+1)
    if len(data)!=st.st_size or len(data)>MAX_FILE:raise ValueError('archive file size changed or exceeded bound')
    return data

def read(name):return json.loads(ordinary(BASE,name))
def unreleased(value):
    if any(value.get(k)is not False for k in FLAGS):raise ValueError('isolated research cannot claim release or adoption')

def inventory():
    found=set()
    for root,dirs,files in os.walk(BASE,followlinks=False):
        for name in dirs:
            if (Path(root)/name).is_symlink():raise ValueError('archive symlink directory refused')
        for name in files:
            p=Path(root)/name
            if not stat.S_ISREG(p.lstat().st_mode):raise ValueError('archive nonregular file refused')
            found.add(p.relative_to(BASE).as_posix())
    return found


def verify(check_current_sources=False,replay=False):
    receipt=read('archive-receipt.json');unreleased(receipt)
    if receipt['schema']!='osr-propulsion-redesign-archive/1':raise ValueError('archive receipt schema differs')
    expected=receipt['files_sha256']
    if inventory()!=set(expected)|{'archive-receipt.json'}:raise ValueError('exact archive file inventory differs')
    total=0
    for name,h in expected.items():
        data=ordinary(BASE,name);total+=len(data)
        if total>MAX_TOTAL or not isinstance(h,str) or len(h)!=64 or digest(data)!=h:raise ValueError('bounded archive hash inventory differs')
    original=read('executed/manifest.json');result=read('executed/results.json')
    if digest(ordinary(BASE,'executed/manifest.json'))!=receipt['original_manifest_sha256']:raise ValueError('original executed manifest differs')
    if set(receipt['executed_file_mapping'])!=set(original['files_sha256']):raise ValueError('all original executed files must be mapped')
    for name,h in original['files_sha256'].items():
        safe(name)
        if digest(ordinary(BASE,receipt['executed_file_mapping'][name]))!=h:raise ValueError('original executed file is not byte identical')
    if receipt['original_execution_directory']!='build/propulsion-redesign-screen' or receipt['original_working_directory']!='/home/hayder/Documents/OpenSourceRail':raise ValueError('accurate original execution locations required')
    if set(receipt['source_archive_mapping'])!=set(original['source_sha256']):raise ValueError('all original source files must be archived')
    for name,h in original['source_sha256'].items():
        safe(name)
        if digest(ordinary(BASE,receipt['source_archive_mapping'][name]))!=h:raise ValueError('archived source input differs')
        if check_current_sources and digest(ordinary(BASE.parents[2],name))!=h:raise ValueError('current source differs from original archive input')
    unreleased(original);unreleased(result)
    if not original['production_sources_unchanged'] or not result['production_sources_unchanged'] or result['source_sha256']!=original['source_sha256']:raise ValueError('original execution source closure differs')
    if receipt['parent_configuration_sha256']!=result['parent_configuration_sha256']:raise ValueError('parent candidate identity differs')
    for row in result['rows']:
        unreleased(row)
        if row['source_sha256']!=original['source_sha256'] or not row['source_unchanged']:raise ValueError('coupon source evidence differs')
        values=read('executed/inputs/'+row['id']+'.json')
        if digest(canonical(values))!=row['input_sha256']:raise ValueError('actual coupon input identity differs')
        hypothesis=digest(canonical(dict(schema='osr-exploratory-propulsion-hypothesis/1',parent=result['parent_configuration_sha256'],input=values,source_sha256=original['source_sha256'])))
        if hypothesis!=row['hypothesis_sha256'] or row!=read('executed/raw/'+row['id']+'.json'):raise ValueError('changed hypothesis or raw coupon differs')
        if 'physical_corner_alternative' in row:
            q=values['propulsion_flux_shoe'];volume=2*q['corner_chamfer_m']**2*q['height_m']*4*q['length_m']/q['period_m'];p=row['physical_corner_alternative']
            if not math.isclose(volume,p['analytic_removed_pm_volume_m3'],rel_tol=1e-14) or not math.isclose(volume*values['materials']['ferrite']['density_kg_m3'],p['analytic_removed_pm_mass_kg'],rel_tol=1e-14):raise ValueError('physical corner scalar volume differs')
    known=next(r for r in result['rows'] if r['id']=='selected-256x48-cold')
    if known['material_current_screen_pass']is not False or known['demag_margin_after_declared_current_bound_a_m']>=0 or result['operating']['geometry_eligible_over_all_retained_sampled_coupons']is not False:raise ValueError('known finer failure must supersede older positive estimates')
    if result['resolved_corner_alternative']['independent_grid_peak_convergence_established']is not False or result['resolved_corner_operating']['full_temperature_range_accepted']is not False:raise ValueError('unresolved numerical/material scope must remain held')
    comparison=read('acceleration-comparison.json')
    mass=comparison['current_candidate_aw3_mass_kg_per_car'];force=comparison['conditional_force_n_per_car']
    boundary=read('executed/current-boundary-diagnostic.json');actual=next(r for r in boundary['rows'] if r['requested_q_current_a']==1349.)
    if actual['accepted_for_conditional_numerical_map']is not True or force!=actual['force_x_n_per_car'] or comparison['new_hypothesis_mass_reconciled']is not False:raise ValueError('conditional force or unreconciled mass scope differs')
    if comparison['ideal_acceleration_upper_bound_m_s2']!=force/mass:raise ValueError('ideal acceleration arithmetic differs')
    contexts={name:tomllib.loads(ordinary(BASE,mapped).decode()) for name,mapped in receipt['comparison_context_mapping'].items()}
    for row in comparison['contexts']:
        if row['source_path'] is not None:
            value=contexts[row['source_path']]
            for key in row['key_path']:value=value[key]
            if row['acceleration_m_s2']!=value:raise ValueError('exact acceleration context differs')
        if row['inertial_force_required_n_per_car']!=mass*row['acceleration_m_s2'] or row['ideal_force_margin_n_per_car']!=force-row['inertial_force_required_n_per_car']:raise ValueError('required-force comparison differs')
    if comparison['launch_profile_feasible']is not False or comparison['configuration_adopted']is not False:raise ValueError('coupon arithmetic is not launch or design acceptance')
    answer=dict(archive_inventory_verified=True,executed_files_byte_identical=True,files=len(expected),source_files=len(original['source_sha256']),executed_coupons=sum(x['state']=='executed' for x in result['rows']),unknown_refused_requests=sum(x['state']!='executed' for x in result['rows']),current_sources_checked=check_current_sources,configuration_adopted=False,physical_validation=False)
    if replay:
        with tempfile.TemporaryDirectory(prefix='osr-propulsion-coupon-replay-') as temporary:
            root=Path(temporary)
            for name,mapped in receipt['source_archive_mapping'].items():
                target=root/safe(name);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(ordinary(BASE,mapped))
            work=root/receipt['original_execution_directory'];work.mkdir(parents=True,exist_ok=True)
            (work/'run.py').write_bytes(ordinary(BASE,'executed/run.py'))
            driver=work/'replay-selected.py';driver.write_bytes(ordinary(BASE,'replay-selected.py'))
            env=dict(os.environ,PYTHONPATH=str(root),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
            completed=subprocess.run([sys.executable,str(driver),str(BASE)],cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=True,timeout=240)
            fresh=json.loads(ordinary(work,'replay-selected-results.json'))
            if fresh['source_sha256']!=original['source_sha256'] or fresh['parent_configuration_sha256']!=receipt['parent_configuration_sha256'] or fresh['current_candidate_aw3_mass_kg_per_car']!=mass:raise ValueError('portable selected replay candidate/source/mass differs')
            if fresh!=read('selected-replay-receipt.json'):raise ValueError('selected replay numerical identity or external runtime differs from retained replay receipt')
            answer.update(portable_selected_replay_verified=True,replayed_coupons=len(fresh['cases']),complete_coupon_and_identity_exact_match=True,ignored_numerical_field='elapsed_host_s only',external_runtime={k:fresh[k] for k in ('python_version','numpy_version','scipy_version')})
    return answer


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check-current-sources',action='store_true');parser.add_argument('--replay',action='store_true');args=parser.parse_args()
    print(json.dumps(verify(args.check_current_sources,args.replay),sort_keys=True))
