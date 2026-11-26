"""Check declared live railway claims against their authoritative inputs."""

import argparse
import ast
from dataclasses import dataclass, field
import gzip
import hashlib
from functools import cache
from importlib.util import resolve_name
import json
from pathlib import Path
import re
import tomllib


ROOT = Path(__file__).resolve().parents[1]
REGISTER = "engineering/live-coherence.toml"


@dataclass
class Report:
    specifications: int = 0
    checks: int = 0
    errors: list[str] = field(default_factory=list)


def _lookup(document, key):
    if key == "":
        return [("", document)]
    name, _, rest = key.partition(".")
    if name == "*":
        entries = document.items() if isinstance(document, dict) else enumerate(document)
    else:
        entries = [(name, document[int(name)] if isinstance(document, list) else document[name])]
    return [
        (".".join(filter(None, (str(index), child))), value)
        for index, item in entries
        for child, value in _lookup(item, rest)
    ]


def _one(document, key):
    entries = _lookup(document, key)
    if len(entries) != 1:
        raise ValueError(f"{key!r} needs exactly one matching field")
    return entries[0][1]


def _assignment(tree, name):
    matches = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        else:
            continue
        if any(isinstance(target, ast.Name) and target.id == name for target in targets):
            matches.append(node.value)
    if len(matches) != 1 or matches[0] is None:
        raise ValueError(f"{name!r} needs exactly one top-level assignment")
    return matches[0]


def _literal(node, key=None):
    if key is None:
        return ast.literal_eval(node)
    if not isinstance(node, ast.Dict):
        raise ValueError(f"{key!r} requires a dictionary assignment")
    for name, value in zip(node.keys, node.values):
        if isinstance(name, ast.Constant) and name.value == key:
            return ast.literal_eval(value)
    raise ValueError(f"missing dictionary literal {key!r}")


