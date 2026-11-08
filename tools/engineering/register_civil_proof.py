from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import json,hashlib,shutil,gzip,tarfile,io,re
from engineering.station_rail.common import identity,encoded,digest
from engineering.design_search.craft_backends import native
import argparse
parser=argparse.ArgumentParser(description='Package an existing exact-load civil experiment; never execute solvers or alter receipts.')
parser.add_argument('--run',type=Path,required=True);parser.add_argument('--prefix',required=True)
args=parser.parse_args()
if Path(args.prefix).name!=args.prefix or '..' in args.prefix:raise ValueError('Ordinary proof basename required')
run=args.run.resolve();base=run.parent;proof=base/(args.prefix+'-compact');proof.mkdir()
root=Path(__file__).resolve().parents[2];upstream=root
report=json.loads((run/'report.json').read_bytes());before=json.loads((run/'source-before.json').read_bytes());train=json.loads((run/'axle-input.json').read_bytes());omissions={}
for f in run.rglob('*'):
 if not f.is_file():continue
 rel=f.relative_to(run);name=str(rel);reason=None
 if name=='manifest.json':rel=Path('full-private-manifest.json')
 elif f.name in ('input.step','imported.json','imported.msh'):reason='Duplicate geometry/mesh representation; exact one STEP and sealed mesh.json retained; original SHA in full private manifest.'
 elif '.fieldcraft' in f.name:reason='Replaceable rolling scratch checkpoint or backup; recorded commands and native raw results retained.'
 elif '/calculix/' in name and f.name not in ('viaduct.dat','stdout.log','stderr.log','usage.json','invocation.json','execution.json'):reason='Replaceable native scratch/duplicate deck or alternative result representation; exact source deck and raw DAT retained.'
 elif any(p in ('config','cache','data','tmp') for p in rel.parts):reason='Private application scratch configuration/cache; input commands and tool/resource records retained.'
 if reason:
  omissions[name]=dict(reason=reason,sha256=digest(f),bytes=f.stat().st_size);continue
 dest=proof/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dest)
for kind,repo,values in [('numerical',root,before),('upstream',upstream,train['source_sha256'])]:
 for n,want in values.items():
  f=repo/n
  if digest(f)!=want:raise ValueError('Source drift before proof snapshot: '+n)
  dest=proof/'source'/kind/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dest)
(proof/'omissions.json').write_bytes(encoded(dict(schema='osr-pilot-civil-proof-omissions/1',full_private_run=str(run),members=omissions,physical_evidence_removed=False,reason='Full immutable private run retained separately; only duplicate/replaceable scratch omitted from compact copy.')))
version=json.loads((run/'independent-freecad/measurement.json').read_bytes());model=json.loads((run/'case-3/mesh.json').read_bytes())
tools=dict(schema='osr-pilot-civil-tools/1',solidcraft=native.pin('solidcraft'),fieldcraft=native.pin('fieldcraft'),gmsh_version=model['gmsh_version'],FreeCAD_version=version['FreeCAD_version'],OpenCASCADE_version=version['OpenCASCADE_version'],
 calculix=dict(version='2.23',executable='/usr/bin/ccx',sha256=digest('/usr/bin/ccx'),hash_observation='Measured after the successful runs; raw solver stdout records version. This system executable was not independently source-sandboxed or captured before execution.'),
 python=dict(version='3.13.16',scope='Numerical receipt; executable digests in each actual invocation.json'),
 resources=json.loads((run/'request.json').read_bytes())['resources'],filesystem='Recorded native Bubblewrap/Flatpak execution scope, single-thread request, process limits; not aggregate cgroup limits or OS-enforced immutability of the coordinator source.')
