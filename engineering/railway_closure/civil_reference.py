"""Authenticate an exact-load elastic FEM reference without executing tools."""
from pathlib import Path
from hashlib import sha256
from math import fsum
import json,tarfile
from engineering.station_rail.common import identity,digest
from engineering.pilot_civil.native_trial import source_context
from . import ROOT

FOLDER='engineering/railway_closure/data/civil-native'
MANIFEST='civil-final-load01-proof.json'
INDEX='index.json'


def require(condition,message):
    if not condition:raise ValueError(message)


def sealed(v,key='evaluation_id'):
    require(v[key]==identity({k:x for k,x in v.items() if k!=key}),'Civil proof seal differs')
    return v


def manifest_names(folder):
    folder=Path(folder);path=folder/INDEX
    if not path.exists():return [MANIFEST]
    registry=sealed(json.loads(path.read_bytes()),'index_id')
    require(registry['schema']=='osr-civil-proof-registry/1','Unexpected civil proof registry')
    names=registry['manifests']
    require(isinstance(names,list) and names and len(names)<=16 and len(names)==len(set(names)),'Bounded unique civil proof manifests required')
    for name in names:
        require(isinstance(name,str) and Path(name).name==name and name.endswith('.json') and '..' not in name,'Ordinary civil proof manifest name required')
    return names


