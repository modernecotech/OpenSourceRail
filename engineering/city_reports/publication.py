"""Publish current city front doors without changing numerical source epochs.

The geographic hold producer remains authoritative for its exact summaries and
register. This explicit presentation owner binds richer front doors under /3
receipts, independently authenticating the calculated outline and map sources.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import csv
import gzip
import io
import json
import os
import zipfile

from engineering.station_rail import ROOT, FLAGS
from engineering.station_rail import cities
from engineering.station_rail.common import digest, encoded, identity

OUTPUT = 'docs/design-engine/city-dossiers'
SCHEMA = 'osr-city-dossiers/1'
CITY_SCHEMA = 'osr-current-city-publication/3'
PACKAGE = 'engineering/outline'


def _sources(root):
    folder = Path(root)/'engineering/city_reports'
    return {p.relative_to(root).as_posix(): digest(p) for p in sorted(folder.iterdir())
            if p.suffix in ('.py', '.json') and p.is_file()}


def _read(path, limit=32*1024**2):
    path = Path(path)
    if path.suffix == '.gz':
        with gzip.open(path, 'rb') as f:
            raw = f.read(limit+1)
    else:
        raw = path.read_bytes()
    if len(raw) > limit:
        raise ValueError('City dossier input exceeds byte budget')
    return json.loads(raw)


def _write(path, raw):
    cities.write(path, raw.encode() if isinstance(raw, str) else raw)


def _csv(rows):
    if not rows:
        return 'status\nNo rows established by the current source\n'
    fields = list(dict.fromkeys(k for r in rows for k in r))
    text = io.StringIO(newline='')
    writer = csv.DictWriter(text, fields, lineterminator='\n')
    writer.writeheader()
    for row in rows:
        if any(isinstance(x, (dict, list, tuple)) for x in row.values()):
            raise ValueError('Flat CSV rows required')
        writer.writerow(row)
    return text.getvalue()


def _relative(directory, path):
    from urllib.parse import quote
    return quote(Path(os.path.relpath(path, directory)).as_posix(), safe='/-._?=')


def _inputs(root):
    from engineering.outline import city_atlas, city_atlas_api, publication_cache
    # Authenticate the publication and all compressed source hashes once. Each
    # requested packet is then checked and numerically reconciled by analysis;
    # do not decode/canonicalise the entire atlas twice before publishing it.
    atlas=city_atlas_api.published(root)
    am=_read(root/city_atlas.PUBLICATION/'manifest.json')
    cm,_=publication_cache.verified(root)
    if am['publication_manifest_id'] != cm['manifest_id']:
        raise ValueError('Atlas and city outline epochs differ')
    registered = cities.read_catalogue(root)
    rows = {r['slug']:r for r in registered['cities']}
    if set(rows) != {r['city']['slug'] for r in atlas['cities']}:
        raise ValueError('Complete registered city dossier coverage required')
    return am, cm, rows


def _city_inputs(root, row, atlas_manifest, outline_manifest, *, background_needed=True):
    from engineering.outline import city_atlas, completion_publication
    slug = row['slug']
    atlas_name = 'cities/'+slug+'.json.gz'
    detail_name = 'cities/'+slug+'.json.gz'
    ap = root/city_atlas.PUBLICATION/atlas_name
    dp = root/completion_publication.PUBLICATION/detail_name
    if digest(ap) != atlas_manifest['files_sha256'][atlas_name] or digest(dp) != outline_manifest['files_sha256'][detail_name]:
        raise ValueError('City dossier calculation bytes changed')
    packet, detail = _read(ap), _read(dp)
    context_path = root/row['geography_path']
    if packet['sources']['calculation_sha256'].get(row['geography_path']) != digest(context_path):
        raise ValueError('City context differs from the calculated source')
    background = None
    ref = packet.get('map_context')
    if ref:
        p = Path(ref['path'])
        if p.is_absolute() or '..' in p.parts or packet['sources']['calculation_sha256'].get(p.as_posix()) != ref['sha256']:
            raise ValueError('City map context is not calculation-bound')
        if digest(root/p) != ref['sha256']:
            raise ValueError('City map context changed')
        if background_needed:background = _read(root/p,limit=64*1024**2)
    return packet, detail, _read(context_path), background, ap, dp


def _hold_readme(value, root):
    original = cities._city_readmes(value, root)[1]
    directory = Path(value['city_path'])/'engineering/current'
    report = _relative(directory, Path(value['city_path'])/'README.md')
    return original+'\n[Complete city design and cost dossier]('+report+') includes the calculated network, service, maps, resources, costs and explicit outline scenarios. This physical-evidence record remains a separate hold.\n'


def publish_geography(root=ROOT):
    """Keep exact hold/register bytes while preserving an existing /3 frontend.

    This calls the unchanged geographic evaluator. A display refresh never
    enters its source map or changes a planning seed's numerical ancestry.
    """
    root=Path(root).resolve()
    from engineering.development_baseline import selection
    baseline=selection.load(root);rows=cities.catalogue(root)
    for row in rows:
        value=cities.evaluate_city(row['geography_path'],baseline,root=root,_canonical=baseline)
        current=root/row['path']/'engineering/current'
        try:
            m=_read(current/'manifest.json')
            retain=(m.get('schema')==CITY_SCHEMA and (current/'summary.json').read_bytes()==encoded(value))
        except (OSError,ValueError):retain=False
        if not retain:cities._publish_city_frontdoor(row,baseline,root)
    value=cities._record(root,baseline);_write(root/cities.INDEX,encoded(value))
    receipt=dict(schema='osr-current-city-catalogue-publication/1',**{k:value[k] for k in cities.IDS},
        selection_id=value['selection_id'],evaluation_id=value['evaluation_id'],
        files_sha256={cities.INDEX:digest(root/cities.INDEX)},summary=value['summary'],
        development_default=True,city_performance_packages_written=0,current_city_frontdoors_written=len(rows),**FLAGS)
    _write(root/cities.INDEX_MANIFEST,encoded(receipt))
    return value


def publish(root=ROOT):
    import fcntl
    root=Path(root).resolve();lock=root/'build/city-dossiers/publication.lock';lock.parent.mkdir(parents=True,exist_ok=True)
    with lock.open('a+') as handle:
        fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        return _publish(root)


def _publish(root):
    from . import analysis, maps, render
    root = Path(root).resolve()
    am, cm, rows = _inputs(root)
    try:
        previous=_manifest(root)
        if (previous['atlas_manifest_id']==am['manifest_id'] and previous['outline_manifest_id']==cm['manifest_id']
                and previous['source_register_sha256']==digest(root/cities.INDEX)):
            return previous
    except (OSError,ValueError,KeyError):pass
    from engineering.development_baseline import selection
    selected = selection.load(root)
    source = _sources(root)
    files, index = {}, []
    for slug, row in sorted(rows.items()):
        packet, detail, context, _, ap, dp = _city_inputs(root, row, am, cm,background_needed=False)
        model = analysis.build(packet, detail, city_context=context)
        folder = root/row['path']/PACKAGE
        _write(folder/'summary.json', encoded(model))
        map_request=dict(renderer_sha256=digest(Path(maps.__file__)),packet_id=packet['packet_id'],
                         context=packet.get('map_context'),width=1400,height=1050)
        map_request_id=identity(map_request)
        reuse=False
        try:
            previous=_read(folder/'manifest.json')
            old_valid=(previous.get('manifest_id')==identity({k:v for k,v in previous.items() if k!='manifest_id'})
                and previous.get('atlas_packet_id')==packet['packet_id']
                and previous.get('source_sha256',{}).get('engineering/city_reports/maps.py')==map_request['renderer_sha256']
                and previous['files_sha256'].get('network.svg')==digest(folder/'network.svg'))
            if old_valid:
                if previous.get('map_request_id')==map_request_id:reuse=True
                elif 'map_request_id' not in previous:
                    # Migration of this publisher's initial source-bound display
                    # receipt: validate its explicit default canvas as well.
                    from xml.etree import ElementTree as ET
                    svg_root=ET.parse(folder/'network.svg').getroot()
                    reuse=(svg_root.get('width')=='1400' and svg_root.get('height')=='1050')
        except (ValueError,OSError,KeyError):pass
        if not reuse:
            ref=packet.get('map_context');background=_read(root/ref['path'],limit=64*1024**2) if ref else None
            _write(folder/'network.svg',maps.render(packet,background,context_verified=background is not None))
        local_files = {'summary.json':digest(folder/'summary.json'), 'network.svg':digest(folder/'network.svg')}
        drafts=dict(schema=SCHEMA+'/delivery-draft',source_outline_file_sha256=digest(dp),
            source_outline_evaluation_id=packet['identity']['outline_evaluation_id'],
            source_fragment=detail['delivery_draft'],source_fragment_id=identity(detail['delivery_draft']),
            transactions_performed=False,release_granted=False)
        drafts['record_id']=identity(drafts)
        _write(folder/'delivery-draft.json.gz',gzip.compress(encoded(drafts),mtime=0))
        local_files['delivery-draft.json.gz']=digest(folder/'delivery-draft.json.gz')
        for name, table in model['tables'].items():
            if not name.replace('_','').isalnum():
                raise ValueError('Known city table name required')
            bound=[dict(atlas_packet_id=packet['packet_id'],outline_evaluation_id=packet['identity']['outline_evaluation_id'],**record)
                   for record in table]
            _write(folder/(name+'.csv'), _csv(bound))
            local_files[name+'.csv'] = digest(folder/(name+'.csv'))
        bundle=io.BytesIO()
        with zipfile.ZipFile(bundle,'w') as archive:
            layers=maps.geojson_layers(packet)
            for name,layer in sorted(layers.items()):
                info=zipfile.ZipInfo(name+'.geojson',date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
                info.external_attr=0o100644<<16;archive.writestr(info,encoded(layer))
        _write(folder/'gis.zip',bundle.getvalue());local_files['gis.zip']=digest(folder/'gis.zip')
        for name, layer in layers.items():
            if not name.replace('_','').replace('-','').isalnum():
                raise ValueError('Known city GIS layer required')
            filename = 'gis/'+name+'.geojson.gz'
            _write(folder/filename, gzip.compress(encoded(layer), mtime=0))
            local_files[filename] = digest(folder/filename)
        _write(root/row['path']/'README.md', render.city(model, packet, detail, row, root))
        value = cities.evaluate_city(row['geography_path'], selected, root=root, _canonical=selected)
        current = root/row['path']/'engineering/current'
        if (current/'summary.json').read_bytes() != encoded(value):
            raise ValueError('Canonical geographic hold must be published before dossiers')
        _write(current/'README.md', _hold_readme(value, root))
        dossier = dict(schema=SCHEMA+'/city', city_slug=slug,
            outline_evaluation_id=packet['identity']['outline_evaluation_id'], atlas_packet_id=packet['packet_id'],
            source_sha256=source, atlas_file=ap.relative_to(root).as_posix(), atlas_sha256=digest(ap),
            outline_file=dp.relative_to(root).as_posix(), outline_sha256=digest(dp),
            files_sha256=local_files,map_request_id=map_request_id,map_request=map_request,
            city_frontdoor_path=row['path']+'/README.md',
            city_frontdoor_sha256=digest(root/row['path']/'README.md'), **FLAGS)
        dossier['manifest_id'] = identity(dossier)
        _write(folder/'manifest.json', encoded(dossier))
        physical = dict(schema=CITY_SCHEMA, family=cities.FAMILY,
            **{key:value[key] for key in cities.IDS}, selection_id=value['selection_id'], evaluation_id=value['evaluation_id'],
            development_default=True, city_frontdoor_path=dossier['city_frontdoor_path'],
            city_frontdoor_sha256=dossier['city_frontdoor_sha256'], source_sha256=value['source_sha256'],
            files_sha256={n:digest(current/n) for n in ('README.md','summary.json')}, city_performance_package=False,
            presentation=dict(owner='engineering.city_reports.publication', dossier_manifest_path=(folder/'manifest.json').relative_to(root).as_posix(),
                              dossier_manifest_id=dossier['manifest_id']), **FLAGS)
        physical['manifest_id'] = identity(physical)
        _write(current/'manifest.json', encoded(physical))
        for name in (*local_files, 'manifest.json'):
            p=folder/name;files[p.relative_to(root).as_posix()]=digest(p)
        for p in (root/row['path']/'README.md',current/'README.md',current/'manifest.json'):
            files[p.relative_to(root).as_posix()] = digest(p)
        index.append(dict(city=packet['city'],path=row['path'],packet_id=packet['packet_id'],
            outline_evaluation_id=packet['identity']['outline_evaluation_id'],route_km=packet['summary']['route_km'],
            lines=len(packet['lines']),station_complexes=packet['summary']['operational_station_complexes'],
            trainsets=packet['summary']['total_trainsets'],installed_capital_usd=packet['costs']['installed_capital_usd'],
            whole_life_npv_usd=packet['costs']['whole_life_npv_usd']))
    _write(root/OUTPUT/'index.json', encoded(dict(schema=SCHEMA+'/index',cities=index,city_count=len(index),**FLAGS)))
    files[OUTPUT+'/index.json']=digest(root/OUTPUT/'index.json')
    countries=render.nations(index,root)
    for name, text in countries.items():
        _write(root/name,text);files[name]=digest(root/name)
    manifest=dict(schema=SCHEMA+'/publication',source_sha256=source,
        atlas_manifest_id=am['manifest_id'],outline_manifest_id=cm['manifest_id'],
        city_count=len(index),files_sha256=files,
        numerical_sources_changed=False,source_register_sha256=digest(root/cities.INDEX),**FLAGS)
    manifest['manifest_id']=identity(manifest)
    _write(root/OUTPUT/'manifest.json', encoded(manifest))
    return manifest


def _manifest(root):
    path=root/OUTPUT/'manifest.json';m=_read(path)
    if (m.get('schema')!=SCHEMA+'/publication' or m.get('manifest_id')!=identity({k:v for k,v in m.items() if k!='manifest_id'})
            or any(m.get(k) is not False for k in FLAGS) or m.get('source_sha256')!=_sources(root)):
        raise ValueError('City dossier publication source/identity differs')
    for name, sha in m['files_sha256'].items():
        p=Path(name)
        if p.is_absolute() or '..' in p.parts or digest(root/p)!=sha:
            raise ValueError('City dossier output differs: '+name)
    return m


def verify_all(output=None, baseline=None, root=ROOT, civil=None, replay=True):
    root=Path(root).resolve()
    if not (root/OUTPUT/'manifest.json').is_file():
        return cities.verify_all(output,baseline,root,civil,replay)
    from engineering.development_baseline import selection
    baseline=selection.load(root) if baseline is None else baseline
    m=_manifest(root);am,cm,rows=_inputs(root)
    if (m['atlas_manifest_id']!=am['manifest_id'] or m['outline_manifest_id']!=cm['manifest_id']
            or m['source_register_sha256']!=digest(root/cities.INDEX) or m['city_count']!=len(rows)):
        raise ValueError('City dossier upstream epoch differs')
    actual=cities.read_catalogue(root)
    if actual!=cities._record(root,baseline):
        raise ValueError('Current city geographic register differs')
    receipt=_read(root/cities.INDEX_MANIFEST)
    if (receipt['files_sha256']!={cities.INDEX:digest(root/cities.INDEX)}
            or receipt.get('city_performance_packages_written')!=0
            or receipt.get('current_city_frontdoors_written')!=len(rows)
            or any(receipt.get(k) is not False for k in FLAGS)):
        raise ValueError('City hold catalogue receipt differs')
    for key in ('selection_id',*cities.IDS,'evaluation_id'):
        if receipt.get(key)!=actual[key]:raise ValueError('City hold receipt identity differs')
    for slug,row in rows.items():
        value=cities.evaluate_city(row['geography_path'],baseline,root=root,_canonical=baseline)
        current=root/row['path']/'engineering/current';package=_read(current/'manifest.json')
        if (package.get('schema')!=CITY_SCHEMA or package.get('manifest_id')!=identity({k:v for k,v in package.items() if k!='manifest_id'})
                or package.get('city_performance_package') is not False or any(package.get(k) is not False for k in FLAGS)):
            raise ValueError('Current city presentation/hold disposition differs')
        if ((current/'summary.json').read_bytes()!=encoded(value) or (current/'README.md').read_text()!=_hold_readme(value,root)
                or package.get('source_sha256')!=value['source_sha256']
                or package.get('files_sha256')!={n:digest(current/n) for n in ('README.md','summary.json')}
                or package.get('city_frontdoor_path')!=row['path']+'/README.md'
                or package.get('city_frontdoor_sha256')!=digest(root/row['path']/'README.md')):
            raise ValueError('City hold source or front door differs: '+slug)
        for key in ('selection_id',*cities.IDS,'evaluation_id'):
            if package.get(key)!=value[key]:raise ValueError('Mixed physical city identity')
        dossier=_read(root/row['path']/PACKAGE/'manifest.json')
        expected_path=row['path']+'/'+PACKAGE+'/manifest.json'
        if (dossier.get('schema')!=SCHEMA+'/city' or dossier.get('city_slug')!=slug
                or dossier.get('manifest_id')!=identity({k:v for k,v in dossier.items() if k!='manifest_id'})
                or package['presentation']['dossier_manifest_id']!=dossier['manifest_id']
                or package['presentation'].get('dossier_manifest_path')!=expected_path
                or package['presentation'].get('owner')!='engineering.city_reports.publication'
                or dossier['source_sha256']!=m['source_sha256'] or any(dossier.get(k) is not False for k in FLAGS)):
            raise ValueError('City presentation ownership differs')
        packet,detail,context,_,ap,dp=_city_inputs(root,row,am,cm,background_needed=False)
        if (dossier.get('atlas_file')!=ap.relative_to(root).as_posix() or dossier.get('atlas_sha256')!=digest(ap)
                or dossier.get('outline_file')!=dp.relative_to(root).as_posix() or dossier.get('outline_sha256')!=digest(dp)
                or dossier.get('atlas_packet_id')!=packet['packet_id']
                or dossier.get('outline_evaluation_id')!=packet['identity']['outline_evaluation_id']):
            raise ValueError('City dossier calculation identity differs')
        if replay:
            from . import analysis,render
            model=analysis.build(packet,detail,city_context=context)
            if ((root/row['path']/PACKAGE/'summary.json').read_bytes()!=encoded(model)
                    or (root/row['path']/'README.md').read_text()!=render.city(model,packet,detail,row,root)):
                raise ValueError('City dossier replay differs: '+slug)
        for name,sha in dossier['files_sha256'].items():
            n=Path(name)
            if n.is_absolute() or '..' in n.parts:raise ValueError('Relative dossier artifact required')
            rel=row['path']+'/'+PACKAGE+'/'+name
            if m['files_sha256'].get(rel)!=sha or digest(root/rel)!=sha:
                raise ValueError('City dossier artifact coverage differs')
    expected={OUTPUT+'/index.json'}
    for row in rows.values():
        dossier=_read(root/row['path']/PACKAGE/'manifest.json')
        expected.update(row['path']+'/'+PACKAGE+'/'+n for n in dossier['files_sha256'])
        expected.update((row['path']+'/'+PACKAGE+'/manifest.json',row['path']+'/README.md',
                        row['path']+'/engineering/current/README.md',row['path']+'/engineering/current/manifest.json'))
        expected.add(str(Path(row['path']).parent/'NATIONAL-BRIEF.md'))
    if set(m['files_sha256'])!=expected:raise ValueError('City dossier publication coverage differs')
    return dict(verified=True,replayed=replay,city_count=len(rows),cities_held=len(rows),
        city_dossiers_verified=len(rows),selection_id=actual['selection_id'],candidate_id=actual['candidate_id'],
        source_and_payload_integrity=True,city_performance_packages_written=0,
        current_city_frontdoors_verified=len(rows),physical_acceptance=False)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=('publish','verify'))
    a=p.parse_args()
    r=publish() if a.command=='publish' else verify_all()
    print(json.dumps({k:v for k,v in r.items() if k in ('verified','manifest_id','city_count','city_dossiers_verified')}))


if __name__=='__main__':main()
