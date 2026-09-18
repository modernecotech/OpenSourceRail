"""Source-bound engineering change bundles; screening never grants release."""
import hashlib
import json
import math
from pathlib import Path


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def write(path,value):Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def artifacts(folder):
    # Python/FreeCAD may create ignored interpreter caches while inspecting a
    # bundle. They are not retained evidence or dependencies used by execution.
    return [p for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.relative_to(folder).parts]


def validate_config(root,config):
    if config.get('schema')!='osr-engineering-change-config/1' or config.get('environment')!='simulation':
        raise ValueError('Only explicit simulation engineering changes are supported')
    for key in ['city','asset_id','component','object']:
        if not isinstance(config.get(key),str) or not config[key].strip():raise ValueError('Missing '+key)
    source=(root/config['source_cad']).resolve()
    if not source.is_relative_to(root.resolve()) or not source.is_file():raise ValueError('CAD source outside repository or missing')
    for key in ['candidate_depth_mm','density_kg_m3','youngs_modulus_mpa','screening_point_load_n']:
        if type(config.get(key)) not in (int,float) or not math.isfinite(config[key]) or config[key]<=0:raise ValueError('Invalid '+key)
    for key,low,high in [('poisson_ratio',0,.49),('purchase_allowance',0,1),('mesh_relative_tolerance',0,.05),('analytical_relative_tolerance',0,.1)]:
        value=config.get(key)
        if type(value) not in (int,float) or not math.isfinite(value) or not low<=value<=high:raise ValueError('Invalid '+key)
    meshes=config.get('mesh_elements')
    if not isinstance(meshes,list) or len(meshes)<3 or any(type(n)!=int or not 4<=n<=128 or n%2 for n in meshes) or meshes!=sorted(set(meshes)):
        raise ValueError('At least three increasing even meshes (4..128) required')
    if not config.get('release_blockers'):raise ValueError('Release boundary must remain explicit')
    return config


def evidence_status(record,current_inputs):
    if record.get('input_sha256')!=current_inputs:return 'superseded'
    return 'screening-current' if record.get('passed') is True else 'failed'


def seal(root,folder,config,configuration_sources=()):
    cad=json.loads((folder/'cad-results.json').read_text())
    if not cad.get('passed') or cad['source_sha256']!=sha(root/config['source_cad']):raise ValueError('CAD source changed during execution')
    if cad['candidate_sha256']!=sha(folder/'candidate.FCStd'):raise ValueError('Candidate CAD differs from native result')
    records=[]
    for name in ['baseline','candidate']:
        if json.loads((folder/(name+'-quantities.json')).read_text())!=cad[name]:raise ValueError('Native quantities differ')
        result=json.loads((folder/(name+'-analysis/summary.json')).read_text())
        if result.get('passed') is not True:raise ValueError('Analysis did not pass')
        inputs=dict(cad=cad['source_sha256'] if name=='baseline' else cad['candidate_sha256'],
            quantities=sha(folder/(name+'-quantities.json')),configuration=digest(config))
        records.append(dict(revision=name,passed=True,maturity='screening',input_sha256=inputs,
            result_sha256=sha(folder/(name+'-analysis/summary.json')),independently_accepted=False))
    records[0]['status']=evidence_status(records[0],records[1]['input_sha256'])
    records[1]['status']=evidence_status(records[1],records[1]['input_sha256'])
    if records[0]['status']!='superseded':raise ValueError('Candidate must change CAD-dependent evidence')
    write(folder/'assurance.json',dict(schema='osr-change-assurance/1',records=records,
        formal_impact_assessment='required; no mechanical formal proof is claimed',physical_release=False,
        remaining=config['release_blockers']))
    write(folder/'resolved-config.json',config)
    files={p.relative_to(folder).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(artifacts(folder))}
    dependencies={name:sha(root/name) for name in [config['source_cad'],'engineering/changes/freecad_change.py',
        'engineering/changes/workflow.py','design/component-catalogue/src/osr_mech/freecad_fea.py',
        'design/component-catalogue/src/osr_mech/freecad_assembly_review.py',*configuration_sources]}
    manifest=dict(schema='osr-engineering-change-bundle/1',city=config['city'],asset_id=config['asset_id'],
        component=config['component'],environment='simulation',files=files,source_sha256=dependencies,
        stages=['native-cad-edit','native-solid-quantities','calculix-mesh-and-analytical-checks','erp-nested-bom-and-production','screening-evidence-supersession'],
        engineering_release=False,physical_release=False)
    manifest['sha256']=digest(manifest);write(folder/'manifest.json',manifest)
    return manifest


def verify(root,folder):
    manifest=json.loads((folder/'manifest.json').read_text())
    if manifest.get('schema')!='osr-engineering-change-bundle/1' or manifest.get('sha256')!=digest({k:v for k,v in manifest.items() if k!='sha256'}):
        raise ValueError('Invalid change manifest')
    if manifest.get('engineering_release') is not False or manifest.get('physical_release') is not False:raise ValueError('Screening cannot grant release')
    actual={p.relative_to(folder).as_posix() for p in artifacts(folder)}
    if actual!=set(manifest['files'])|{'manifest.json'}:raise ValueError('Change bundle membership differs')
    for path,record in manifest['files'].items():
        p=folder/path
        if not p.resolve().is_relative_to(folder.resolve()) or p.is_symlink() or sha(p)!=record['sha256'] or p.stat().st_size!=record['bytes']:
            raise ValueError('Changed or unsafe artifact: '+path)
    for path,expected in manifest['source_sha256'].items():
        p=root/path
        if not p.resolve().is_relative_to(root.resolve()) or sha(p)!=expected:raise ValueError('Source dependency changed: '+path)
    validate_config(root,json.loads((folder/'resolved-config.json').read_text()))
    return manifest