(proof/'tools-resources.json').write_bytes(encoded(tools))
(proof/'proof-readme.txt').write_text('''OpenSourceRail gauge-corrected final-load elastic method proof\n\nRun `python verify.py` after extracting this archive into a fresh directory.\nThe verifier uses only the Python standard library and performs no simulation.\nIt authenticates member bytes, sealed inputs/results/meshes, exact source snapshots,\nCAD volume, case identities, equilibrium, rotating support axes and refinement.\n\nFull numerical replay requires an OpenSourceRail checkout with the numerical\nsource snapshot and the pinned installed tools. The numerical source epoch is\nsource-before.json. Actual commands and resource limits are retained verbatim;\ncommands contain the original private absolute paths, so a relocated replay\nshould use engineering.pilot_civil.final_trial with a NEW --output directory.\nUse this package's axle-input.json and source/upstream as --upstream-root.\nInstall the exact declared toolchain/Gmsh/Python environment first. Never run\nthe original commands against the retained private output directories.\n\nThe original finite-patch model is retained separately; its recovered support\nwrenches in prior-support-audit.json identify unintended bending couples.\nThe final experiment uses explicit transverse bearing lines, which release\nlongitudinal bending rotation. Actual finite bearing contact/compliance, joint\nstrength, cracking, prestressing, fatigue and physical acceptance remain open.\nThis proof package supplies a converged elastic comparison for one exact\nnormal-base load case. It is not approval for manufacturing or operation.\n\nOnly replaceable rolling checkpoints, alternative scratch result formats, and\nduplicate STEP/mesh/deck representations are omitted here. omissions.json\nrecords their exact original hashes; full-private-manifest.json covers the\nseparately retained full private run.\n''')
(proof/'verify.py').write_text(r'''"""Authenticate compact evidence; no solvers or external files are executed."""
import hashlib,json,math
from pathlib import Path
P=Path(__file__).resolve().parent

def load(n):return json.loads((P/n).read_bytes())
def identity(v):return hashlib.sha256((json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()).hexdigest()
def sealed(v,key='evaluation_id'):
    assert v[key]==identity({k:x for k,x in v.items() if k!=key}), 'Seal differs: '+key
    return v

manifest=sealed(load('compact-members.json'))
for n,spec in manifest['members'].items():
    f=P/n
    assert f.is_file() and f.stat().st_size==spec['bytes'], 'Size/file differs: '+n
    assert hashlib.sha256(f.read_bytes()).hexdigest()==spec['sha256'], 'SHA differs: '+n
train=sealed(load('axle-input.json'));civil=sealed(load('civil.json'));spec=sealed(load('native-input.json'),'input_id');report=sealed(load('report.json'))
assert report['system_candidate_id']==train['candidate_id']==spec['system_candidate_id']==civil['system_candidate_id']
assert report['civil_candidate_id']==civil['civil_candidate_id']==spec['candidate_id']==identity(civil['physical_definition'])
assert report['civil_evaluation_id']==civil['evaluation_id']
assert report['input_load_evaluation_id']==train['evaluation_id']==spec['input_load_evaluation_id']==civil['input_load_evaluation_id']
assert report['native_input_id']==spec['input_id']
assert report['source_unchanged'] and report['upstream_source_unchanged']
interface=train['track_interface']
assert interface==civil['physical_definition']['rail_interface']['track_interface']==spec['track_interface']
assert interface['inner_face_gauge_m']==1.435 and interface['nominal_rail_head_width_m']==.07
assert interface['nominal_contact_centres_y_m']==[-.7525,.7525]
assert spec['rail_patch_hypothesis']['centres_y_m']==interface['nominal_contact_centres_y_m']
for kind,mapping in [('numerical',load('source-before.json')),('upstream',train['source_sha256'])]:
    for n,want in mapping.items():assert hashlib.sha256((P/'source'/kind/n).read_bytes()).hexdigest()==want, 'Source differs: '+n
for case in train['load_cases']:
    total=math.fsum(a['vertical_force_N'] for a in case['axles'])
    assert abs(total-case['train_mass_kg']*9.80665)<1e-7*total
step=P/'gross-beam-cad/execution/assembly.step'
assert hashlib.sha256(step.read_bytes()).hexdigest()==spec['cad_artifact']['step_sha256']
assert abs(load('independent-cad-summary.json')['total_volume_m3']-civil['quantities']['concrete_beam_m3'])<1e-6
results=[]
for i in (1,2,3):
    root='case-'+str(i)+'/';r=sealed(load(root+'result.json'));m=sealed(load(root+'mesh.json'),'mesh_id')
    assert r['candidate_id']==civil['civil_candidate_id'] and r['input_id']==spec['input_id']
    assert r['mesh_id']==m['mesh_id'] and len(m['elements'])<=50000
    assert r['cross_solver_screen_passed'] and r['cross_solver_relative_difference']<=.02
    assert r['support_audit']['rotation_free_line_definition_resolved']
    for row in r['support_audit']['rows']:
        assert row['node_x_range_m']==[row['axis_x_m'],row['axis_x_m']]
        assert abs(row['vertical_reaction_bending_couple_Nm'])<1e-6
    for tool in ('fieldcraft','calculix'):
        v=r[tool]
        assert v['force_equilibrium_passed'] and v['moment_equilibrium_passed']
        assert v['physical_accepted'] is False and v['engineering_accepted'] is False
    F=math.fsum(v[2] for v in m['nodal_load_N'].values())
    assert abs(F-m['applied_N'][2])<1e-8*abs(F)
    # Independent second-moment audit detects a symmetric wrong rail spacing
    # which total force and first lateral moment alone cannot detect.
    patch=spec['rail_patch_hypothesis'];centres=patch['centres_y_m']
    live=math.fsum(a['force_N'] for a in spec['live_pose']['points'])
    live_m2=-live*(math.fsum(y*y for y in centres)/2+patch['width_m']**2/12)
    line=spec['line_equipment_gravity'];line_m2=-line['mass_kg']*9.80665*(line['lateral_y_m']**2+line['spread_width_m']**2/12)
    calls=[json.loads(row) for row in (P/root/'fieldcraft/stdin.jsonl').read_text().splitlines()]
    cmds=[c for call in calls if call.get('method')=='tools/call' for c in call['params']['arguments'].get('commands',[])]
    forces={int(c['params']['name'][9:]):c['params']['vector'][2] for c in cmds if c['command']=='model.load.create' and c['params']['name'].startswith('PilotLoad')}
    actual_m2=math.fsum(m['nodes'][str(n)][1]**2*f for n,f in forces.items())
    assert abs(actual_m2-live_m2-line_m2)<1e-7*abs(live_m2+line_m2), 'FieldCraft actual lateral load second moment differs'
    body_m2=0.
    for e in m['elements'].values():
        points=[m['nodes'][str(n)] for n in e[:4]];a=points[0]
        b,c,d=[[v[j]-a[j] for j in range(3)] for v in points[1:]]
        volume=abs(b[0]*(c[1]*d[2]-c[2]*d[1])-b[1]*(c[0]*d[2]-c[2]*d[0])+b[2]*(c[0]*d[1]-c[1]*d[0]))/6
        ys=[v[1] for v in points]
        body_m2-=2500*9.80665*volume*(sum(ys)**2+sum(y*y for y in ys))/20
    reserve_m2=-(spec['superimposed_mass_kg']-line['mass_kg'])*9.80665/3
    actual_total=math.fsum(m['nodes'][str(n)][1]**2*v[2] for n,v in m['nodal_load_N'].items())
    assert abs(actual_total-(body_m2+reserve_m2+line_m2+live_m2))<1e-7*abs(actual_total), 'CalculiX assembled lateral load second moment differs'
    line=spec['line_equipment_gravity'];expected=-line['mass_kg']*9.80665*line['lateral_y_m']
    assert abs(m['applied_moment_Nm'][0]-expected)<1e-6*abs(expected), 'Conductor eccentric moment differs'
    for tool in ('mesh-native','fieldcraft','calculix'):
        usage=load(root+tool+'/usage.json')
        assert usage['exit']==0 and usage['peak_rss_kib']<=3072*1024
        if 'user_s' in usage:assert usage['user_s']+usage['system_s']<=75
    results.append(r)
for a,b in zip(results,results[1:]):
    u=a['fieldcraft']['displacement_m'][2];v=b['fieldcraft']['displacement_m'][2]
    assert abs(u-v)/abs(v)<=.05
assert report['refinement_screen_passed'] and report['physical_accepted'] is False
print(json.dumps(dict(status='verified',files=len(manifest['members']),system_candidate_id=train['candidate_id'],civil_candidate_id=civil['civil_candidate_id'],report_id=report['evaluation_id'],numerical_refinement_screen_passed=True,physical_accepted=False)))
''')
members={str(f.relative_to(proof)):dict(sha256=digest(f),bytes=f.stat().st_size) for f in sorted(proof.rglob('*')) if f.is_file()}
inner=dict(schema='osr-pilot-civil-compact-members/1',members=members);inner['evaluation_id']=identity(inner);(proof/'compact-members.json').write_bytes(encoded(inner))
archive=base/(args.prefix+'.tar.gz')
with archive.open('wb') as raw:
 with gzip.GzipFile(filename='',fileobj=raw,mode='wb',compresslevel=9,mtime=0) as gz:
  with tarfile.open(fileobj=gz,mode='w|',format=tarfile.PAX_FORMAT) as tar:
   for f in sorted(proof.rglob('*')):
    if not f.is_file():continue
    info=tarfile.TarInfo(str(f.relative_to(proof)));info.size=f.stat().st_size;info.mode=0o644;info.uid=info.gid=0;info.mtime=0
    with f.open('rb') as data:tar.addfile(info,data)
