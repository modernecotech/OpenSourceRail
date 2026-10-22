"""Run the tracked complete suite and bind its calculation/test source envelope."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,os,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engineering.ferrite_maglev import model

root=model.ROOT

def auxiliary_snapshot(primary):
    paths={Path(__file__).resolve()}
    suffixes={'.rs','.toml','.py','.sh','.mjs','.js','.json'}
    omitted={'target','build','node_modules','__pycache__','.git'}
    for folder in ('crates','engineering','tools/automation','lib'):
        for path in (root/folder).rglob('*'):
            relative=path.relative_to(root)
            if (not path.is_file() or path.suffix not in suffixes or any(part in omitted for part in relative.parts)
                    or relative.parts[:2]==('engineering','assurance')):continue
            if path.suffix=='.json' and relative.parts[0]!='crates':continue
            paths.add(path)
    for name in ('pytest.ini','pyproject.toml','rust-toolchain.toml','.cargo/config.toml'):
        if (root/name).is_file():paths.add(root/name)
    return {path.relative_to(root).as_posix():sha256(path.read_bytes()).hexdigest()
        for path in sorted(paths) if path.relative_to(root).as_posix() not in primary}

def main():
    before=model.sources();aux_before=auxiliary_snapshot(before)
    log=root/'build/closure-final-tests.log'
    started=datetime.now(timezone.utc).isoformat()
    with log.open('wb') as stream:
        result=subprocess.run(['./osr','test'],cwd=root,stdout=stream,stderr=subprocess.STDOUT,env=os.environ.copy())
    after=model.sources();aux_after=auxiliary_snapshot(after)
    receipt=dict(schema='osr-executed-final-suite/1',command=['./osr','test'],
        started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),
        exit_status=result.returncode,source_unchanged=before==after,source_sha256=after,
        auxiliary_test_sources_unchanged=aux_before==aux_after,auxiliary_test_source_sha256=aux_after,
        auxiliary_scope='Repository Rust/Python/JS/shell source and Cargo/config/fixture envelope beyond the primary calculation map; generated build, documentation and assurance outputs excluded. Inclusion is a source binding, not a claim every file executed.',
        log_sha256=sha256(log.read_bytes()).hexdigest(),physical_release=False)
    (root/'build/closure-final-suite.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({key:value for key,value in receipt.items() if key not in {'source_sha256','auxiliary_test_source_sha256'}},indent=2),flush=True)
    return result.returncode or (0 if before==after and aux_before==aux_after else 2)

if __name__=='__main__':raise SystemExit(main())
