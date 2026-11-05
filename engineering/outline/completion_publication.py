"""Small, lazy-loadable presentation of immutable completed calculations.

Presentation changes do not invalidate engineering calculations. This producer
binds its own source independently of the full execution's evaluator epoch.
"""
from copy import deepcopy
import gzip
import json
import re
from pathlib import Path

from engineering.station_rail import ROOT
from engineering.station_rail.common import digest,encoded,identity
from engineering.development_baseline.planning import _gzip_member
from . import completion,design_completion

PRODUCER='engineering/outline/completion_publication.py'
PUBLICATION=completion.PUBLICATION
FLAGS=completion.FLAGS


def _catalogue(summary):
    value=deepcopy(summary)
    value['schema']='osr-outline-completion-catalogue/2'
    for row in value['cities']:
        row.pop('line_outlines',None)
        row.pop('resources',None)
    value['catalogue_id']=identity(value)
    return value


def _detail(value,full_sha):
    result=completion._detail(value,full_sha)
    civil=value['cost']['civil']
    result['civil_quantities']=civil['quantities']
    result['delivery_draft']['quantity_takeoff']=civil['quantities']
    result['city_cost_evaluation_id']=value['cost']['evaluation_id']
    result['planning_seed']=planning_seed(value,full_sha)
    return result


def planning_seed(value,full_sha):
    """Bind a lossless replay recipe without duplicating all route coordinates."""
    inputs=value['geometry_and_service']
    seed=dict(schema='osr-priced-planning-seed/1',city_slug=value['city']['slug'],
        rules=value['policy'],selected_alignment_id=value['selected_alignment_id'],
        selected_alignment_kind=value['selected_alignment_kind'],
        original_city_input_id=inputs.get('ancestry',{}).get('parent_input_id',inputs['input_id']),
        selected_city_input_id=inputs['input_id'],
        selected_service_evaluation_id=value['service_evaluation']['evaluation_id'],
        source_outline_evaluation_id=value['evaluation_id'],
        source_core_outline_evaluation_id=value['source_outline_evaluation_id'],
        source_cost_evaluation_id=value['cost']['evaluation_id'],
        research_configuration_id=value['research_configuration_id'],
        reference_candidate_ids=value['reference_candidate_ids'],
        source_sha256=value['source_sha256'],source_result_sha256=full_sha,**FLAGS)
    seed['seed_id']=identity(seed)
    return seed


def _write_gzip(path,value):
    path=Path(path);completion._ordinary(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(_gzip_member(encoded(value)))


def publish(state,output,root=ROOT):
    state,output=Path(state),Path(output)
    completion.verify(state,root)
    if output.exists():raise ValueError('Fresh compressed outline publication required')
    summary=json.loads((state/'summary.json').read_bytes())
    if (not summary['every_requested_city_priced'] or summary['pending_cities']
            or summary['outline_accepted_cities']!=summary['requested_cities']):
        raise ValueError('Complete every requested outline before publication')
    full=json.loads((state/'manifest.json').read_bytes())
    output.mkdir(parents=True)
    completion._write(output/'summary.json',_catalogue(summary))
    files={'summary.json':digest(output/'summary.json')}
    for row in summary['cities']:
        slug=row['city']['slug'];name='cities/'+slug+'/result.json'
        value=json.loads((state/name).read_bytes())
        city='cities/'+slug+'.json.gz';geo='maps/'+slug+'.geojson.gz'
        _write_gzip(output/city,_detail(value,full['files_sha256'][name]))
        _write_gzip(output/geo,value['alignment_geometry'])
        files.update({city:digest(output/city),geo:digest(output/geo)})
    sources={**summary['source_sha256'],PRODUCER:digest(Path(root)/PRODUCER),
        'engineering/development_baseline/planning.py':digest(Path(root)/'engineering/development_baseline/planning.py')}
    manifest=completion.seal(dict(schema='osr-outline-completion-publication/2',
        evaluation_id=summary['evaluation_id'],catalogue_id=_catalogue(summary)['catalogue_id'],
        source_sha256=sources,files_sha256=files,canonical_run_manifest_id=full['manifest_id'],
        canonical_summary_sha256=full['files_sha256']['summary.json'],
        publication_scope='Calculated city/design outlines; compressed presentation, no physical release',
        full_run_storage='Private immutable execution; regenerate through engineering.outline complete',
        **FLAGS),'manifest_id')
    completion._write(output/'manifest.json',manifest)
    return manifest


def verify(output=None,root=ROOT):
    output=Path(root)/PUBLICATION if output is None else Path(output)
    manifest=json.loads(completion._ordinary(output/'manifest.json').read_bytes())
    if (manifest.get('schema')!='osr-outline-completion-publication/2'
            or manifest.get('manifest_id')!=identity({k:v for k,v in manifest.items() if k!='manifest_id'})
            or any(manifest.get(k) is not False for k in FLAGS)):
        raise ValueError('Compressed outline publication identity or disposition differs')
    completion._check_sources(root,manifest['source_sha256'])
    value=json.loads(completion._ordinary(output/'summary.json').read_bytes())
    if (value.get('schema')!='osr-outline-completion-catalogue/2'
            or value.get('catalogue_id')!=identity({k:v for k,v in value.items() if k!='catalogue_id'})
            or value['catalogue_id']!=manifest['catalogue_id']
            or value['evaluation_id']!=manifest['evaluation_id']
            or value['completed_cities']!=len(value['cities'])
            or value['outline_accepted_cities']!=value['completed_cities']
            or not value['every_requested_city_priced'] or value['pending_cities']
            or any(value.get(k) is not False for k in FLAGS)):
        raise ValueError('Complete outline catalogue required')
    design_completion.validate(value['designs'],root=root)
    slugs=[r['city']['slug'] for r in value['cities']]
    if (len(slugs)!=len(set(slugs)) or value['requested_cities']!=len(slugs)
            or any(not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',s) for s in slugs)):
        raise ValueError('Unique complete city catalogue required')
    expected={'summary.json'}
    for row in value['cities']:
        completion._check_costs(row)
        if not row['outline_complete'] or any(row.get(k) is not False for k in FLAGS):
            raise ValueError('Calculated city outline cannot grant release')
        slug=row['city']['slug']
        expected.update({'cities/'+slug+'.json.gz','maps/'+slug+'.geojson.gz'})
    if set(manifest['files_sha256'])!=expected:raise ValueError('City publication coverage differs')
    for name,sha in manifest['files_sha256'].items():
        if digest(completion._ordinary(output/name))!=sha:
            raise ValueError('Outline publication artifact differs: '+name)
    return manifest,value


def read_json(path,maximum=64*1024**2):
    with gzip.open(completion._ordinary(path),'rb') as stream:raw=stream.read(maximum+1)
    if len(raw)>maximum:raise ValueError('Compressed city artifact exceeds read budget')
    return json.loads(raw)
