import importlib.util
import json
from pathlib import Path
import subprocess

import pytest

PATH = Path(__file__).resolve().parents[1]/'engineering/design_search/craft_backends/freecad_reference.py'
SPEC = importlib.util.spec_from_file_location('freecad_reference', PATH)
backend = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(backend)


def measurement():
    return dict(execution='completed', body_count=1,
        bodies=[dict(id='source/body', native_name='Part', valid=True, closed=True,
            all_solids_closed_valid=True, solid_count=1, volume_m3=.006,
            area_m2=.22, center_of_mass_m=[1.05, 2.1, 3.15],
            bbox_m=dict(min=[1., 2., 3.], max=[1.1, 2.2, 3.3]), mass_kg=None)],
        total_volume_m3=.006, FreeCAD_version=['1', '1', '0'],
        native_process_usage=dict(peak_rss_kib=112040,
            actual_address_space_limit_bytes=[2147483648, 2147483648]), **backend.FLAGS)


def test_exact_material_occurrences_require_source_id_bijection():
    value = measurement()
    assert backend.validate_measurements(value, ['source/body']) is value
    with pytest.raises(ValueError, match='identity/count'):
        backend.validate_measurements(value, ['different'])


@pytest.mark.parametrize('edit', [
    lambda x: x['bodies'][0].update(valid=False),
    lambda x: x['bodies'][0].update(closed=False),
    lambda x: x['bodies'][0].update(solid_count=2),
    lambda x: x['bodies'][0].update(volume_m3=float('nan')),
    lambda x: x['bodies'][0].update(mass_kg=1),
    lambda x: x['bodies'][0].update(center_of_mass_m=[0, 0, 0]),
    lambda x: x.update(total_volume_m3=0),
    lambda x: x.update(physical_accepted=True),
])
def test_unknown_invalid_or_promoted_material_cannot_pass(edit):
    value = measurement()
    edit(value)
    with pytest.raises(ValueError):
        backend.validate_measurements(value)


def test_worker_imports_exact_geometry_without_replacement_or_offsets():
    assert 'Import.insert' in backend.WORKER
    assert 'shape.Volume*1e-9' in backend.WORKER
    assert 'shape.CenterOfMass' in backend.WORKER
    assert 'shape.BoundBox' in backend.WORKER
    assert 'id=obj.Label' in backend.WORKER
    assert 'Part.make' not in backend.WORKER
    assert 'tessellate(' not in backend.WORKER
    assert 'render_offset_m' not in backend.WORKER


def mock_process(monkeypatch, mode='ok'):
    calls = []
    class Process:
        pid = 987654
        def __init__(self, command, **kwargs):
            calls.append((command, kwargs))
            self.waits = 0
            root = Path(kwargs['cwd'])
            kwargs['stdout'].write(b'native stdout\n')
            kwargs['stderr'].write(b'native stderr\n')
            if mode != 'timeout':
                value = measurement()
                if mode == 'mismatch':
                    value['bodies'][0]['id'] = 'wrong'
                (root/'measurement.json').write_text(json.dumps(value))
                (root/'resource.json').write_text(json.dumps(dict(peak_rss_kib=65536, user_cpu_seconds=.3)))
        def wait(self, timeout=None):
            self.waits += 1
            if mode == 'timeout' and self.waits == 1:
                raise subprocess.TimeoutExpired('FreeCAD', timeout)
            return -9 if mode == 'timeout' else 0
    monkeypatch.setattr(backend.subprocess, 'Popen', Process)
    monkeypatch.setattr(backend.shutil, 'which', lambda name: '/usr/bin/'+name)
    return calls


def test_bounded_run_preserves_request_logs_tool_version_and_resources(tmp_path, monkeypatch):
    calls = mock_process(monkeypatch)
    step = tmp_path/'source.step'
    step.write_text('immutable STEP fixture')
    output = tmp_path/'run'
    result = backend.run(step, output, expected_body_ids=['source/body'])
    assert result['execution'] == 'completed'
    assert result['bodies'][0]['volume_m3'] == .006
    assert result['native']['FreeCAD_version'] == ['1', '1', '0']
    assert result['usage']['peak_rss_kib'] == 112040
    assert result['usage']['launcher_process']['peak_rss_kib'] == 65536
    assert result['limits']['aggregate_cgroup_memory_limit'] is False
    assert (output/'input.step').read_bytes() == step.read_bytes()
    assert (output/'stdout.log').read_text() == 'native stdout\n'
    assert (output/'stderr.log').read_text() == 'native stderr\n'
    command, kwargs = calls[0]
    assert '--unshare=network' in command
    assert '--nofilesystem=home' in command
    assert '--filesystem='+str(output) in command
    assert 'ulimit -v 2097152 && exec FreeCADCmd "$1"' in command
    assert kwargs['start_new_session'] is True
    assert callable(kwargs['preexec_fn'])
    assert json.loads((output/'input.json').read_text())['expected_body_ids'] == ['source/body']
    assert json.loads((output/'result.json').read_text())['execution'] == 'completed'


def test_failed_identity_check_retains_native_execution(tmp_path, monkeypatch):
    mock_process(monkeypatch, 'mismatch')
    step = tmp_path/'source.step'
    step.write_text('STEP')
    result = backend.run(step, tmp_path/'run', expected_body_ids=['source/body'])
    assert result['execution'] == 'failed'
    assert result['returncode'] == 0
    assert result['native']['bodies'][0]['id'] == 'wrong'
    assert 'identity/count' in result['error']['message']


def test_timeout_kills_launched_process_group_and_keeps_logs(tmp_path, monkeypatch):
    mock_process(monkeypatch, 'timeout')
    killed = []
    monkeypatch.setattr(backend.os, 'killpg', lambda pid, sig: killed.append((pid, sig)))
    step = tmp_path/'source.step'
    step.write_text('STEP')
    result = backend.run(step, tmp_path/'run', timeout_s=1)
    assert result['execution'] == 'timeout'
    assert killed == [(987654, backend.signal.SIGKILL)]
    assert result['native'] is None
    assert result['usage']['child_resource_measurement_available'] is False
    assert (tmp_path/'run/stdout.log').is_file()


def test_unsafe_inputs_are_rejected_before_native_execution(tmp_path):
    source = tmp_path/'source.step'
    source.write_text('STEP')
    link = tmp_path/'link.step'
    link.symlink_to(source)
    with pytest.raises(ValueError, match='Ordinary'):
        backend.run(link, tmp_path/'run')
    with pytest.raises(ValueError, match='timeout'):
        backend.run(source, tmp_path/'run', timeout_s=float('nan'))
    with pytest.raises(ValueError, match='memory'):
        backend.run(source, tmp_path/'run', memory_mb=1)
    with pytest.raises(ValueError, match='Unique'):
        backend.run(source, tmp_path/'run', expected_body_ids=['a', 'a'])
    output = tmp_path/'existing'
    output.mkdir()
    (output/'keep.txt').write_text('existing evidence')
    with pytest.raises(ValueError, match='Fresh'):
        backend.run(source, output)


def test_step_brep_names_are_diagnostics_without_heuristic_native_mapping(tmp_path):
    step = tmp_path/'named.step'
    step.write_text("#125=MANIFOLD_SOLID_BREP('source/a',#124);\n"
                    "#197 = MANIFOLD_SOLID_BREP('source/it''s', #196);\n"
                    "#198=PRODUCT('assembly','assembly','',(#1));")
    assert backend._step_brep_names(step) == [
        dict(step_entity_id=125, name='source/a', shell_entity_id=124),
        dict(step_entity_id=197, name="source/it's", shell_entity_id=196)]
