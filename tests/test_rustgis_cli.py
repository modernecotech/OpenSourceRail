"""Synthetic CLI orchestration checks; no native editor or city solver runs."""
import json
from pathlib import Path

import pytest

from engineering.rustgis import __main__ as cli, adapter, revision


@pytest.mark.parametrize('external_stores',[False,True])
def test_reprice_can_export_and_verify_the_completed_child_study(tmp_path, monkeypatch, capsys,external_stores):
    project = tmp_path / 'edited.rgis'
    project.write_bytes(b'{"format":1}')
    output = tmp_path / 'refreshed-projects'
    calls = {}

    class Service:
        def __init__(self, root):
            assert Path(root) == tmp_path
            self.closed = False

        def close(self):
            self.closed = True

    service = Service(tmp_path)
    def create_service(root,**kwargs):
        assert kwargs==({'store':tmp_path.parent/(tmp_path.name+'-studies')} if external_stores else {})
        return service
    monkeypatch.setattr('engineering.outline.city_jobs.CityStudyService',create_service)

    def import_project(*args, **kwargs):
        assert kwargs['service'] is service
        assert kwargs['store']==(tmp_path.parent/(tmp_path.name+'-imports') if external_stores else None)
        return dict(import_id='1' * 32, execution='submitted',
                    job=dict(job_id='2' * 32, state='completed'))

    def export_study(study_id, *, root, service, output):
        calls.update(study_id=study_id, root=Path(root), service=service, output=Path(output))
        Path(output).mkdir()
        return dict(verified=True, archive=str(Path(output) / 'samawah.zip'),
                    manifest_id='3' * 64, physical_accepted=False)

    monkeypatch.setattr(revision, 'import_project', import_project)
    def verify_import(folder,**kwargs):
        assert Path(folder)==revision.import_store(tmp_path,
            tmp_path.parent/(tmp_path.name+'-imports') if external_stores else None)/('1'*32)
        return dict(verified=True)
    monkeypatch.setattr(revision,'verify_import',verify_import)
    monkeypatch.setattr(adapter, 'export_study', export_study)
    cli.main(['reprice', '--city', 'samawah', '--packet-id', '4' * 64,
        '--project', str(project), '--actor', 'Planner', '--reason', 'Route edit',
        '--data-crs', 'EPSG:4326', '--refreshed-output', str(output)]+(
        ['--import-store',str(tmp_path.parent/(tmp_path.name+'-imports')),
         '--study-store',str(tmp_path.parent/(tmp_path.name+'-studies'))] if external_stores else []),root=tmp_path)

    result = json.loads(capsys.readouterr().out)
    assert calls == dict(study_id='2' * 32, root=tmp_path, service=service, output=output)
    assert result['job']['state'] == 'completed'
    assert result['import_verification']['verified'] is True
    assert result['refreshed_project']['verified'] is True
    assert result['physical_accepted'] is False
    assert output.is_dir() and service.closed


def test_refreshed_export_requires_a_fresh_output_directory(tmp_path, monkeypatch):
    project = tmp_path / 'edited.rgis'
    project.write_bytes(b'{"format":1}')
    output = tmp_path / 'already-exists'
    output.mkdir()
    called = False

    def forbidden(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError('A non-fresh export path must be refused before repricing')

    monkeypatch.setattr(revision, 'import_project', forbidden)
    with pytest.raises(SystemExit):
        cli.main(['reprice', '--city', 'samawah', '--packet-id', '4' * 64,
            '--project', str(project), '--actor', 'Planner', '--reason', 'Route edit',
            '--data-crs', 'EPSG:4326', '--refreshed-output', str(output)], root=tmp_path)
    assert not called
