#!/usr/bin/env python3
"""Compile generic + city ERP profiles against reproducible OSR operations bundles."""
import argparse
import gzip
from functools import lru_cache
import json
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "deployment/erpnext/apps/osr_erpnext"))
from osr_erpnext.city_config import make_city_plan, merge_config, validate_config

GENERIC = ROOT / "deployment/erpnext/config/generic.toml"


@lru_cache(maxsize=1)
def catalogue():
    result = {}
    for path in sorted((ROOT / "cities/catalogue").glob("*/*/*/design.toml")):
        city = tomllib.loads(path.read_text())["city"]
        if city["slug"] in result:
            raise ValueError("Duplicate city slug")
        result[city["slug"]] = (path, city)
    return result


def seed_profiles():
    created = 0
    for slug, (design_path, city) in catalogue().items():
        profile = design_path.parent / "operations/erpnext.toml"
        if profile.exists():
            continue
        profile.parent.mkdir(parents=True, exist_ok=True)
        content = ("# City-specific ERP overrides. Shared defaults: deployment/erpnext/config/generic.toml\n"
                   "# Lists replace generic lists; omitted values inherit. Operator dates remain unset.\n\n"
                   "[city]\n" + "\n".join(f"{k} = {json.dumps(v)}" for k, v in {
                       "slug": slug, "name": design_path.parent.name.replace("-", " "),
                       "country_code": city["country"],
                       "design_path": design_path.relative_to(ROOT).as_posix(),
                   }.items()) + "\n")
        profile.write_text(content)
        created += 1
    return created


def effective_config(slug, generic=GENERIC):
    design_path, city = catalogue()[slug]
    config = merge_config(tomllib.loads(generic.read_text()),
                          tomllib.loads((design_path.parent / "operations/erpnext.toml").read_text()))
    validate_config(config)
    if config["city"]["slug"] != slug or config["city"]["country_code"] != city["country"] or config["city"]["design_path"] != design_path.relative_to(ROOT).as_posix():
        raise ValueError("City profile identity differs from the catalogue")
    return config


def prepare(slug, output, bundle_path=None, company=None, start_date=None, release=None):
    config = effective_config(slug)
    if company is not None:
        config["organisation"]["company"] = company
    if start_date is not None:
        config["calendar"]["start_date"] = start_date
    if release is not None:
        config["release"] = release
    design_path, _ = catalogue()[slug]
    source = bundle_path or design_path.parent / "operations" / f"{slug}-operations.json.gz"
    if not source.is_file():
        raise ValueError(f"Missing city bundle {source}; generate it with ./osr city {slug} first")
    raw = source.read_bytes()
    bundle = json.loads(gzip.decompress(raw) if source.suffix == ".gz" else raw)
    plan = make_city_plan(bundle, config)
    output.mkdir(parents=True, exist_ok=True)
    (output / "effective-config.json").write_text(json.dumps(config, indent=2) + "\n")
    (output / "plan.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n")
    counts = {kind: sum(r["kind"] == kind for r in plan["records"]) for kind in config["tasks"]}
    summary = dict(city=slug, revision=plan["revision"], release=plan["release"],
                   config_sha256=plan["config_sha256"], package_sha256=plan["package_sha256"],
                   task_counts=counts, dependencies=sum(len(r["depends_on"]) for r in plan["records"]),
                   dated_tasks=sum(bool(r["start_date"]) for r in plan["records"]),
                   company=config["organisation"]["company"] or "operator-configuration-required",
                   calendar_status="configured" if config["calendar"]["start_date"] else "relative-planning-days-only")
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init-configs")
    sub.add_parser("validate")
    command = sub.add_parser("prepare")
    command.add_argument("city")
    command.add_argument("--bundle", type=Path)
    command.add_argument("--output", type=Path)
    command.add_argument("--company")
    command.add_argument("--start-date")
    command.add_argument("--release")
    args = parser.parse_args()
    try:
        if args.command == "init-configs":
            print(f"Created {seed_profiles()} city profiles; existing overrides preserved")
        elif args.command == "validate":
            cities = catalogue()
            for slug in cities:
                effective_config(slug)
            print(f"Validated {len(cities)} generic + city configurations")
        else:
            print(json.dumps(prepare(args.city, args.output or ROOT / "build/erpnext/cities" / args.city,
                                     args.bundle, args.company, args.start_date, args.release), indent=2))
    except (ValueError, KeyError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
