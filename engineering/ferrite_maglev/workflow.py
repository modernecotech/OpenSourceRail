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

from . import cities, coupled, delivery, evacuation, geometry, media, model, system_development, navigation, reference_assembly, iteration

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
    def document(script, *args):
        subprocess.run([sys.executable, str(model.ROOT/'tools/automation'/script), *args], cwd=model.ROOT, check=True, capture_output=True, text=True)
    values = [
        ('primary-host-configuration', lambda: document('validate-host-manifests.py'), lambda: document('validate-host-manifests.py')),
        ('native-interface-and-bay', lambda: geometry.verify_native(BASE/'native'), native),
        ('beam-only-kit', lambda: evacuation.verify_native(BASE/'beam-only'), lambda: fresh_packet('beam-only', evacuation.publish_native)),
        ('linked-mechanical-civil-software', system_development.verify, lambda: fresh_packet('system-development', system_development.publish)),
        ('coupled-controller-guideway', lambda: coupled.verify(BASE/'coupled'), lambda: fresh_packet('coupled', coupled.publish, marker='receipt.json')),
        ('adaptive-system-design', iteration.verify, lambda: fresh_packet('iterative', iteration.publish)),
        ('baghdad-six-car-reference',reference_assembly.verify,lambda: fresh_packet('baghdad-reference',reference_assembly.publish)),
        ('all-city-maglev-planning', city_check, cities.generate_all),
        ('primary-capability-directory', lambda: navigation.publish(check=True), navigation.publish),
        ('markdown-inventory', lambda: document('generate-doc-index.py','--check'), lambda: document('generate-doc-index.py')),
        ('primary-report', lambda: report_check(delivery.OUTPUT), lambda: delivery.publish()),
        ('primary-overview', lambda: document('generate-public-overview.py', '--check'), lambda: document('generate-public-overview.py')),
        ('primary-reader-book', lambda: document('build-doc-book.py', '--check'), lambda: document('build-doc-book.py')),
    ]
    if Path(output).resolve() != delivery.OUTPUT.resolve():
        report_position = next(i for i, row in enumerate(values) if row[0]=='primary-report')
        values.insert(report_position+1, ('report-mirror', lambda: report_check(output), lambda: delivery.publish(output)))
    return values


def run(output=delivery.OUTPUT, *, state=STATE, stage_list=None):
    """Reverify each dependency after restart; a failed build stops descendants."""
    state = Path(state)
    with locked(state):
        model.load()
        def input_identity():
            return {name:digest for name,digest in model.sources().items()
                if '/engineering/maglev/' not in name and not name.startswith('engineering/ferrite_maglev/city-index.')
                and not (name.startswith('cities/catalogue/') and name.endswith('/README.md'))}
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
