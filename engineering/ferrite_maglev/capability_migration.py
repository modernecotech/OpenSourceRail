"""Current capability-page index; no old product description is published here."""
from hashlib import sha256
import json
import os
from pathlib import Path

from . import model, pilot_assurance

INPUT = Path(__file__).parent/'data/pilot-capability-migration.json'
OUTPUT = model.ROOT/'docs/design-engine/ferrite-maglev/capability-migration'
SCHEMA = 'osr-v06-current-capability-index/1'
MIGRATION_SCHEMA = 'osr-maglev-capability-migration/1'
STATES = {'retained-and-tested','retained-but-unconnected','replaced','deliberately-retired','missing'}
CURRENT_PAGES = (
    ('Project overview','docs/open-source-rail-overview.md'),
    ('Platform capabilities','docs/capabilities/README.md'),
    ('Current engineering dossier','docs/design-engine/current/README.md'),
    ('Planning workspace','docs/workbench/planning/index.html'),
)


def encoded(value):
    return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def source_paths():
    return [Path(__file__),INPUT,model.ROOT/'engineering/analysis/tests/test_ferrite_maglev_capability_migration.py']


def sources():
    paths=set(source_paths())
    for row in load()['capabilities']:
        paths.update(model.ROOT/name for name in row['current_sources']+row['tests'])
    return {p.relative_to(model.ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def load():
    value=json.loads(INPUT.read_bytes())
    if value['schema']!='osr-v04-capability-migration-input/1' or len(value['capabilities'])!=14:
        raise ValueError('actual fourteen v0.4 feature rows required')
    if len({r['id'] for r in value['capabilities']})!=14:
        raise ValueError('duplicate migration identity')
    for row in value['capabilities']:
        if row['state'] not in STATES or not row['owner'] or not row['decision'] or not row['acceptance_test']:
            raise ValueError('migration disposition/owner/test required')
        for name in row['current_sources']+row['tests']:
            path=model.ROOT/name
            if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(model.ROOT):
                raise ValueError('migration evidence source absent or unsafe: '+name)
    return value


def study():
    value=load(); rows=[]
    profiles={r['id']:r for r in pilot_assurance.study()['profiles']}
    for source in value['capabilities']:
        row=dict(source)
        profile=profiles.get(row.get('execution_profile'))
        row['executed_current']=bool(profile and profile['digital_state']=='executed-current')
        row['execution_receipt']=profile['receipt'] if row['executed_current'] else None
        # Passing a source-only check cannot establish integrated retention.
        if row['state']=='retained-and-tested' and not row['executed_current']:
            row['state']='retained-but-unconnected'
        row['engineering_accepted']=False
        rows.append(row)
    return dict(schema=MIGRATION_SCHEMA,baseline=value['baseline'],capabilities=rows,
                state_counts={s:sum(r['state']==s for r in rows) for s in sorted(STATES)},
                products=value['products'],source_sha256=sources(),
                scope='Migration of the actual v0.4 feature table. Tested scope is stated per row; missing features are not marked complete.',
                **model.FLAGS)


def readme(value,output=OUTPUT):
    def link(name):
        return Path(os.path.relpath(model.ROOT/name,output)).as_posix()
    lines=['# Current OpenSourceRail capabilities','',
           'Use the maintained v0.6 pages for current product scope and workflow status:', '',
           f"- [Project overview]({link('docs/open-source-rail-overview.md')})",
           f"- [Platform capabilities]({link('docs/capabilities/README.md')})",
           f"- [Current engineering dossier]({link('docs/design-engine/current/README.md')})",
           f"- [Planning workspace]({link('docs/workbench/planning/index.html')})", '',
           'These pages describe the selected wheel-supported reference, candidate-bound planning and delivery records, and the limits of each current workflow. They are the maintained source for user-facing capability claims.', '']
    return '\n'.join(lines)


def current_index():
    pages=[dict(title=title,path=path) for title,path in CURRENT_PAGES]
    return dict(schema=SCHEMA,pages=pages,
                scope='Current v0.6 product and workflow documentation.',
                source_sha256=index_sources(),**model.FLAGS)


def index_sources():
    paths={Path(__file__)}
    paths.update(model.ROOT/name for _,name in CURRENT_PAGES)
    return {p.relative_to(model.ROOT).as_posix():sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}


def publish(output=OUTPUT):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);value=current_index()
    files={'study.json':encoded(value),'README.md':readme(value,output).encode()}
    for name,data in files.items():(output/name).write_bytes(data)
    receipt=dict(schema=SCHEMA,source_sha256=value['source_sha256'],files_sha256={n:sha256(d).hexdigest() for n,d in files.items()},**model.FLAGS)
    (output/'manifest.json').write_bytes(encoded(receipt));return receipt


def verify(output=OUTPUT):
    output=Path(output);r=json.loads((output/'manifest.json').read_bytes())
    current=current_index()
    if (output.is_symlink() or r['schema']!=SCHEMA or any(r.get(k) is not False for k in model.FLAGS)
            or set(p.name for p in output.iterdir())!={'README.md','study.json','manifest.json'}
            or any(p.is_symlink() for p in output.iterdir())
            or r['files_sha256']!={n:sha256((output/n).read_bytes()).hexdigest() for n in ('README.md','study.json')}
            or r.get('source_sha256')!=index_sources()
            or json.loads((output/'study.json').read_bytes())!=current
            or (output/'README.md').read_text()!=readme(current,output)):
        raise ValueError('stale or altered capability migration')
    return r


def read_summary(output=OUTPUT):
    verify(output)
    return json.loads((Path(output)/'study.json').read_bytes())
