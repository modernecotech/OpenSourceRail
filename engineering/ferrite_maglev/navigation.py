"""Source-bound capability and city entrypoints for the current architecture."""
from hashlib import sha256
import json
from pathlib import Path
import os

from . import cities, model

OUTPUT = model.ROOT/'docs/capabilities'
CAPABILITIES = (
    ('city-planning', 'engineering/ferrite_maglev/cities.py', './osr city baghdad', 'Separate maglev formation, fleet, duty, charging and partial cost planning; no route acceptance.'),
    ('system-search', 'engineering/ferrite_maglev/optimisation.py', './osr design run', 'Vehicle/beam/span sensitivities and indexed allowances; complete costs and full coupling remain open.'),
    ('native-geometry', 'engineering/ferrite_maglev/geometry.py', './osr design native', 'Partial magnetic interface and civil-bay native solids; not complete production geometry.'),
    ('beam-only-egress', 'engineering/ferrite_maglev/evacuation.py', './osr design evacuation-native', 'Beam-only geometry and chute envelope/height screens; no evacuation approval.'),
    ('field-equations', 'engineering/ferrite_maglev/field.py', './osr design run', '2D field equation controls; coupon force convergence and qualified force/loss maps remain open.'),
    ('rust-control', 'crates/osr-maglev-control/Cargo.toml', 'cargo test --locked -p osr-maglev-control --all-targets', 'Fixed-module Rust control and advisory egress logic; no physical output authority.'),
    ('coupled-replay', 'engineering/ferrite_maglev/coupled.py', './osr design coupled', 'Two-way virtual Rust/vertical-beam replay; no qualified vehicle dynamics.'),
    ('linked-development', 'engineering/ferrite_maglev/system_development.py', './osr design system', 'Partial entry/support geometry, stage demands and geometry-bound software replays.'),
    ('dependency-runner', 'engineering/ferrite_maglev/workflow.py', './osr build', 'Restartable build of implemented studies; missing evaluators and acceptance remain open.'),
    ('primary-ui', 'tools/automation/maglev-workbench.py', './osr workbench', 'Read-only primary design UI, city plans, images and visibility videos; no hardware commands.'),
    ('development-host', 'deployment/maglev.toml', 'tools/automation/osr-python tools/automation/validate-host-manifests.py', 'Offline SBC development profile; no deployed host image or physical timing qualification.'),
)


def source_paths():
    return [model.ROOT/name for name in (
        'engineering/ferrite_maglev/navigation.py', 'tools/automation/capabilities.py',
        'tools/automation/catalogue.py', 'tools/automation/test-maglev.sh',
        'tools/automation/check-readmes.py', 'tools/automation/generate-doc-index.py',
        'tools/automation/generate-design-index.py',
        'tools/automation/validate-host-manifests.py', 'deployment/maglev.toml',
        'deployment/hosts.toml', 'deployment/components.toml')]


