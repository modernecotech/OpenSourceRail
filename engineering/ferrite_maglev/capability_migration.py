"""Evidence-based v0.4 capability migration, without restoring its wheelset design."""
from hashlib import sha256
import json
import os
from pathlib import Path

from . import model, pilot_assurance

INPUT = Path(__file__).parent/'data/pilot-capability-migration.json'
OUTPUT = model.ROOT/'docs/design-engine/ferrite-maglev/capability-migration'
SCHEMA = 'osr-maglev-capability-migration/1'
STATES = {'retained-and-tested','retained-but-unconnected','replaced','deliberately-retired','missing'}


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
    return dict(schema=SCHEMA,baseline=value['baseline'],capabilities=rows,
                state_counts={s:sum(r['state']==s for r in rows) for s in sorted(STATES)},
                products=value['products'],source_sha256=sources(),
                scope='Migration of the actual v0.4 feature table. Tested scope is stated per row; missing features are not marked complete.',
                **model.FLAGS)


def readme(value):
    def link(name):
        return Path(os.path.relpath(model.ROOT/name,OUTPUT)).as_posix()
    lines=['# v0.4 capability migration to station-powered maglev','',value['scope'],'',
           'Baseline: v0.4.0 commit `'+value['baseline']['commit']+'`, README feature table. Historical product quantities and wheelset geometry are not current inputs.','',
           '| Capability | Disposition | Accountable function | Current evidence and limits |', '|---|---|---|---|']
    for r in value['capabilities']:
        evidence='; '.join(f'[{Path(p).name}]({link(p)})' for p in r['current_sources'])
        lines.append(f"| {r['title']} | {r['state']} | {r['owner']} | {r['decision']} {evidence} |")
    lines+=['','## Three products','']
    for row in value['products']:
        lines += [f"**{row['name']}** — {row['boundary']} {row['first_adoptable']}",'']
    lines+=['The first adoptable product is the simulated owner/builder/operator delivery workflow. It may be used for controlled planning and training before rolling-stock certification; legal entities, calendars, permissions and real equipment bindings remain deployment inputs.',
            'The read-only maglev evidence Workbench and the authenticated native lifecycle application have different responsibilities. Neither grants movement authority or accepts manufactured hardware.','']
    return '\n'.join(lines)


def publish(output=OUTPUT):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);value=study()
    files={'study.json':encoded(value),'README.md':readme(value).encode()}
    for name,data in files.items():(output/name).write_bytes(data)
    receipt=dict(schema=SCHEMA,source_sha256=value['source_sha256'],files_sha256={n:sha256(d).hexdigest() for n,d in files.items()},**model.FLAGS)
    (output/'manifest.json').write_bytes(encoded(receipt));return receipt


def verify(output=OUTPUT):
    output=Path(output);r=json.loads((output/'manifest.json').read_bytes())
    current=study()
    if (output.is_symlink() or r['schema']!=SCHEMA or any(r.get(k) is not False for k in model.FLAGS)
            or set(p.name for p in output.iterdir())!={'README.md','study.json','manifest.json'}
            or any(p.is_symlink() for p in output.iterdir())
            or r['files_sha256']!={n:sha256((output/n).read_bytes()).hexdigest() for n in ('README.md','study.json')}
            or r.get('source_sha256')!=sources()
            or json.loads((output/'study.json').read_bytes())!=current
            or (output/'README.md').read_text()!=readme(current)):
        raise ValueError('stale or altered capability migration')
    return r


def read_summary(output=OUTPUT):
    verify(output)
    return json.loads((Path(output)/'study.json').read_bytes())
