"""Backups must verify the actual database and every archive member."""
import hashlib
import importlib.util
import json
import sqlite3
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('backup', ROOT / 'tools/automation/ops-core-backup.py')
BACKUP = importlib.util.module_from_spec(spec)
spec.loader.exec_module(BACKUP)


def test_unlisted_invalid_database_is_rejected(tmp_path):
    archive = tmp_path / 'invalid.zip'
    with zipfile.ZipFile(archive, 'w') as out:
        out.writestr('manifest.json', json.dumps({'schema_version': '1.0', 'files': []}))
        out.writestr('data/ops-core.sqlite3', 'not a database')
    with pytest.raises(SystemExit):
        BACKUP.verify_backup(archive)


def archive_fixture(tmp_path):
    database = tmp_path / 'source.sqlite3'
    with sqlite3.connect(database) as db:
        db.execute('CREATE TABLE sample (value TEXT)')
        db.execute("INSERT INTO sample VALUES ('retained')")
    body = database.read_bytes()
    manifest = dict(schema_version='1.0', created_at='2026-09-18T12:00:00+00:00', files=[
        dict(path='data/ops-core.sqlite3', size_bytes=len(body), sha256=hashlib.sha256(body).hexdigest())])
    return manifest, body


def write_archive(path, manifest, body, extra=()):
    with zipfile.ZipFile(path, 'w') as out:
        out.writestr('manifest.json', json.dumps(manifest))
        out.writestr('data/ops-core.sqlite3', body)
        for name, data in extra:
            out.writestr(name, data)


@pytest.mark.parametrize('fault', ['empty', 'schema', 'no-timezone', 'duplicate-manifest',
    'duplicate-archive', 'extra', 'missing', 'traversal', 'absolute', 'backslash',
    'size', 'checksum', 'invalid-sqlite', 'corrupt-sqlite', 'symlink'])
def test_invalid_archives_fail_closed(tmp_path, fault):
    manifest, body = archive_fixture(tmp_path)
    extras = []
    if fault == 'empty': manifest['files'] = []
    elif fault == 'schema': manifest['schema_version'] = 'future'
    elif fault == 'no-timezone': manifest['created_at'] = '2026-09-18T12:00:00'
    elif fault == 'duplicate-manifest': manifest['files'] *= 2
    elif fault == 'duplicate-archive': extras = [('data/ops-core.sqlite3', body)]
    elif fault == 'extra': extras = [('unlisted', b'extra')]
    elif fault in ('missing', 'traversal', 'absolute', 'backslash'):
        name = {'missing': 'data/evidence/missing', 'traversal': 'data/evidence/../../escape',
                'absolute': '/tmp/escape', 'backslash': 'data/evidence/..\\escape'}[fault]
        manifest['files'].append(dict(path=name, size_bytes=1, sha256=hashlib.sha256(b'x').hexdigest()))
        if fault != 'missing': extras = [(name, b'x')]
    elif fault == 'size': manifest['files'][0]['size_bytes'] = True
    elif fault == 'checksum': manifest['files'][0]['sha256'] = '0' * 64
    elif fault in ('invalid-sqlite', 'corrupt-sqlite'):
        body = b'not sqlite' if fault == 'invalid-sqlite' else body[:200]
        manifest['files'][0].update(size_bytes=len(body), sha256=hashlib.sha256(body).hexdigest())
    archive = tmp_path / 'invalid.zip'
    if fault == 'symlink':
        info = zipfile.ZipInfo('data/evidence/link'); info.external_attr = 0o120777 << 16
        extras = [(info, b'/etc/passwd')]
    write_archive(archive, manifest, body, extras)
    with pytest.raises(SystemExit, match='verification failed'):
        BACKUP.verify_backup(archive)


def test_fresh_restore_preserves_application_and_rebases_evidence(tmp_path):
    spec = importlib.util.spec_from_file_location('restore_ops', ROOT / 'tools/automation/ops-core-server.py')
    ops = importlib.util.module_from_spec(spec); spec.loader.exec_module(ops)
    database = tmp_path / 'ops.sqlite3'
    evidence = tmp_path / 'evidence'
    content = b'performed fixture inspection\x00\xff'
    digest = hashlib.sha256(content).hexdigest()
    original = evidence / 'test' / digest[:2] / (digest + '-inspection.bin')
    original.parent.mkdir(parents=True); original.write_bytes(content)
    with ops.connect(database) as db:
        ops.init_db(db)
        db.execute("INSERT INTO city_state(city_slug,updated_at) VALUES ('test','2026-09-18')")
        db.execute("INSERT INTO work_orders(city_slug,id,position,title,payload) VALUES ('test','WO-1',0,'retained work','{}')")
        db.execute('INSERT INTO evidence_files VALUES (?,?,?,?,?,?,?,?,?)',
            ('test', digest, 'inspection.bin', 'application/octet-stream', len(content), str(original), '2026-09-18', 'inspector', '{}'))
        reference = '/api/ops-core/test/evidence/' + digest
        db.execute('INSERT INTO inspections(city_slug,id,position,wo_id,evidence_ref,payload) VALUES (?,?,?,?,?,?)',
            ('test', 'INS-1', 0, 'WO-1', reference, json.dumps(dict(id='INS-1',wo_id='WO-1',evidence_ref=reference))))
        db.commit()
    archive = tmp_path / 'backup.zip'
    BACKUP.create_backup(database, evidence, archive)
    output = tmp_path / 'fresh'
    BACKUP.restore_backup(archive, output)
    original.unlink()
    with sqlite3.connect(output / 'data/ops-core.sqlite3') as db:
        assert db.execute('SELECT title FROM work_orders').fetchone()[0] == 'retained work'
        assert db.execute('SELECT evidence_ref FROM inspections').fetchone()[0] == reference
        restored = Path(db.execute('SELECT stored_path FROM evidence_files').fetchone()[0])
        assert restored.is_relative_to(output)
        assert restored.read_bytes() == content
        assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    with pytest.raises(SystemExit, match='must not exist'):
        BACKUP.restore_backup(archive, output)
    # Checksums of the ZIP alone cannot prove that application evidence is present.
    missing = tmp_path / 'missing-evidence.zip'
    with zipfile.ZipFile(archive) as source:
        manifest = json.loads(source.read('manifest.json'))
        body = source.read('data/ops-core.sqlite3')
    manifest['files'] = [row for row in manifest['files'] if row['path'] == 'data/ops-core.sqlite3']
    write_archive(missing, manifest, body)
    with pytest.raises(SystemExit, match='application evidence'):
        BACKUP.verify_backup(missing)
