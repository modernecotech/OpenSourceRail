"""Independent exact OpenCASCADE STEP measurements through existing FreeCAD.

This worker measures imported geometry only.  It never creates replacement CAD,
applies display offsets, assigns materials or grants engineering acceptance.
"""
import hashlib
import json
import math
import os
from pathlib import Path
import re
import resource
import shutil
import signal
import stat
import subprocess
import time

FLAGS = dict(physical_accepted=False, engineering_accepted=False,
             manufacturing_release=False, operating_release=False,
             selected_reference_changed=False, movement_authority=False)

WORKER = r'''import json, math, resource, time, traceback
from pathlib import Path
import FreeCAD as App
import Part, Import

root = Path(__file__).resolve().parent
request = json.loads((root/'input.json').read_text())
started = time.monotonic()
doc = None
result = dict(schema='osr-freecad-step-reference/1', execution='failed',
              FreeCAD_version=list(App.Version()),
              OpenCASCADE_version=str(getattr(Part, 'OCC_VERSION', 'unknown')),
              native_units=dict(length='mm', area='mm2', volume='mm3'),
              units=dict(length='m', area='m2', volume='m3'),
              measurement_method='Exact imported OpenCASCADE B-rep; no tessellation',
              display_offsets_applied=False, installed_mass_complete=False,
              physical_accepted=False, engineering_accepted=False,
              manufacturing_release=False, operating_release=False,
              selected_reference_changed=False, movement_authority=False)
try:
    doc = App.newDocument('IndependentSTEPReference')
    Import.insert(str(root/'input.step'), doc.Name)
    doc.recompute()
    bodies = []
    imported = []
    for obj in doc.Objects:
        imported.append(dict(name=obj.Name, label=obj.Label, type_id=obj.TypeId))
        if not obj.isDerivedFrom('Part::Feature') or not hasattr(obj, 'Shape'):
            continue
        shape = obj.Shape
        if shape.isNull():
            continue
        solids = shape.Solids
        conservative_box = shape.BoundBox
        box = shape.optimalBoundingBox(False, False)
        center = shape.CenterOfMass
        bodies.append(dict(id=obj.Label, native_name=obj.Name, type_id=obj.TypeId,
            shape_type=shape.ShapeType, solid_count=len(solids),
            valid=bool(shape.isValid()), closed=bool(shape.isClosed()),
            all_solids_closed_valid=bool(solids) and all(s.isClosed() and s.isValid() and s.Volume > 0 for s in solids),
            volume_m3=shape.Volume*1e-9, area_m2=shape.Area*1e-6,
            center_of_mass_m=[center.x*.001, center.y*.001, center.z*.001],
            bbox_m=dict(min=[box.XMin*.001, box.YMin*.001, box.ZMin*.001],
                        max=[box.XMax*.001, box.YMax*.001, box.ZMax*.001]),
            bbox_method='OpenCASCADE optimalBoundingBox(False, False); no triangulation',
            conservative_bbox_m=dict(
                min=[conservative_box.XMin*.001, conservative_box.YMin*.001, conservative_box.ZMin*.001],
                max=[conservative_box.XMax*.001, conservative_box.YMax*.001, conservative_box.ZMax*.001]),
            mass_kg=None))
    bodies.sort(key=lambda row: row['id'])
    result.update(execution='completed', bodies=bodies, imported_objects=imported,
                  body_count=len(bodies), total_volume_m3=sum(b['volume_m3'] for b in bodies))
except BaseException as error:
    result.update(error=dict(type=type(error).__name__, message=str(error)),
                  traceback=traceback.format_exc())
finally:
    result['native_wall_seconds'] = time.monotonic()-started
    usage = resource.getrusage(resource.RUSAGE_SELF)
    result['native_process_usage'] = dict(peak_rss_kib=usage.ru_maxrss,
        user_cpu_seconds=usage.ru_utime, system_cpu_seconds=usage.ru_stime,
        actual_address_space_limit_bytes=list(resource.getrlimit(resource.RLIMIT_AS)))
    if doc is not None:
        App.closeDocument(doc.Name)
    (root/'measurement.json').write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False)+'\n')
'''


