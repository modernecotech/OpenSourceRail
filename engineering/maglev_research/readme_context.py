"""Maintain current README introductions and audit every retained README route.

Only thirteen explicitly owned manual entrypoints receive an introduction.
Generated city studies, numerical packets and archived evidence stay byte-bound
through their existing receipts; the coverage page supplies current context.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path('docs/design-engine/ferrite-maglev/research-closure')
START = '<!-- osr-system-context:start -->'
END = '<!-- osr-system-context:end -->'
OWNED = (
    'LICENSES/README.md', 'control-electronics/README.md', 'crates/README.md',
    'crates/osr-maglev-control/README.md', 'deployment/README.md',
    'deployment/erpnext/README.md', 'deployment/supervision/README.md',
    'docs/README.md', 'engineering/README.md', 'engineering/ferrite_maglev/README.md',
    'engineering/ferrite_maglev/observer-prototype/README.md',
    'tools/README.md', 'tools/reference-ma/README.md',
)
CONTEXT_TARGETS = {'README.md', 'engineering/README.md', 'engineering/ferrite_maglev/README.md'}
INTRODUCTION = (
    'OpenSourceRail develops an open, locally buildable urban railway with fixed linear '
    'motors at stations and, where needed, located boosters. Trains coast between powered '
    'zones while onboard ferrite support, guidance and passenger services remain independently '
    'powered; passengers transfer between fixed lines at junctions. Simple vehicles, repeated '
    'civil works and repairable local production aim for high useful passenger throughput '
    'and affordable construction, operation and debt repayment. Current studies and digital '
    'workflows support development; an accepted physical railway has not been established.'
)
LINK = re.compile(r'(?<!!)\[[^\]\n]*\]\(([^\n]*?)\)')
DIGEST = re.compile(r'[a-f0-9]{64}')


def _hash(raw):
    return sha256(raw).hexdigest()


def _ordinary(root, name):
    path = root / name
    if Path(name).is_absolute() or '..' in Path(name).parts or not path.is_file():
        raise ValueError('ordinary repository-relative README required: ' + str(name))
    if any(node.is_symlink() for node in (path, *path.parents)):
        raise ValueError('symlink README paths are not owned')
    return path


def inventory(root=ROOT):
    """Include tracked and new README Markdown, including executed-README."""
    root = Path(root).resolve()
    names = set()
    for options in ([], ['--others', '--exclude-standard']):
        raw = subprocess.check_output(['git', 'ls-files', '-z', *options, '*README*'], cwd=root)
        names.update(name.decode() for name in raw.split(b'\0') if name and name.decode().endswith('.md'))
    return sorted(names)


def category(name):
    if name in OWNED:
        return 'manual-current-entrypoint'
    if name == 'README.md':
        return 'project-frontdoor'
    if name == 'engineering/design_search/README.md':
        return 'candidate-design-method'
    if name == 'engineering/city_maps/README.md':
        return 'city-map-method'
    if name in {'cities/catalogue/README.md', 'docs/capabilities/README.md'}:
        return 'generated-navigation-index'
    if name == 'docs/design-engine/ferrite-maglev/research-closure/README.md':
        return 'current-research-programme'
    if name.startswith('cities/catalogue/'):
        return 'generated-city-package' if '/engineering/maglev/' in name else 'generated-city-brief'
    if name.startswith('docs/design-engine/'):
        return 'retained-design-evidence'
    if name.startswith('engineering/assurance/'):
        return 'retained-assurance-evidence'
    return 'unclassified'


def introduction(name):
    parent = Path(name).parent
    route = Path(os.path.relpath('README.md', parent)).as_posix()
    method = Path(os.path.relpath('engineering/ferrite_maglev/README.md', parent)).as_posix()
    return '\n'.join((START, INTRODUCTION, '',
                      f'[Project introduction]({route}) · [Engineering approach and current status]({method})', END))


def render(text, name):
    if name not in OWNED:
        raise ValueError('README is outside the thirteen owned manual entrypoints')
    if text.count(START) != text.count(END) or text.count(START) > 1:
        raise ValueError('one complete owned introduction block required')
    block = introduction(name)
    if START in text:
        first = text.index(START)
        last = text.index(END) + len(END)
        return text[:first] + block + text[last:]
    lines = text.splitlines(keepends=True)
    if not lines or not lines[0].startswith('# '):
        raise ValueError('manual README must start with its existing H1')
    return lines[0].rstrip('\r\n') + '\n\n' + block + '\n\n' + ''.join(lines[1:]).lstrip('\r\n')


def local_links(root, name, text):
    """Resolve ordinary local Markdown routes; never fetch external URLs."""
    result = set()
    for target in LINK.findall(text):
        target = target.strip().removeprefix('<').removesuffix('>')
        if ' "' in target:
            target = target.split(' "', 1)[0]
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        path = (root / name).parent / unquote(parsed.path)
        try:
            relative = path.resolve().relative_to(root).as_posix()
        except ValueError:
            continue
        if (root / relative).is_file():
            result.add(relative)
    return sorted(result)


def _route(graph, name):
    if name in CONTEXT_TARGETS:
        return [name]
    pending = deque([[name]])
    seen = {name}
    while pending:
        chain = pending.popleft()
        if len(chain) > 4:
            continue
        for link in graph.get(chain[-1], []):
            if link in CONTEXT_TARGETS:
                return chain + [link]
            if link not in seen and link in graph:
                seen.add(link)
                pending.append(chain + [link])
    return []


def bindings(root, names):
    """Locate README source/payload digests without rewriting numerical receipts."""
    names = set(names)
    result = {name: [] for name in names}
    manifests = list((root/'docs/design-engine').rglob('manifest.json'))
    manifests += list((root/'engineering/assurance').rglob('manifest.json'))
    manifests += list((root/'engineering/assurance').rglob('archive-receipt.json'))
    def add(path, expected, receipt, kind):
        try:
            name = path.resolve().relative_to(root).as_posix()
        except ValueError:
            return
        if name in names and isinstance(expected, str) and DIGEST.fullmatch(expected):
            result[name].append(dict(receipt=receipt.relative_to(root).as_posix(), kind=kind,
                                     expected_sha256=expected))
    for receipt in sorted(set(manifests)):
        if receipt == root/OUTPUT/'manifest.json':
            continue  # This new publication checks its own packet independently.
        if receipt.is_symlink() or receipt.stat().st_size > 16*1024*1024:
            raise ValueError('bounded ordinary publication receipt required')
        value = json.loads(receipt.read_bytes())
        for key, payload_relative in (('files_sha256', True), ('source_sha256', False)):
            if key == 'source_sha256' and 'engineering/assurance' in receipt.relative_to(root).as_posix():
                continue  # Frozen historical source paths are not current dependencies.
            mapping = value.get(key)
            if isinstance(mapping, dict):
                for name, expected in mapping.items():
                    add((receipt.parent if payload_relative else root)/name, expected, receipt, key)
    city_index = root/'engineering/ferrite_maglev/city-index.json'
    if city_index.is_file():
        for row in json.loads(city_index.read_bytes()).get('cities', []):
            if isinstance(row.get('package_path'), str):
                add(root/row['package_path']/'README.md', row.get('readme_sha256'), city_index, 'city-readme-payload')
    return result


def audit(root=ROOT):
    root = Path(root).resolve()
    names = inventory(root)
    texts = {name: _ordinary(root, name).read_text() for name in names}
    bound = bindings(root, names)
    graph = {name: local_links(root, name, text) for name, text in texts.items()}
    rows = []
    errors = []
    for name in names:
        kind = category(name)
        text = texts[name]
        digest = _hash(text.encode())
        route = _route(graph, name)
        current = name in OWNED and text == render(text, name)
        if kind == 'unclassified':
            errors.append(name + ': README class needs an explicit ownership decision')
        if name in OWNED and not current:
            errors.append(name + ': current owned system introduction missing or stale')
        mismatches = [entry for entry in bound[name] if digest != entry['expected_sha256']]
        if mismatches:
            errors.append(name + ': README differs from retained numerical source/payload receipt')
        # The city brief and package are separate introduction routes. Both must
        # retain their own declared primary-method link, even if coverage links exist.
        if kind == 'generated-city-brief' and 'engineering/maglev/README.md' not in text:
            errors.append(name + ': city brief lacks its current numerical planning package')
        if kind == 'generated-city-package' and '[Primary planning method]' not in text:
            errors.append(name + ': city package lacks its current common-method link')
        rows.append(dict(path=name, category=kind, sha256=digest,
                         owned_introduction_current=current,
                         existing_context_route=route,
                         coverage_context_path='engineering/README.md',
                         coverage_context_required=not bool(route),
                         retained_bindings=bound[name],
                         retained_bindings_match=not mismatches,
                         preserved_evidence=kind.startswith('retained-') or kind.startswith('generated-city-')))
    return dict(schema='osr-readme-context-coverage/1', readme_count=len(rows),
                categories=dict(sorted(Counter(row['category'] for row in rows).items())),
                owned_manual_readmes=len(OWNED),
                owned_introductions_current=sum(row['owned_introduction_current'] for row in rows),
                existing_context_routes=sum(bool(row['existing_context_route']) for row in rows),
                central_context_routes=sum(row['coverage_context_required'] for row in rows),
                current_source_packet_readmes_preserved=all(row['retained_bindings_match'] for row in rows),
                current=not errors, errors=errors, readmes=rows,
                source_sha256={'engineering/maglev_research/readme_context.py':_hash(Path(__file__).read_bytes())},
                scope='Every tracked or new README-like Markdown has an explicit class and current-context link. Only thirteen manual entrypoints are edited; numerical and retained evidence documents retain their original byte/source bindings.')


def write_owned(root=ROOT):
    root = Path(root).resolve()
    names = inventory(root)
    bound = bindings(root, names)
    proposed = []
    for name in OWNED:
        path = _ordinary(root, name)
        if bound.get(name):
            raise ValueError('owned introduction would alter numerical evidence: ' + name)
        old = path.read_text()
        new = render(old, name)
        if old != new:
            proposed.append((path, new))
    for path, text in proposed:
        path.write_text(text)
    return [path.relative_to(root).as_posix() for path, _ in proposed]


def markdown(value):
    if not value['current']:
        raise ValueError('current README audit required before publishing coverage')
    base = OUTPUT
    def link(name, label=None):
        relative = Path(os.path.relpath(name, base)).as_posix().replace(' ', '%20')
        return '['+(label or name)+']('+relative+')'
    lines = ['# README introductions and current system context', '', INTRODUCTION, '',
        link('README.md', 'Project introduction')+' · '+link('engineering/README.md', 'System approach')+' · '+link('engineering/ferrite_maglev/README.md', 'Detailed implementation and current design gates'), '',
        f"All **{value['readme_count']} tracked or new README documents** are classified below. The **{value['owned_introductions_current']} manual entrypoints** carry a maintained concise introduction. Existing generated city introductions and their primary-method links remain intact. The project front door is maintained separately.", '',
        f"Existing local navigation reaches current context from **{value['existing_context_routes']} documents**. This page supplies an explicit current-context route for the remaining **{value['central_context_routes']} retained or generated documents**. These are navigation gaps, not rewritten scientific evidence.", '',
        'Source-bound city, design and archived research documents retain their exact README payloads and original scope. Their solver/source receipts are checked rather than silently resealed for presentation changes. A historical result never becomes current design acceptance because it appears beside the current introduction.', '',
        '| README class | Documents |', '|---|---:|']
    lines += [f'| {kind} | {count} |' for kind,count in value['categories'].items()]
    lines += ['', 'Regenerate and check with:', '', '```bash',
        'tools/automation/osr-python -m engineering.maglev_research.readme_context --write',
        'tools/automation/osr-python -m engineering.maglev_research.readme_context --check', '```', '',
        'The write command owns only the thirteen manual introduction blocks; it does not rewrite root, generated or retained research READMEs. Local document titles, technical scopes, licences and all content outside an owned block remain with their existing authors.', '',
        '| README | Class | Current system context | Existing route |', '|---|---|---|---|']
    for row in value['readmes']:
        existing = ' → '.join(link(name, Path(name).parent.name or 'project') for name in row['existing_context_route'][1:])
        if row['existing_context_route'] == [row['path']]:
            existing = 'Current system introduction'
        lines.append('| '+link(row['path'])+' | '+row['category']+' | '+link(row['coverage_context_path'], 'System approach')+' | '+(existing or 'Via this coverage page')+' |')
    return '\n'.join(lines)+'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='update only the thirteen owned introductions and coverage reports')
    parser.add_argument('--check', action='store_true', help='check introductions, all README routes and exact current coverage reports')
    args = parser.parse_args()
    if args.write:
        write_owned()
    value = audit()
    if not value['current']:
        for error in value['errors']:
            print('ERROR: '+error)
        return 1
    outputs = {ROOT/OUTPUT/'readme-coverage.json': json.dumps(value, sort_keys=True, indent=2)+'\n',
               ROOT/OUTPUT/'readme-coverage.md': markdown(value)}
    if args.write:
        for path,text in outputs.items():
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(text)
    if args.check:
        for path,text in outputs.items():
            if not path.is_file() or path.read_text() != text:
                print('ERROR: stale README coverage report: '+str(path.relative_to(ROOT)))
                return 1
    print(json.dumps({key:value[key] for key in ('readme_count','owned_introductions_current','existing_context_routes','central_context_routes','current_source_packet_readmes_preserved','current')},sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
