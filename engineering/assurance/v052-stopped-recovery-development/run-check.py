"""Retain command output with before/after development-source receipts.

This records execution and source consistency, never engineering acceptance.
Use after the primary refresh for checks reading canonical generated packets.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from engineering.ferrite_maglev import model


def sources():
    values = model.sources()
    omitted = {'target', 'build', 'node_modules', '__pycache__', '.git', 'assurance'}
    for folder in ('crates', 'engineering', 'tools/automation', 'lib'):
        for path in (ROOT / folder).rglob('*'):
            relative = path.relative_to(ROOT)
            if (not path.is_file() or any(p in omitted for p in relative.parts)
                    or path.suffix not in {'.rs', '.toml', '.py', '.sh', '.mjs', '.js'}):
                continue
            values[relative.as_posix()] = sha256(path.read_bytes()).hexdigest()
    for name in ('Cargo.toml', 'Cargo.lock', 'rust-toolchain.toml', 'package.json',
                 'package-lock.json', 'pytest.ini', '.cargo/config.toml'):
        path = ROOT / name
        if path.is_file():
            values[name] = sha256(path.read_bytes()).hexdigest()
    values[Path(__file__).relative_to(ROOT).as_posix()] = sha256(Path(__file__).read_bytes()).hexdigest()
    return dict(sorted(values.items()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', required=True)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not args.name or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in args.name):
        parser.error('a simple lower-case check name is required')
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('an executable command is required')
    base = Path(__file__).parent
    receipt_path = base / (args.name + '.json')
    log = base / (args.name + '.txt')
    if receipt_path.exists() or log.exists():
        parser.error('a new check name is required; retained runs are immutable')
    before = sources()
    started = datetime.now(timezone.utc).isoformat()
    with log.open('wb') as stream:
        result = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
    after = sources()
    receipt = dict(schema='osr-stopped-recovery-executed-check/1', command=command,
        started_utc=started, finished_utc=datetime.now(timezone.utc).isoformat(),
        exit_status=result.returncode, source_unchanged=before == after,
        source_sha256=before, log_sha256=sha256(log.read_bytes()).hexdigest(),
        source_scope='Primary input map plus Rust/Python/JS/shell implementation and test envelope. Inclusion does not claim every source file executed.',
        engineering_accepted=False, **model.FLAGS)
    receipt_path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')
    print(json.dumps({k:v for k,v in receipt.items() if k != 'source_sha256'}, indent=2))
    return result.returncode or (0 if before == after else 2)


if __name__ == '__main__':
    raise SystemExit(main())