def verify(folder=None,*,root=ROOT,manifest_name=MANIFEST):
    folder=Path(root)/FOLDER if folder is None else Path(folder)
    require(Path(manifest_name).name==manifest_name and manifest_name.endswith('.json') and '..' not in manifest_name,'Ordinary civil proof manifest name required')
    m=sealed(json.loads((folder/manifest_name).read_bytes()))
    require(m['schema']=='osr-pilot-civil-native-proof/1','Unexpected civil proof schema')
    archive=folder/m['archive_file']
    require(archive.parent==folder and archive.stat().st_size==m['archive_bytes'] and digest(archive)==m['archive_sha256'],'Civil proof archive changed')
    wanted={'axle-input.json','civil.json','native-input.json','report.json','source-before.json','source-after.json','upstream-source-after.json','independent-cad-summary.json'}
    for i in (1,2,3):
        wanted|={f'case-{i}/result.json',f'case-{i}/mesh.json'}
        wanted|={f'case-{i}/{tool}/usage.json' for tool in ('mesh-native','fieldcraft','calculix')}
    values={}
    with tarfile.open(archive,'r:gz') as tar:
        members=tar.getmembers();names=[q.name for q in members]
        require(len(names)==len(set(names)) and set(names)==set(m['members']),'Civil proof inventory differs')
        require(sum(q.size for q in members)<=512*1024**2,'Civil proof byte budget exceeded')
        for q in members:
            name=Path(q.name);spec=m['members'][q.name]
            require(q.isfile() and not name.is_absolute() and '..' not in name.parts and q.size<=64*1024**2,'Ordinary bounded civil proof member required')
            require(q.size==spec['bytes'],'Civil proof member size differs')
            stream=tar.extractfile(q);h=sha256();chunks=[]
            while block:=stream.read(1024**2):
                h.update(block)
                if q.name in wanted:chunks.append(block)
            require(h.hexdigest()==spec['sha256'],'Civil proof member hash differs: '+q.name)
            if q.name in wanted:values[q.name]=json.loads(b''.join(chunks))
    require(wanted<=set(values),'Missing civil proof input/result')
    train=sealed(values['axle-input.json']);civil=sealed(values['civil.json']);native=sealed(values['native-input.json'],'input_id');report=sealed(values['report.json'])
    contract=train['track_interface']
    require(contract==civil['physical_definition']['rail_interface']['track_interface']==native['track_interface'],'Civil proof wheel/rail datums differ')
    require(native['rail_patch_hypothesis']['centres_y_m']==contract['nominal_contact_centres_y_m'],'Civil native rail patches differ from installed interface')
    require(report['system_candidate_id']==train['candidate_id']==native['system_candidate_id']==civil['system_candidate_id'],'Mixed civil proof system')
    require(report['civil_candidate_id']==civil['civil_candidate_id']==native['candidate_id']==identity(civil['physical_definition']),'Mixed civil physical identity')
    require(report['civil_evaluation_id']==civil['evaluation_id']==m['civil_evaluation_id'],'Mixed civil evaluation')
    require(report['input_load_evaluation_id']==train['evaluation_id']==native['input_load_evaluation_id']==civil['input_load_evaluation_id']==m['input_load_evaluation_id'],'Mixed civil axle inputs')
    require(report['native_input_id']==native['input_id']==m['native_input_id'],'Mixed civil native input')
    before=values['source-before.json']
    require(before==values['source-after.json']==source_context(root),'Civil method source epoch differs')
    require(identity(before)==m['native_source_epoch_id'],'Civil source epoch identity differs')
    require(values['upstream-source-after.json']==train['source_sha256'],'Civil upstream source changed')
    for kind,mapping in (('numerical',before),('upstream',train['source_sha256'])):
        for name,want in mapping.items():
            require(m['members'].get('source/'+kind+'/'+name,{}).get('sha256')==want,'Archived civil source binding differs')
    for load in train['load_cases']:
        force=fsum(a['vertical_force_N'] for a in load['axles'])
        require(abs(force-load['train_mass_kg']*9.80665)<=1e-7*force,'Civil input mass does not close')
    require(abs(values['independent-cad-summary.json']['total_volume_m3']-civil['quantities']['concrete_beam_m3'])<1e-6,'Civil CAD volume differs')
    results=[]
    for i in (1,2,3):
        prefix=f'case-{i}/';r=sealed(values[prefix+'result.json']);mesh=sealed(values[prefix+'mesh.json'],'mesh_id')
        require(r['candidate_id']==civil['civil_candidate_id'] and r['input_id']==native['input_id'] and r['mesh_id']==mesh['mesh_id'],'Civil mesh/case differs')
        require(len(mesh['elements'])<=50000 and r['cross_solver_screen_passed'] and r['cross_solver_relative_difference']<=.02,'Civil numerical comparison outside declared screen')
        require(r['support_audit']['rotation_free_line_definition_resolved'],'Civil supports do not implement the declared rotation-free lines')
        for row in r['support_audit']['rows']:
            require(row['node_x_range_m']==[row['axis_x_m']]*2 and abs(row['vertical_reaction_bending_couple_Nm'])<1e-6,'Civil numerical support introduces a bending clamp')
        for tool in ('fieldcraft','calculix'):
            q=r[tool]
            require(q['force_equilibrium_passed'] and q['moment_equilibrium_passed'] and q['physical_accepted'] is False and q['engineering_accepted'] is False,'Civil equilibrium or evidence boundary differs')
        force=fsum(q[2] for q in mesh['nodal_load_N'].values())
        require(abs(force-mesh['applied_N'][2])<=1e-8*abs(force),'Civil mesh force accounting differs')
        line=native['line_equipment_gravity'];moment=-line['mass_kg']*9.80665*line['lateral_y_m']
        require(abs(mesh['applied_moment_Nm'][0]-moment)<=1e-6*abs(moment),'Conductor eccentric load differs')
        for tool in ('mesh-native','fieldcraft','calculix'):
            usage=values[prefix+tool+'/usage.json']
            require(usage['exit']==0 and usage['peak_rss_kib']<=3072*1024,'Civil job unsuccessful or memory budget exceeded')
            if 'user_s' in usage:require(usage['user_s']+usage['system_s']<=75,'Civil job CPU budget exceeded')
        results.append(r)
    changes=[abs(a['fieldcraft']['displacement_m'][2]-b['fieldcraft']['displacement_m'][2])/abs(b['fieldcraft']['displacement_m'][2]) for a,b in zip(results,results[1:])]
    require(all(x<=.05 for x in changes) and report['refinement_screen_passed'],'Civil refinement exceeds unchanged target')
    require(report['physical_accepted'] is False and report['engineering_accepted'] is False,'Civil elastic proof cannot grant acceptance')
    return dict(manifest=m,report=report,refinement_changes=changes)


def applicable(civil,axles,*,root=ROOT):
    folder=Path(root)/FOLDER;seen=[];matches=[]
    for name in manifest_names(folder):
        m=sealed(json.loads((folder/name).read_bytes()));seen.append(m['evaluation_id'])
        require(m['schema']=='osr-pilot-civil-native-proof/1','Unexpected civil proof schema')
        if m['civil_evaluation_id']==civil['evaluation_id'] and m['input_load_evaluation_id']==axles['evaluation_id']:
            matches.append(name)
    require(len(matches)<=1,'Ambiguous exact-load civil proof; revise the registry explicitly')
    if not matches:
        return dict(applicable=False,reference_manifest_ids=seen,reason='Different candidate/load/source evaluation; native result is not inherited',physical_accepted=False)
    name=matches[0];proof=verify(root=root,manifest_name=name);m=proof['manifest']
    return dict(applicable=True,reference_manifest_id=m['evaluation_id'],manifest_file=name,archive_file=m['archive_file'],report=proof['report'],
                refinement_changes=proof['refinement_changes'],physical_accepted=False)
