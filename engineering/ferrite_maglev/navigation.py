"""Source-bound capability and city entrypoints for the current architecture."""
from hashlib import sha256
import json
from pathlib import Path
import os

from . import cities, model

OUTPUT = model.ROOT/'docs/capabilities'
CAPABILITIES = (
    ('trip-research-tools','engineering/trip_dynamics/README.md','./osr trip','Local Workbench and CLI for source-bound vehicle/equipment comparisons, bounded private journey jobs, fixtures, solver setup, model imports and logs; candidate evidence preflights and ideal-support Chrono benchmarks retain separate meanings.'),
    ('detailed-system','engineering/ferrite_maglev/detailed_system.py','./osr design detailed-system','Exact candidate geometry,magnetics,dynamics,structures,quantitative manufacturing,native chain,BIM and economics; mandatory failures block adoption.'),
    ('owner-builder-planning','engineering/ferrite_maglev/platform_publication.py','./osr plan serve','Editable city stop/service/OD proposals,16GISlayers,immutable revisions,generic resource/procurement/monthlycash adapter and native owner/builder/operator navigation.'),
    ('independent-operations','engineering/ferrite_maglev/operations_crosscheck.py','./osr design operations-crosscheck','Executed independent SUMO railway blocks,dwell/receiverdelay and capacitynegativecontrols; kinematic timing, notmagneticforce orphysicalGoA4 qualification.'),
    ('connected-pilot-delivery','engineering/ferrite_maglev/pilot_release.py','./osr design pilot-delivery','Connected product, actuator, launch search, pilot delivery/finance, serial lifecycle, migration and executed development profiles. Engineering failures and physical gates remain visible.'),
    ('controlled-pilot-product','engineering/ferrite_maglev/pilot_product.py','./osr design pilot-product','Scope-exclusive mass/cost/space ledger and equipped-bay variants; target overruns are not hidden.'),
    ('coupled-pilot-actuators','engineering/ferrite_maglev/pilot_actuators.py','./osr design pilot-actuators','Actual Rust current kernels with bounded voltage/current/force/beam/sensing and thermal/DC accounting; unqualified plant maps.'),
    ('segmented-launch-search','engineering/ferrite_maglev/launch_optimisation.py','./osr design launch-optimisation','Separate energised sections, conductor/voltage candidates and lifecycle cost, including extra cabinets and maintenance.'),
    ('pilot-corridor-finance','engineering/ferrite_maglev/pilot_corridor.py','./osr design pilot-corridor','Declared access/demand proxies, full pilot service/failures, monthly procurement cash, revenue/DSCR and independent comparison quantities.'),
    ('resource-delivery','engineering/ferrite_maglev/delivery_schedule.py','./osr design delivery-schedule','Resource-constrained1km construction, procurement and origin-accounted pooled factory/training.'),
    ('exact-actuator-pilot-finance','engineering/ferrite_maglev/pilot_variants.py','./osr design pilot-variants','Separate cost, full-line service and finance for the exact executed steel/higher-copper actuator configuration; no cheaper alternative is substituted.'),
    ('serial-pilot-lifecycle','engineering/ferrite_maglev/pilot_lifecycle.py','./osr design pilot-lifecycle','Simulated serial-specific native ERPNext/FUXA/Workbench chain; business records never accept hardware.'),
    ('pilot-assurance','engineering/ferrite_maglev/pilot_assurance.py','./osr design pilot-assurance','Separate engineering, delivery-lifecycle and control-formal execution profiles, source-pinned raw logs and project-wide evidence graph.'),
    ('v04-capability-migration','engineering/ferrite_maglev/capability_migration.py','./osr design capability-migration','Actual v0.4 feature dispositions and three-product scope with explicit missing capabilities.'),
    ('city-planning', 'engineering/ferrite_maglev/cities.py', './osr city baghdad', 'Detailed PM-maglev city briefs, formation, fleet, duty, charging, manufacture and CAPEX/OPEX/debt sensitivities; complete costs, financing and route acceptance remain open.'),
    ('system-search', 'engineering/ferrite_maglev/optimisation.py', './osr design run', 'Vehicle/beam/span sensitivities and indexed allowances; complete costs and full coupling remain open.'),
    ('adaptive-search', 'engineering/ferrite_maglev/iteration.py', './osr design iterate', 'Result-guided vehicle/beam/Rust gain variants and separate holdout confirmation; research recommendation only.'),
    ('station-propulsion','engineering/ferrite_maglev/station.py','./osr design station','Jerk-limited launch/coast/receive, actual-band overlap, headway and corrected services charging; no qualified motor map.'),
    ('gfrp-civil-product','engineering/ferrite_maglev/station_structure.py','./osr design structure','Panel/civil quantity, finite-dipole reference and production-target studies; no manufactured release.'),
    ('station-protocol','engineering/ferrite_maglev/station_protocol.py','./osr design protocol','Executed Rust station replay and durable atomic launch tests; local offline domain only.'),
    ('support-and-launch-construction','engineering/ferrite_maglev/drive_design.py','./osr design drives','Counted support/LSM windings, power electronics, sensors, connections and British supplier references; executed Rust current/commutation coupons, with magnetic maps, hardware and integrated actuator dynamics still open.'),
    ('moving-six-car','engineering/ferrite_maglev/moving_train.py','./osr design moving','Moving six-car ideal-force Rust/beam/coupler studies, refinement and motion animation; physical qualification open.'),
    ('integrated-station','engineering/ferrite_maglev/system_campaign.py','./osr design campaign','Actual local interlocking-to-station control, full-tail ownership, fault cases and independent recovery sizing.'),
    ('fixed-powered-corridors','engineering/ferrite_maglev/corridor.py','./osr design corridor','Finite station/booster urban/suburban trajectories, actual offline Rust control and moving confirmations; electrical, reserve and capacity holds remain explicit.'),
    ('interchange-hubs','engineering/ferrite_maglev/interchange_hubs.py','./osr design interchange-hubs','Bounded Baghdad hub, accessible connector and realignment alternatives; unchanged default and unqualified costs, capacity and sites remain explicit.'),
    ('sectioned-line-capacity','engineering/ferrite_maglev/line_capacity.py','./osr design line-capacity','Actual Rust progressive reservations for several trains, stopping-distance envelopes and adverse controls; local study only, without city or safety acceptance.'),
    ('interchange-access-engineering','engineering/ferrite_maglev/hub_access.py','./osr design hub-access','Counted access structures, pedestrian/lift pulse models and outage comparisons; site, structure and passenger acceptance remain open.'),
    ('qualification-protocols','engineering/ferrite_maglev/qualification.py','./osr design qualification','Requirement-specific dependency tasks, raw physical-evidence schemas and fail-closed ingestion; preparation and simulations do not close physical gates.'),
    ('assembled-structural-body','engineering/ferrite_maglev/assembled_body.py','./osr design assembled-body','Placed structural material regions, native interference controls and geometry-derived partial mass/inertia; omitted equipment and physical qualification stay explicit.'),
    ('body-longitudinal-stock-alternatives','engineering/ferrite_maglev/body_stiffness.py','./osr design body-stiffness','Exact drilled longitudinal-stock and spacer changes with added full-AW3 mass in actual Rust moving sensitivities; unchanged phase criterion, no joined-body or default adoption.'),
    ('shared-hub-station-geometry','engineering/ferrite_maglev/shared_hub_layout.py','./osr design shared-hub-layout','Fitted station tangents and bounded transitions, door-to-door circulation and explicitly counted new geometry; no site or operating approval.'),
    ('stopped-controller-recovery','engineering/ferrite_maglev/stopped_recovery.py','./osr design stopped-recovery','Actual local stopped reconciliation, pinned model, fresh whole-consist proofs and new contracts; moving recovery, distributed handover and physical acceptance remain open.'),
    ('portable-study-bundles','engineering/ferrite_maglev/release_bundle.py','tools/automation/osr-python tools/automation/package-maglev-release.py --output build/release-bundle','Streaming, bounded multipart archives with exact committed inputs, independent part checks and no physical-release authority.'),
    ('booster-recovery-kit','engineering/ferrite_maglev/booster_kit.py','./osr design booster-kit','Counted powered-zone mounts and independently equipped recovery alternatives with foundations, energy, mass and unquoted costs.'),
    ('booster-recovery-native','engineering/ferrite_maglev/booster_native.py','./osr design booster-native','Reopened partial booster/rescue stock solids, native mesh, image and visibility video; not a qualified assembled installation.'),
    ('manufactured-dossier','engineering/ferrite_maglev/closure.py','./osr design dossier','Counted frame/connection/handling/prestress/bearing/brake/foundation candidates and all-obligation evidence map; no release.'),
    ('manufactured-native','engineering/ferrite_maglev/manufactured_native.py','./osr build','Reopened native frame cut-stock and connection details with quantities and visibility media.'),
    ('station-native','engineering/ferrite_maglev/station_native.py','./osr build','Actual FreeCAD/STEP, PNG and visibility video for partial GFRP/civil material stock.'),
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
        'tools/automation/generate-design-index.py', 'tools/automation/package-maglev-release.py',
        'tools/automation/validate-host-manifests.py', 'tools/automation/retain-pilot-ui.py', 'deployment/maglev.toml',
        'deployment/hosts.toml', 'deployment/components.toml',
        'docs/workbench/trip/index.html', 'docs/workbench/trip/app.js', 'docs/workbench/trip/app.css',
        'tools/automation/tests/verify-trip-workbench.mjs',
        'engineering/trip_dynamics/interactive.py', 'engineering/trip_dynamics/interactive_worker.py',
        'engineering/trip_dynamics/experiments.py', 'engineering/trip_dynamics/setup_tools.py',
        'engineering/trip_dynamics/interface_integrity.py', 'engineering/trip_dynamics/__main__.py')]


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