members={str(f.relative_to(proof)):dict(sha256=digest(f),bytes=f.stat().st_size) for f in sorted(proof.rglob('*')) if f.is_file()}
outer=dict(schema='osr-pilot-civil-native-proof/1',civil_candidate_id=report['civil_candidate_id'],civil_evaluation_id=report['civil_evaluation_id'],input_load_evaluation_id=report['input_load_evaluation_id'],system_candidate_id=report['system_candidate_id'],native_input_id=report['native_input_id'],
 report_file='report.json',report_evaluation_id=report['evaluation_id'],archive_file=archive.name,archive_sha256=digest(archive),archive_bytes=archive.stat().st_size,members=members,native_source_epoch_id=identity(before),source_commits=[],run_name=run.name,correction='Fresh exact installed loads and common1.435m gauge; no different candidate/evaluation FEM is inherited',
 physical_accepted=False,engineering_accepted=False,manufacturing_release=False,operating_release=False,selected_reference_changed=False,movement_authority=False)
outer['evaluation_id']=identity(outer);(base/(args.prefix+'.json')).write_bytes(encoded(outer))
print(json.dumps(dict(archive=str(archive),archive_bytes=archive.stat().st_size,archive_sha256=outer['archive_sha256'],manifest_id=outer['evaluation_id'],native_source_epoch_id=outer['native_source_epoch_id'],members=len(members))))

from engineering.railway_closure import civil_reference
folder=root/civil_reference.FOLDER
for file in (archive,base/(args.prefix+'.json')):
    target=folder/file.name
    if target.exists():raise ValueError('Proof already registered; previous evidence is immutable')
    shutil.copyfile(file,target)
civil_reference.verify(root=root,manifest_name=args.prefix+'.json')
index=json.loads((folder/civil_reference.INDEX).read_bytes());index.pop('index_id')
index['manifests'].append(args.prefix+'.json');index['index_id']=identity(index)
(folder/civil_reference.INDEX).write_bytes(encoded(index))
