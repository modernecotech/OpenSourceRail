#!/usr/bin/env python3
"""Route exact Azure Ubuntu mirror URIs on a disposable historical CI runner.

Only known source files and exact URI tokens change. Suites, components,
priorities, security URIs and signing metadata remain unchanged. Snapshot all
APT source files before and after the change; never invoke APT or a native tool.

Noble GitHub runners use mirror+file:/etc/apt/apt-mirrors.txt:
https://github.com/actions/runner-images/blob/ubuntu24/20261012.334/images/ubuntu/scripts/build/configure-apt-sources.sh
Acquire::http::Dl-Limit=0 is APT's unlimited default, not evidence of a prior cap:
https://manpages.ubuntu.com/manpages/noble/man1/apt-transport-http.1.html
"""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import stat
import tempfile

URI_MAP = {
    scheme + '://azure.archive.ubuntu.com/ubuntu' + slash:
    'https://archive.ubuntu.com/ubuntu' + slash
    for scheme in ('http', 'https') for slash in ('', '/')
}
TARGETS = {
    'sources.list': 'legacy',
    'sources.list.d/ubuntu.sources': 'deb822',
    'apt-mirrors.txt': 'mirrors',
}


def uri_tokens(text):
    body, marker, comment = text.partition('#')
    return re.sub(r'\S+', lambda m: URI_MAP.get(m[0], m[0]), body) + marker + comment


def rewrite(text, kind):
    output = []
    uri_field = False
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith('#'):
            output.append(line)
            continue
        if kind == 'legacy':
            match = re.match(r'^(\s*deb(?:-src)?\s+(?:\[[^\]]*\]\s+)?)(\S+)', line)
            if match:
                line = line[:match.start(2)] + URI_MAP.get(match[2], match[2]) + line[match.end(2):]
        elif kind == 'deb822':
            field = re.match(r'^([A-Za-z][A-Za-z0-9-]*):', line)
            if field:
                uri_field = field[1].lower() == 'uris'
            elif not line.strip():
                uri_field = False
            if uri_field:
                line = uri_tokens(line)
        elif kind == 'mirrors':
            match = re.match(r'^(\s*)(\S+)', line)
            if match:
                line = line[:match.start(2)] + URI_MAP.get(match[2], match[2]) + line[match.end(2):]
        else:
            raise ValueError('Explicit supported APT source format required')
        output.append(line)
    return ''.join(output)


def ordinary(root, name):
    path = root / name
    for part in (path, *path.parents):
        if part == root:
            break
        if part.is_symlink():
            raise ValueError('Linked APT configuration refused: ' + name)
    if not path.is_file():
        raise ValueError('Ordinary APT source file required: ' + name)
    if path.stat().st_size > 1024 * 1024:
        raise ValueError('APT source file exceeds bounded review size')
    return path


def configure(apt_root, output):
    apt_root, output = Path(apt_root), Path(output)
    if apt_root.is_symlink() or not apt_root.is_dir():
        raise ValueError('Explicit ordinary APT root required')
    if output.is_symlink():
        raise ValueError('Linked audit directory refused')
    root, output = apt_root.resolve(), output.resolve()
    if output.exists() or output.is_relative_to(root):
        raise ValueError('Fresh audit directory outside APT root required')
    names = {name for name in TARGETS if (root / name).exists() or (root / name).is_symlink()}
    directory = root / 'sources.list.d'
    if directory.is_symlink():
        raise ValueError('Linked APT source directory refused')
    if directory.is_dir():
        names.update(p.relative_to(root).as_posix()
                     for p in directory.iterdir() if p.suffix in ('.list', '.sources'))
    if not names or len(names) > 100:
        raise ValueError('Bounded existing APT source inventory required')
    original = {name: ordinary(root, name).read_bytes() for name in sorted(names)}
    effective = {
        name: (rewrite(raw.decode('utf-8'), TARGETS[name]).encode('utf-8')
               if name in TARGETS else raw)
        for name, raw in original.items()
    }
    output.mkdir(parents=True)
    for stage, values in (('original', original), ('effective', effective)):
        for name, raw in values.items():
            target = output / stage / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    # Review all bytes before mutation. Atomic replacement preserves file mode.
    for name, raw in original.items():
        if ordinary(root, name).read_bytes() != raw:
            raise ValueError('APT source changed during review: ' + name)
    for name, raw in effective.items():
        path = ordinary(root, name)
        if raw == original[name]:
            continue
        mode = stat.S_IMODE(path.stat().st_mode)
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.osr-apt-', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(raw)
            os.fchmod(stream.fileno(), mode)
        try:
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)
    for name, raw in effective.items():
        if ordinary(root, name).read_bytes() != raw:
            raise ValueError('APT effective source differs: ' + name)
    records = {
        name: dict(original_sha256=sha256(original[name]).hexdigest(),
                   effective_sha256=sha256(raw).hexdigest(), changed=raw != original[name])
        for name, raw in effective.items()
    }
    value = dict(
        schema='osr-historical-apt-source-route/1', sources=records,
        changed_sources=[name for name, row in records.items() if row['changed']],
        replacement='Exact Azure Ubuntu URI tokens to https://archive.ubuntu.com/ubuntu',
        suites_components_signing_and_security_metadata_changed=False,
        package_requirements_changed=False, inherited_rate_cap_established=False,
        scope='Disposable CI dependency acquisition only; no numerical or physical acceptance',
        observed_failure=dict(run_id=40555969817, job_id=122371989330, step=7,
                              reason='20-minute timeout during continuous slow Azure package downloads'),
        helper_sha256=sha256(Path(__file__).read_bytes()).hexdigest(), physical_accepted=False,
    )
    (output / 'manifest.json').write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apt-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(configure(args.apt_root, args.output), sort_keys=True))