def identity():
    from . import transition
    paths = set(source_paths()+[model.POLICY,model.INPUT,model.SPEC,Path(model.__file__),cities.INDEX])
    paths.update(model.ROOT/source for _,source,_,_ in CAPABILITIES)
    paths.update(model.ROOT/name for name in transition.sources())
    return {p.relative_to(model.ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def capability_data():
    model.load()
    from . import transition
    register = transition.build()
    values = []
    for name, source, command, scope in CAPABILITIES:
        if not (model.ROOT/source).is_file():
            raise ValueError('missing primary capability source: '+source)
        values.append(dict(id=name, source=source, entry=command, scope=scope, engineering_accepted=False))
    return dict(schema='osr-primary-capabilities/1', family='ferrite-pm-maglev-study',
        capabilities=values, source_sha256=identity(),
        inventory=dict(primary_capabilities=len(values), **register['inventory_counts']),
        accepted_item_count=0, **model.FLAGS)


def city_index(*, require_current=True):
    model.load()
    status = cities.verify_index()
    if require_current and not status['current']:
        raise ValueError('primary city catalogue stale; run ./osr design catalogue')
    index = json.loads(cities.INDEX.read_text())
    if index.get('architecture')!='ferrite-pm-maglev-study' or index.get('physical_release') is not False:
        raise ValueError('primary city index architecture/release differs')
    return dict(schema='osr-maglev-city-artifact-index/1', family=index['architecture'],
        source_current=status['current'], city_count=index['city_count'],
        source_index_sha256=sha256(cities.INDEX.read_bytes()).hexdigest(),
        cities={row['city']:dict(name=row['name'], package_path=row['package_path'],
            summary_sha256=row['summary_sha256'], trainsets=row['trainsets'], cars=row['cars'],
            open_gate_count=row['open_gate_count'], complete_city_programme_usd=None,
            physical_release=False) for row in index['cities']},
        payloads_deleted=False, **model.FLAGS)


def selected_plan(slugs):
    if not slugs or len(slugs) != len(set(slugs)):
        raise ValueError('choose distinct existing city slugs')
    # Resolve the complete selection before any write; require an explicit current city input.
    directories = {slug:cities.find_city(slug) for slug in slugs}
    return dict(schema='osr-maglev-selected-city-generation/1', family='ferrite-pm-maglev-study',
        selected=list(slugs), commands=[['./osr','city',slug] for slug in directories],
        unchanged_scope='unselected primary maglev packages',
        unselected_unchanged_required=True, baseline_adoption_permitted=False, **model.FLAGS)


def run_selected(slugs, *, output=None):
    from . import workflow
    plan = selected_plan(slugs)
    with workflow.locked():
        # Hash owned city packages so selection cannot mutate another city.
        unselected = [p.parent/'engineering/maglev' for p in (model.ROOT/'cities/catalogue').glob('*/*/*/city.json')
            if cities.city_slug(p) not in slugs]
        def snapshot():
            return {p:sha256(p.read_bytes()).hexdigest() for folder in unselected for p in folder.rglob('*') if p.is_file()}
        before = snapshot()
        completed = []
        for slug in slugs:
            target = None if output is None else Path(output)/slug
            result = cities.generate(cities.find_city(slug), output_dir=target)
            completed.append(dict(city=result['city'], physical_release=False))
        if snapshot()!=before:
            raise ValueError('selected generation changed an unselected primary package')
    return dict(**plan, completed=completed, global_catalogue_current=cities.verify_index()['current'])


def publish(output=OUTPUT, *, check=False):
    output = Path(output)
    data = capability_data()
    def link(name):
        return Path(os.path.relpath(model.ROOT/name, output)).as_posix().replace(' ', '%20')
    lines = ['# Primary maglev capability directory', '',
        'Implemented digital capabilities for v0.5. Every engineering/physical acceptance gate remains open.', '',
        '| Capability | Entry | Implemented scope |', '|---|---|---|']
    lines += [f"| [{r['id']}]({link(r['source'])}) | `{r['entry']}` | {r['scope']} |" for r in data['capabilities']]
    lines += ['', 'Selected city rebuild: `./osr catalogue run --city <slug>`.', '']
    files = {'ledger.json':json.dumps(data,indent=2,sort_keys=True)+'\n', 'directory.md':'\n'.join(lines),
        'README.md':'# Capability Directory\n\nGenerated by `./osr capabilities` for the primary ferrite-PM maglev architecture.\n\n[Capabilities and commands](directory.md) · [Source-bound ledger](ledger.json) · [Primary city packages](city-artifacts.json).\n',
        'city-artifacts.json':json.dumps(city_index(),indent=2,sort_keys=True)+'\n'}
    for name, value in files.items():
        path = output/name
        if check:
            if not path.is_file() or path.read_text()!=value:
                raise ValueError('primary capability directory differs: '+name)
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            temporary=path.with_suffix(path.suffix+'.pending')
            temporary.write_text(value);os.replace(temporary,path)
    return data
