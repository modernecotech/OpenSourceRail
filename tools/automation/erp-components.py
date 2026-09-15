#!/usr/bin/env python3
"""Compile reusable component profiles for any OSR city."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'deployment/erpnext/apps/osr_erpnext'))
from osr_erpnext.component_catalogue import CATALOGUE, merge_profiles, make_package

spec = importlib.util.spec_from_file_location('erp_city', ROOT / 'tools/automation/erpnext-city.py')
cities = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cities)
GENERIC = ROOT / 'deployment/erpnext/config/components.json'


def effective(slug):
    path, _ = cities.catalogue()[slug]
    city = json.loads((path.parent / 'operations/erp-components.json').read_text())
    if city.get('city') != slug:
        raise ValueError('Component profile city does not match catalogue')
    return merge_profiles(json.loads(GENERIC.read_text()), city)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('catalogue')
    sub.add_parser('init-configs')
    sub.add_parser('validate')
    p = sub.add_parser('prepare'); p.add_argument('city'); p.add_argument('--project', required=True); p.add_argument('--output', type=Path)
    for action in ['preview', 'apply']:
        p = sub.add_parser(action); p.add_argument('package', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'catalogue':
            print(json.dumps(CATALOGUE, indent=2))
        elif args.command == 'init-configs':
            count = 0
            for slug, (path, _) in cities.catalogue().items():
                target = path.parent / 'operations/erp-components.json'
                if not target.exists():
                    target.write_text(json.dumps(dict(schema='osr-components/1', city=slug, defaults={}, instances=[]), indent=2)+'\n')
                    count += 1
            print(f'Created {count} profiles; existing city overrides preserved')
        elif args.command == 'validate':
            for slug in cities.catalogue():
                effective(slug)
            print(f'Validated {len(cities.catalogue())} component profiles')
        elif args.command == 'prepare':
            package = make_package(effective(args.city), args.project)
            target = args.output or ROOT / 'build/erpnext/cities' / args.city / 'components.json'
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(package, indent=2)+'\n')
            print(target)
        else:
            command = 'component-preview' if args.command == 'preview' else 'component-apply'
            subprocess.run([sys.executable, str(ROOT / 'tools/automation/erp-platform.py'), command, str(args.package)], check=True)
    except (ValueError, KeyError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