def _write(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n')


def _file(path):
    path = Path(path).absolute()
    if not stat.S_ISREG(path.lstat().st_mode) or path.is_symlink():
        raise ValueError('Ordinary STEP input file required')
    return path


def _step_brep_names(path):
    """Read literal STEP B-rep names, without asserting an importer mapping."""
    text = Path(path).read_text(encoding='latin1')
    pattern = r"#(\d+)\s*=\s*MANIFOLD_SOLID_BREP\s*\(\s*'((?:[^']|'')*)'\s*,\s*#(\d+)\s*\)\s*;"
    return [dict(step_entity_id=int(entity), name=name.replace("''", "'"), shell_entity_id=int(shell))
            for entity, name, shell in re.findall(pattern, text)]


def _expected(value):
    if value is None:
        return None
    if not isinstance(value, (list, tuple)) or not value or len(value) > 3500:
        raise ValueError('Bounded nonempty expected body IDs required')
    if any(not isinstance(v, str) or not v or len(v) > 512 or any(ord(c) < 32 for c in v) for v in value):
        raise ValueError('Printable expected body IDs required')
    if len(set(value)) != len(value):
        raise ValueError('Unique expected body IDs required')
    return sorted(value)


def validate_measurements(value, expected_body_ids=None):
    """Check exact solid measurements and optionally the source ID bijection."""
    expected = _expected(expected_body_ids)
    if not isinstance(value, dict) or value.get('execution') != 'completed':
        raise ValueError('Native STEP measurement did not complete')
    bodies = value.get('bodies')
    if not isinstance(bodies, list) or not bodies or value.get('body_count') != len(bodies):
        raise ValueError('Nonempty native material body records required')
    ids = [b.get('id') for b in bodies]
    if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
        raise ValueError('Native material body IDs must be unique')
    if expected is not None and sorted(ids) != expected:
        raise ValueError('STEP source occurrence identity/count differs')
    for body in bodies:
        if (body.get('valid') is not True or body.get('closed') is not True
                or body.get('all_solids_closed_valid') is not True or body.get('solid_count') != 1):
            raise ValueError('Each named material occurrence must be one closed valid solid')
        numbers = [body.get('volume_m3'), body.get('area_m2')]
        for key in ('center_of_mass_m',):
            vector = body.get(key)
            if not isinstance(vector, list) or len(vector) != 3:
                raise ValueError('Explicit SI center coordinates required')
            numbers.extend(vector)
        bbox = body.get('bbox_m')
        if not isinstance(bbox, dict):
            raise ValueError('Explicit SI native bounds required')
        for key in ('min', 'max'):
            vector = bbox.get(key)
            if not isinstance(vector, list) or len(vector) != 3:
                raise ValueError('Explicit SI native bounds required')
            numbers.extend(vector)
        if any(type(n) not in (int, float) or not math.isfinite(n) for n in numbers):
            raise ValueError('Finite native material quantities required')
        if numbers[0] <= 0 or numbers[1] <= 0 or any(a >= b for a, b in zip(bbox['min'], bbox['max'])):
            raise ValueError('Positive material solid quantities required')
        if any(not a <= c <= b for a, c, b in zip(bbox['min'], body['center_of_mass_m'], bbox['max'])):
            raise ValueError('Native material center lies outside its bounds')
        if body.get('mass_kg') is not None:
            raise ValueError('STEP volume does not establish installed mass')
    total = value.get('total_volume_m3')
    if (type(total) not in (int, float) or not math.isfinite(total)
            or not math.isclose(total, sum(b['volume_m3'] for b in bodies), rel_tol=1e-12, abs_tol=1e-15)):
        raise ValueError('Native material total differs from its occurrences')
    if any(value.get(k) is not False for k in FLAGS):
        raise ValueError('STEP measurements cannot grant acceptance or authority')
    return value


def run(step_path, output_directory, timeout_s=120, memory_mb=2048, *, expected_body_ids=None):
    """Measure STEP using one Flatpak FreeCADCmd process; retain every execution.

    The address-space limit is inherited per process, not a cgroup aggregate.
    Timeout terminates the launched process group. Flatpak home/host permission
    overrides and a private output grant reduce filesystem access; they are not
    a claim of a separate host-wide verifier or an immutable external tool.
    """
    if type(timeout_s) not in (int, float) or not math.isfinite(timeout_s) or not 1 <= timeout_s <= 600:
        raise ValueError('STEP reference timeout must be 1–600 seconds')
    if type(memory_mb) is not int or not 256 <= memory_mb <= 8192:
        raise ValueError('STEP reference memory budget must be 256–8192 MiB')
    expected = _expected(expected_body_ids)
    step = _file(step_path)
    output = Path(output_directory).absolute()
    if output.is_symlink() or (output.exists() and (not output.is_dir() or any(output.iterdir()))):
        raise ValueError('Fresh private STEP reference directory required')
    flatpak = shutil.which('flatpak')
    timer = shutil.which('time')
    if flatpak is None or timer is None:
        raise ValueError('FreeCAD Flatpak and GNU time launchers required')
    output.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(step.read_bytes()).hexdigest()
    shutil.copyfile(step, output/'input.step')
    copied = hashlib.sha256((output/'input.step').read_bytes()).hexdigest()
    if copied != digest:
        raise ValueError('STEP changed during immutable input copy')
    _write(output/'input.json', dict(source_step_path=str(step), source_sha256=digest,
                                   expected_body_ids=expected))
    (output/'worker.py').write_text(WORKER)
    command = [timer, '-f', '{"wall_seconds":%e,"user_cpu_seconds":%U,"system_cpu_seconds":%S,"peak_rss_kib":%M,"exit_code":%x}',
               '-o', str(output/'resource.json'), flatpak, 'run', '--unshare=network',
               '--nofilesystem=host', '--nofilesystem=home', '--filesystem='+str(output),
               '--env=QT_QPA_PLATFORM=offscreen', '--env=OMP_NUM_THREADS=1',
               '--env=XDG_CONFIG_HOME='+str(output/'config'),
               '--env=XDG_CACHE_HOME='+str(output/'cache'),
               '--command=sh', 'org.freecad.FreeCAD', '-c',
               'ulimit -v '+str(memory_mb*1024)+' && exec FreeCADCmd "$1"',
               'osr-freecad-reference', str(output/'worker.py')]
    limits = dict(timeout_s=timeout_s, per_process_address_space_mib=memory_mb,
                  cpu_threads_requested=1, process_group_timeout=True,
                  aggregate_cgroup_memory_limit=False,
                  address_space_limit_set_inside_sandbox=True)
    _write(output/'command.json', dict(argv=command, limits=limits))
    def limit():
        amount = memory_mb*1024*1024
        resource.setrlimit(resource.RLIMIT_AS, (amount, amount))
    start = time.monotonic()
    execution, returncode, error = 'failed', None, None
    with (output/'stdout.log').open('wb') as stdout, (output/'stderr.log').open('wb') as stderr:
        try:
            process = subprocess.Popen(command, cwd=output, stdout=stdout, stderr=stderr,
                                       start_new_session=True, preexec_fn=limit)
            try:
                returncode = process.wait(timeout=timeout_s)
            except subprocess.TimeoutExpired:
                execution = 'timeout'
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                returncode = process.wait()
            else:
                execution = 'completed' if returncode == 0 else 'failed'
        except OSError as exc:
            error = dict(type=type(exc).__name__, message=str(exc))
    usage = dict(coordinator_wall_seconds=time.monotonic()-start)
    try:
        # GNU time can prefix diagnostics when a child is signalled.
        lines = (output/'resource.json').read_text().splitlines()
        usage['launcher_process'] = json.loads(next(line for line in reversed(lines) if line.startswith('{')))
    except (OSError, ValueError, StopIteration):
        usage['child_resource_measurement_available'] = False
    native = None
    try:
        native = json.loads((output/'measurement.json').read_text())
        validate_measurements(native, expected)
        actual = native.get('native_process_usage', {}).get('actual_address_space_limit_bytes')
        if actual != [memory_mb*1024*1024]*2:
            raise ValueError('Native FreeCAD address-space limit was not independently observed')
    except (OSError, ValueError, TypeError) as exc:
        if execution == 'completed':
            execution = 'failed'
        error = dict(type=type(exc).__name__, message=str(exc))
    result = dict(schema='osr-freecad-step-execution/1', execution=execution,
                  returncode=returncode, error=error, source_step_sha256=digest,
                  worker_sha256=hashlib.sha256(WORKER.encode()).hexdigest(),
                  expected_body_ids=expected,
                  source_step_brep_name_records=_step_brep_names(output/'input.step'),
                  step_brep_name_to_native_body_mapping='Not established; native labels are retained verbatim',
                  limits=limits, usage=usage, native=native,
                  bodies=native.get('bodies', []) if native else [],
                  total_volume_m3=native.get('total_volume_m3') if native else None,
                  installed_mass_complete=False, **FLAGS)
    if native and isinstance(native.get('native_process_usage'), dict):
        usage['native_process'] = native['native_process_usage']
        usage['peak_rss_kib'] = native['native_process_usage'].get('peak_rss_kib')
        usage['launcher_usage_includes_native_process'] = False
    _write(output/'result.json', result)
    return result