def check(root=ROOT):
    """Return diagnostics without importing production models or regenerating packets."""
    root = Path(root)
    report = Report()

    @cache
    def read(path):
        return (root / path).read_bytes()

    @cache
    def content(path):
        return read(path).decode()

    @cache
    def tree(path):
        return ast.parse(content(path), filename=path)

    @cache
    def document(path):
        data = read(path)
        if path.endswith(".toml"):
            return tomllib.loads(data.decode())
        if path.endswith(".gz"):
            data = gzip.decompress(data)
        return json.loads(data)

    @cache
    def digest(path):
        return hashlib.sha256(read(path)).hexdigest()

    def verify_hashes(hashes, dependencies, location, remediation):
        for dependency in sorted(dependencies):
            if not (root / dependency).resolve().is_relative_to(root.resolve()):
                require(False, location, f"source path leaves the repository: {dependency}")
                continue
            require(hashes.get(dependency) == digest(dependency), location,
                    f"missing or stale SHA-256 for {dependency}; {remediation}")

    def require(condition, location, message):
        report.checks += 1
        if not condition:
            report.errors.append(f"{identifier}: {location}: {message}")

    def compare(actual, expected, location):
        same_type = type(actual) is type(expected)
        both_numeric = type(actual) in (int, float) and type(expected) in (int, float)
        require((same_type or both_numeric) and actual == expected, location,
                f"expected {expected!r}{unit_label if type(expected) in (int, float) else ''}, found {actual!r}")

    def code(entry, expected):
        path = entry["path"]
        nodes = tuple(ast.walk(tree(path))) if {"uses", "keyword", "dict_key"} & entry.keys() else ()

        def assignment(node, name):
            location = f"{path}:{node.lineno} {name}"
            if "reference" in entry:
                expression = ast.unparse(ast.parse(entry["reference"], mode="eval").body)
                actual = ast.unparse(node)
                require(actual == expression, location,
                        f"expected source expression {expression!r}, found {actual!r}")
            else:
                compare(ast.literal_eval(node), expected, location)

        if "symbol" in entry:
            assignment(_assignment(tree(path), entry["symbol"]), entry["symbol"])
        if "import_module" in entry:
            package = ".".join(Path(path).parent.parts)
            imports = {
                alias.asname or alias.name: resolve_name(
                    f"{'.' * node.level}{node.module + '.' if node.module else ''}{alias.name}", package)
                for node in tree(path).body if isinstance(node, ast.ImportFrom)
                for alias in node.names
            }
            alias = entry["import_alias"]
            require(imports.get(alias) == entry["import_module"], path,
                    f"expected {alias!r} to import {entry['import_module']!r}, found {imports.get(alias)!r}")
        dotted = {ast.unparse(node) for node in nodes if isinstance(node, ast.Attribute)}
        for expression in entry.get("uses", []):
            require(expression in dotted, path, f"missing source expression {expression!r}")
        if "keyword" in entry:
            keyword = entry["keyword"]
            matches = [node.value for node in nodes if isinstance(node, ast.keyword) and node.arg == keyword]
            require(bool(matches), path, f"missing keyword {keyword!r}")
            for value in matches:
                assignment(value, keyword)
        if "dict_key" in entry:
            key = entry["dict_key"]
            matches = [
                value
                for node in nodes if isinstance(node, ast.Dict)
                for name, value in zip(node.keys, node.values)
                if isinstance(name, ast.Constant) and name.value == key
            ]
            require(bool(matches), path, f"missing dictionary key {key!r}")
            for value in matches:
                assignment(value, key)

    def record(entry, expected):
        path = entry["path"]
        rows = _lookup(document(path), entry.get("scope", ""))
        for prefix, row in rows:
            location = f"{path}:{prefix + '.' if prefix else ''}"
            for key in entry.get("keys", []):
                compare(_one(row, key), expected, location + key)
            for key, other in entry.get("matches", {}).items():
                require(_one(row, key) == _one(row, other), location + key,
                        f"does not match {other!r} in the same release record")
            for key, value in entry.get("fixed", {}).items():
                compare(_one(row, key), value, location + key)
            if "ratio" in entry:
                ratio = entry["ratio"]
                numerator, denominator = ratio["numerator"], ratio["denominator"]
                value = _one(row, numerator)
                if "multiply" in ratio:
                    value *= _one(row, ratio["multiply"])
                divisor = _one(row, denominator) if isinstance(denominator, str) else denominator
                compare(value / divisor, expected, location + numerator)
            if "external" in entry:
                other = entry["external"]
                for key, other_key in other["matches"].items():
                    require(_one(row, key) == _one(document(other["path"]), other_key), location + key,
                            f"does not match {other['path']}:{other_key}")
            if "path_key" in entry:
                field = entry["path_key"]
                compare(_one(row, field), entry["target_path"], location + field)
            for key in entry.get("provenance", []):
                hashes = _one(row, key)
                dependencies = set(entry.get("dependencies", [source]))
                if key in entry.get("verify_all_sources", []):
                    dependencies.update(hashes)
                verify_hashes(hashes, dependencies, location + key, "regenerate this record")
        require(bool(rows), path,
                f"no records matched {entry.get('scope', '')!r}")

    def reader(entry, expected):
        path = entry["path"]
        text = content(path)
        if "same_as" in entry:
            original = entry["same_as"]
            require(read(path) == read(original), path, f"differs from the maintained reader {original}")
        for pattern in entry.get("required", []):
            pattern = pattern.replace("{value}", re.escape(str(expected)))
            require(re.search(pattern, text, re.IGNORECASE | re.MULTILINE) is not None, path,
                    f"missing current claim or link matching {pattern!r}")
        for pattern in entry.get("forbidden", []):
            for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                require(False, f"{path}:{text.count(chr(10), 0, match.start()) + 1}",
                        f"unexpected live wording {match.group()!r}")
        for pattern in entry.get("values", []):
            matches = list(re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE))
            require(bool(matches), path, f"missing numeric claim matching {pattern!r}")
            for match in matches:
                token = match.group("value").casefold().replace(",", "")
                value = entry.get("words", {}).get(token, token)
                compare(float(value) * entry.get("scale", 1), expected,
                        f"{path}:{text.count(chr(10), 0, match.start()) + 1} {match.group()!r}")

    def artifact(entry, _expected):
        path = entry["path"]
        document_receipt = document(entry["receipt"])
        receipt = _one(document_receipt, entry.get("receipt_scope", ""))
        if "receipt_scope" not in entry:
            compare(receipt["artifact"], path, entry["receipt"])
        if path.endswith(".pdf"):
            require(read(path).startswith(b"%PDF-"), path, "missing PDF file signature")
        artifact_hash = (hashlib.sha256(gzip.decompress(read(path))).hexdigest()
                         if entry.get("gzip_digest") else digest(path))
        require(receipt[entry.get("digest_key", "sha256")] == artifact_hash, path,
                f"artifact digest differs from {entry['receipt']}; rebuild the artifact and receipt")
        hashes = _one(document_receipt, entry.get("source_key", "source_sha256"))
        require(set(entry["sources"]) <= set(hashes), entry["receipt"],
                "receipt is missing required sources from the live register")
        verify_hashes(hashes, hashes, entry["receipt"], "rebuild the artifact and receipt")

    def inventory(spec, entries, expected):
        """Find newly claimed live values or inbound links outside registered readers."""
        monitored = {entry["path"] for entry in entries}
        for path in spec.get("retained", {}):
            require((root / path).is_file(), path, "retained comparison moved or is missing")
        targets = set(spec.get("targets", []))
        markers = [re.compile(pattern, re.I) for pattern in spec.get("markers", [])]
        paths = {path for pattern in spec["globs"] for path in root.glob(pattern) if path.is_file()}
        for path in sorted(paths):
            relative = path.relative_to(root).as_posix()
            if relative in spec.get("retained", {}):
                continue
            for line_number, line in enumerate(content(relative).splitlines(), 1):
                location = f"{relative}:{line_number}"
                claims = [match for marker in markers for match in marker.finditer(line)]
                if relative in monitored:
                    if relative in spec.get("strict_readers", []):
                        for pattern in spec.get("obsolete_claims", []):
                            for match in re.finditer(pattern, line, re.IGNORECASE):
                                require(False, location, f"obsolete live claim {match.group()!r}")
                    for claim in claims:
                        value = claim.groupdict().get("value")
                        if value is not None:
                            compare(float(value), expected, f"{location} {claim.group()!r}")
                    continue
                if not claims and "](" not in line:
                    continue
                links = re.findall(r"\]\(([^#? )]+)", line)
                linked_paths = {
                    (path.parent / link).resolve().relative_to(root.resolve()).as_posix()
                    for link in links
                    if not re.match(r"\w+:", link)
                    and (path.parent / link).resolve().is_relative_to(root.resolve())
                }
                if targets.intersection(linked_paths) or claims:
                    require(False, location,
                            "unregistered live claim or pointer; classify this reader in the register")

    try:
        specifications = document(REGISTER)["spec"]
        if not specifications:
            raise ValueError("register has no specifications")
    except (OSError, KeyError, ValueError, TypeError) as error:
        report.errors.append(f"{REGISTER}: {error}")
        return report

    identifiers = set()
    for spec in specifications:
        identifier = spec.get("id", REGISTER)
        report.specifications += 1
        if identifier in identifiers:
            report.errors.append(f"{REGISTER}: duplicate specification {identifier!r}")
            continue
        identifiers.add(identifier)
        unit_label = f" {spec['unit']}" if "unit" in spec else ""
        source = spec.get("source", REGISTER)
        try:
            if source.endswith(".py"):
                expected = _literal(_assignment(tree(source), spec["symbol"]), spec.get("key"))
            else:
                expected = _one(document(source), spec["key"])
            require(type(expected) in (float, int, str), source,
                    "authority must be a scalar literal")
        except (OSError, KeyError, SyntaxError, ValueError, TypeError) as error:
            report.errors.append(f"{identifier}: {source}: {error}")
            continue
        for kind, validate in (("code", code), ("record", record), ("reader", reader),
                               ("artifact", artifact)):
            for entry in spec.get(kind, []):
                try:
                    validate(entry, expected)
                except (OSError, IndexError, KeyError, SyntaxError, ValueError, TypeError, AttributeError,
                        ZeroDivisionError, ImportError, re.error) as error:
                    report.errors.append(f"{identifier}: {entry.get('path', REGISTER)}: {error}")
        if "inventory" in spec:
            try:
                inventory(spec["inventory"], spec.get("reader", []), expected)
            except (OSError, KeyError, ValueError, TypeError) as error:
                report.errors.append(f"{identifier}: reader inventory: {error}")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="root containing the live register")
    args = parser.parse_args(argv)
    report = check(args.root)
    if report.errors:
        for error in report.errors:
            print(error)
        print(f"Live coherence failed with {len(report.errors)} errors in {report.checks} checks")
        return 1
    print(f"Live coherence passed {report.checks} checks across {report.specifications} specifications")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
