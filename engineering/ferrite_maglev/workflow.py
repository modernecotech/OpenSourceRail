"""Restartable build of implemented v0.5 studies; never an engineering release."""
from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from . import cities, coupled, delivery, evacuation, geometry, media, model, system_development, navigation, reference_assembly, iteration, station, station_structure, station_protocol, station_native, moving_train, system_campaign, closure, manufactured_native, corridor, booster_kit, booster_native, interchange_hubs, line_capacity, hub_access, qualification, assembled_body, shared_hub_layout,body_stiffness,stopped_recovery
from . import drive_design

BASE = model.ROOT/'docs/design-engine/ferrite-maglev'
STATE = model.ROOT/'build/maglev-workflow'


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.pending')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    os.replace(temporary, path)


@contextmanager
def locked(state=STATE):
    """Manual and timer builds share a non-blocking interprocess lock."""
    state = Path(state)
    state.mkdir(parents=True, exist_ok=True)
    with (state/'runner.lock').open('a') as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError('another primary build holds the runner lock') from exc
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def native():
    """Generate off to the side; copy only a complete verified owned packet."""
    inputs = [*geometry.configuration.source_paths(),Path(geometry.__file__), Path(media.__file__), model.ROOT/'engineering/factory_examples/native.py']
    before = {str(p):sha256(p.read_bytes()).hexdigest() for p in inputs}
    STATE.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='native-', dir=STATE) as temporary:
        target = Path(temporary)
        geometry.publish_native(target)
        for folder in ('interface', 'civil-bay'):
            media.native_views(target/folder)
        manifest = geometry.seal_native(target)
        if before != {str(p):sha256(p.read_bytes()).hexdigest() for p in inputs}:
            raise ValueError('native input sources changed during execution')
        install_packet(target, BASE/'native')
    return geometry.verify_native(BASE/'native')


def install_packet(target, output, *, marker='manifest.json'):
    """Install a verified staging packet, marker last; mixed old files can recover.

    Readers must verify the complete receipt before using a packet. A crash can
    leave mismatched old/new payload bytes, but the next fresh build can replace
    that bounded inventory without trusting the interrupted receipt.
    """
    target, output = Path(target), Path(output)
    if any(p.is_symlink() for p in target.rglob('*')) or not (target/marker).is_file():
        raise ValueError('ordinary verified staging packet required')
    expected = {p.relative_to(target).as_posix() for p in target.rglob('*') if p.is_file()}
    if output.is_symlink() or any(p.is_symlink() for p in output.rglob('*')):
        raise ValueError('symlink in owned packet output')
    actual = {p.relative_to(output).as_posix() for p in output.rglob('*') if p.is_file()}
    if actual-expected:
        raise ValueError('unexpected files in owned packet output')
    for name in [*sorted(expected-{marker}), marker]:
        destination = output/name
        destination.parent.mkdir(parents=True, exist_ok=True)
        os.replace(target/name, destination)


def fresh_packet(name, publisher, *, marker='manifest.json'):
    STATE.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=name+'-', dir=STATE) as temporary:
        target = Path(temporary)/'packet'
        publisher(target)
        install_packet(target, BASE/name, marker=marker)


def city_check():
    value = cities.verify_index()
    if not value['current']:
        raise ValueError('primary city inputs/outputs stale: '+str(value['errors'][:3]))
    return value


def report_check(output):
    value = delivery.verify(output)
    retained = json.loads((Path(output)/'result.json').read_text())
    if retained['runtime'] != delivery.runtime():
        raise ValueError('primary report runtime changed')
    return value


def stages(output):
    from . import pilot_product,pilot_actuators,launch_optimisation,pilot_corridor,pilot_variants,delivery_schedule,pilot_lifecycle,pilot_assurance,capability_migration,pilot_release
    from . import candidate_native,candidate_magnetics,candidate_structures,full_dynamics,candidate_manufacturing,candidate_lifecycle,bim_field,operations_crosscheck,platform_publication,planning_ui,detailed_system
    def document(script, *args):
        subprocess.run([sys.executable, str(model.ROOT/'tools/automation'/script), *args], cwd=model.ROOT, check=True, capture_output=True, text=True)
    values = [
        ('primary-host-configuration', lambda: document('validate-host-manifests.py'), lambda: document('validate-host-manifests.py')),
        ('native-interface-and-bay', lambda: geometry.verify_native(BASE/'native'), native),
        ('beam-only-kit', lambda: evacuation.verify_native(BASE/'beam-only'), lambda: fresh_packet('beam-only', evacuation.publish_native)),
        ('linked-mechanical-civil-software', system_development.verify, lambda: fresh_packet('system-development', system_development.publish)),
        ('coupled-controller-guideway', lambda: coupled.verify(BASE/'coupled'), lambda: fresh_packet('coupled', coupled.publish, marker='receipt.json')),
        ('station-launch-coast-receive',station.verify,lambda:fresh_packet('station-powered',station.publish)),
        ('gfrp-civil-production',station_structure.verify,lambda:fresh_packet('station-structure',station_structure.publish)),
        ('station-native-materials',station_native.verify,lambda:fresh_packet('station-native',station_native.publish)),
        ('rust-station-launch-protocol',station_protocol.verify,lambda:fresh_packet('station-protocol',station_protocol.publish)),
        ('support-and-launch-construction',drive_design.verify,lambda:fresh_packet('drive-construction',drive_design.publish)),
        ('adaptive-system-design', iteration.verify, lambda: fresh_packet('iterative', iteration.publish)),
        ('baghdad-six-car-reference',reference_assembly.verify,lambda: fresh_packet('baghdad-reference',reference_assembly.publish)),
        ('moving-six-car-twin',moving_train.verify,lambda:fresh_packet('moving-train',moving_train.publish)),
        ('integrated-station-system',system_campaign.verify,lambda:fresh_packet('system-campaign',system_campaign.publish)),
        ('urban-suburban-powered-corridors',corridor.verify,lambda:fresh_packet('corridor',corridor.publish)),
        ('fixed-booster-and-recovery-kit',booster_kit.verify,lambda:fresh_packet('booster-kit',booster_kit.publish)),
        ('booster-and-recovery-native',booster_native.verify,lambda:fresh_packet('booster-native',booster_native.publish)),
        ('manufactured-design-dossier',closure.verify,lambda:fresh_packet('manufactured-dossier',closure.publish)),
        ('manufactured-detail-native',manufactured_native.verify,lambda:fresh_packet('manufactured-native',manufactured_native.publish)),
        ('assembled-structural-body',assembled_body.verify,lambda:fresh_packet('assembled-body',assembled_body.publish)),
        ('body-longitudinal-stock-alternatives',body_stiffness.verify,lambda:fresh_packet('body-stiffness',body_stiffness.publish)),
        ('all-city-maglev-planning', city_check, cities.generate_all),
        ('baghdad-interchange-hub-investigation', interchange_hubs.verify, lambda: fresh_packet('interchange-hubs', interchange_hubs.publish)),
        ('sectioned-multitrain-capacity', line_capacity.verify, lambda: fresh_packet('line-capacity', line_capacity.publish)),
        ('stopped-controller-recovery',stopped_recovery.verify,lambda:fresh_packet('stopped-recovery',stopped_recovery.publish)),
        ('interchange-access-engineering', hub_access.verify, lambda: fresh_packet('hub-access', hub_access.publish)),
        ('shared-hub-station-geometry',shared_hub_layout.verify,lambda:fresh_packet('shared-hub-layout',shared_hub_layout.publish)),
        ('requirements-qualification-protocols', qualification.verify, lambda: fresh_packet('qualification', qualification.publish)),
        ('controlled-pilot-product',pilot_product.verify,lambda:fresh_packet('pilot-product',pilot_product.publish)),
        ('coupled-pilot-actuators',pilot_actuators.verify,lambda:fresh_packet('pilot-actuators',pilot_actuators.publish)),
        ('segmented-launch-optimisation',launch_optimisation.verify,lambda:fresh_packet('launch-optimisation',launch_optimisation.publish)),
        ('resource-constrained-pilot-delivery',delivery_schedule.verify,lambda:fresh_packet('delivery-schedule',delivery_schedule.publish)),
        ('baghdad-complete-pilot-corridor',pilot_corridor.verify,lambda:fresh_packet('pilot-corridor',pilot_corridor.publish)),
        ('exact-actuator-pilot-finance',pilot_variants.verify,lambda:fresh_packet('pilot-variants',pilot_variants.publish)),
        ('serial-pilot-business-lifecycle',pilot_lifecycle.verify,lambda:fresh_packet('pilot-lifecycle',pilot_lifecycle.publish)),
        ('dimensioned-candidate-magnetics',candidate_magnetics.verify,lambda:fresh_packet('candidate-magnetics',candidate_magnetics.publish)),
        ('native-dimensioned-candidate',candidate_native.verify,lambda:fresh_packet('candidate-native',candidate_native.publish)),
        ('candidate-loads-and-structures',candidate_structures.verify,lambda:fresh_packet('candidate-structures',candidate_structures.publish)),
        ('continued-candidate-fault-dynamics',full_dynamics.verify,lambda:fresh_packet('full-dynamics',full_dynamics.publish)),
        ('quantified-candidate-manufacturing',candidate_manufacturing.verify,lambda:fresh_packet('candidate-manufacturing',candidate_manufacturing.publish)),
        ('quantified-candidate-native-chain',candidate_lifecycle.verify,lambda:fresh_packet('candidate-lifecycle',candidate_lifecycle.publish)),
        ('candidate-bim-and-field-exchange',bim_field.verify,lambda:fresh_packet('bim-field',bim_field.publish)),
        ('independent-sumo-operations',operations_crosscheck.verify,lambda:fresh_packet('operations-crosscheck',operations_crosscheck.publish)),
        ('owner-builder-planning-platform',platform_publication.verify,lambda:fresh_packet('planning-platform',platform_publication.publish)),
        ('planning-browser-evidence',planning_ui.verify,lambda:fresh_packet('planning-ui',planning_ui.publish)),
        ('detailed-candidate-system',detailed_system.verify,lambda:fresh_packet('system-detailed',detailed_system.publish)),
        ('pilot-development-assurance',pilot_assurance.verify,lambda:fresh_packet('assurance-profiles',pilot_assurance.publish)),
        ('v04-capability-migration',capability_migration.verify,lambda:fresh_packet('capability-migration',capability_migration.publish)),
        ('connected-pilot-delivery',pilot_release.verify,lambda:fresh_packet('pilot-delivery',pilot_release.publish)),
        ('city-design-catalogue', lambda: document('generate-design-index.py','--check'), lambda: document('generate-design-index.py')),
        ('primary-capability-directory', lambda: navigation.publish(check=True), navigation.publish),
        ('primary-report', lambda: report_check(delivery.OUTPUT), lambda: delivery.publish()),
        ('primary-overview', lambda: document('generate-public-overview.py', '--check'), lambda: document('generate-public-overview.py')),
        ('markdown-inventory', lambda: document('generate-doc-index.py','--check'), lambda: document('generate-doc-index.py')),
        ('primary-reader-book', lambda: document('build-doc-book.py', '--check'), lambda: document('build-doc-book.py')),
    ]
    if Path(output).resolve() != delivery.OUTPUT.resolve():
        report_position = next(i for i, row in enumerate(values) if row[0]=='primary-report')
        values.insert(report_position+1, ('report-mirror', lambda: report_check(output), lambda: delivery.publish(output)))
    return values


def input_sources():
    """Guard standalone control and launcher inputs as well as primary sources."""
    values=model.sources(include_generated=False)
    # The migration register also binds browser checks outside model.sources().
    from . import capability_migration
    if (model.ROOT/'engineering/ferrite_maglev/data/pilot-capability-migration.json').is_file():
        values.update(capability_migration.sources())
    package=model.ROOT/'engineering/ferrite_maglev/observer-prototype'
    paths=[p for p in package.rglob('*') if p.is_file()
           and p.suffix in {'.rs','.py','.json','.toml','.lock','.h','.c'}
           and not any(part in {'target','__pycache__'} for part in p.parts)]
    launcher=model.ROOT/'tools/automation/osr-python'
    if launcher.is_file():paths.append(launcher)
    values.update({p.relative_to(model.ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in paths})
    return values


def run(output=delivery.OUTPUT, *, state=STATE, stage_list=None):
    """Reverify each dependency after restart; a failed build stops descendants."""
    state = Path(state)
    with locked(state):
        model.load()
        def input_identity():
            # Publication still hashes every retained output. The inter-stage
            # input guard excludes generated files before reading their bytes.
            return input_sources()
        source_identity = input_identity()
        def frozen():
            if input_identity() != source_identity:
                raise ValueError('input sources changed during primary build; restart required')
        journal = dict(schema='osr-maglev-workflow/1', state='running',
            started_utc=datetime.now(timezone.utc).isoformat(), stages=[],
            scope='Build all implemented digital studies; external acceptance and missing evaluators remain open',
            **model.FLAGS)
        path = state/'latest.json'
        write_json(path, journal)
        try:
            for name, verify, build in (stages(output) if stage_list is None else stage_list):
                frozen()
                entry = dict(id=name, state='checking')
                journal['stages'].append(entry)
                write_json(path, journal)
                try:
                    verify()
                    entry['state'] = 'verified-existing'
                except (ValueError, KeyError, FileNotFoundError, subprocess.CalledProcessError) as exc:
                    entry.update(state='building', refresh_reason=str(exc))
                    write_json(path, journal)
                    build()
                    frozen()
                    verify()
                    entry['state'] = 'rebuilt-and-verified'
                write_json(path, journal)
            frozen()
            journal['state'] = ('idle; sources unchanged' if all(s['state']=='verified-existing' for s in journal['stages'])
                                else 'implemented studies current; engineering closure open')
        except Exception as exc:
            journal['state'] = 'held'
            journal['error'] = str(exc)
            if isinstance(exc, subprocess.CalledProcessError):
                journal['error'] += ': '+(exc.stderr or exc.stdout or '')[-4000:]
            if journal['stages']:
                journal['stages'][-1].update(state='failed', error=str(exc))
            write_json(path, journal)
            raise
        journal['finished_utc'] = datetime.now(timezone.utc).isoformat()
        write_json(path, journal)
        return journal
