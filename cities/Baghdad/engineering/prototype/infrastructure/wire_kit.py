"""Prepare unenergised point-to-point wire cut labels from a supplier's drawing issue."""
import argparse
import csv
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import BadZipFile, ZipFile

HERE = Path(__file__).resolve().parent
FIELDS = ("candidate_id", "packet_evaluation_id", "drawing_revision", "wire_spec", "data_class",
          "article", "scope", "interface", "wire_id", "from_connector", "from_pin", "to_connector",
          "to_pin", "route_mm", "service_slack_mm", "from_end_allowance_mm", "to_end_allowance_mm")
UNKNOWN = {"", "?", "-", "tbd", "tbc", "n/a", "unknown", "none", "open", "null"}
CLASSES = {"practice", "supplier-proposal"}


def digest(data):
    return sha256(data).hexdigest()


def drawing_identity():
    drawings = HERE.parent / "drawings"
    if drawings.is_dir():
        manifest = (drawings / "manifest.json").read_bytes()
        opening = (drawings / "opening.json").read_bytes()
    else:
        with ZipFile(HERE.parent / "airport-prototype.zip") as issue:
            manifest = issue.read("manifest.json")
            opening = issue.read("opening.json")
    issued = json.loads(manifest)
    if digest(opening) != issued["sha256"]["opening.json"] or json.loads(opening)["candidate_id"] != issued["candidate_id"]:
        raise ValueError("Opening drawing differs from its packet manifest")
    return issued["candidate_id"], issued["evaluation_id"], digest(manifest)


def csv_bytes(fields, rows):
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def build(raw, revision, wire_spec):
    candidate, packet, manifest_hash = drawing_identity()
    scope_data = (HERE / "connector-return.csv").read_bytes()
    allowed = {(r["scope"], r["interface"]) for r in csv.DictReader(StringIO(scope_data.decode()))}
    reader = csv.DictReader(StringIO(raw.decode("utf-8-sig"), newline=""))
    if not reader.fieldnames or sorted(reader.fieldnames) != sorted(FIELDS):
        raise ValueError("Header must contain the wire-practice.csv columns exactly once")
    seen_wires, seen_pins = set(), set()
    labels, checks = [], []
    classes = set()
    for idx, row in enumerate(reader, 2):
        if None in row or any(v is None for v in row.values()):
            raise ValueError(f"Line {idx} has missing or extra columns")
        r = {k: v.strip() for k, v in row.items()}
        missing = [k for k, v in r.items() if v.casefold() in UNKNOWN]
        if missing:
            raise ValueError(f"Line {idx} needs a value for {', '.join(missing)}")
        if (r["candidate_id"], r["packet_evaluation_id"], r["drawing_revision"], r["wire_spec"]) != (
                candidate, packet, revision, wire_spec):
            raise ValueError(f"Line {idx} has a different candidate, packet, drawing revision or wire specification")
        classes.add(r["data_class"])
        if not classes <= CLASSES or len(classes) != 1 or (r["scope"], r["interface"]) not in allowed:
            raise ValueError(f"Line {idx} has an unknown interface, scope or mixed data class")
        if r["wire_id"].casefold() in seen_wires:
            raise ValueError(f"Line {idx} repeats a wire ID")
        seen_wires.add(r["wire_id"].casefold())
        for side in ("from", "to"):
            pin = (r["article"].casefold(), r[side + "_connector"].casefold(), r[side + "_pin"].casefold())
            if pin in seen_pins:
                raise ValueError(f"Line {idx} repeats a terminal/pin on this article")
            seen_pins.add(pin)
        keys = ("route_mm", "service_slack_mm", "from_end_allowance_mm", "to_end_allowance_mm")
        if any(not r[k].isascii() or not r[k].isdecimal() for k in keys) or int(r["route_mm"]) <= 0:
            raise ValueError(f"Line {idx} needs a positive route and explicit nonnegative whole-millimetre allowances")
        ends = {k: r[k] for k in ("article", "scope", "interface", "wire_id", "from_connector", "from_pin", "to_connector", "to_pin")}
        labels.append(dict(**ends, **{k: int(r[k]) for k in keys}, cut_mm=sum(int(r[k]) for k in keys)))
        checks.append(dict(**ends, independently_checked_drawing="", instrument_and_calibration="", limit_ref="",
                           observed_from="", observed_to="", continuity_reading_and_unit="", unintended_path_check="",
                           disposition="", inspection_ref=""))
    if not labels:
        raise ValueError("The proposed list contains no wires")
    provenance = dict(candidate_id=candidate, packet_evaluation_id=packet, drawing_revision=revision,
                      wire_spec=wire_spec, data_class=classes.pop(), wire_list_sha256=digest(raw),
                      drawing_manifest_sha256=manifest_hash, connector_scope_sha256=digest(scope_data),
                      method_sha256=digest(Path(__file__).read_bytes()))
    evaluation = digest(json.dumps(provenance, sort_keys=True).encode())
    key = dict(kit_evaluation_id=evaluation, candidate_id=candidate, packet_evaluation_id=packet,
               drawing_revision=revision, wire_spec=wire_spec, data_class=provenance["data_class"])
    out = {}
    for filename, table in [("wire-cut-labels.csv", labels), ("continuity-traveller.csv", checks)]:
        rows = [{**key, **r} for r in table]
        out[filename] = csv_bytes(tuple(rows[0]), rows)
    result = dict(**provenance, kit_evaluation_id=evaluation, wire_count=len(labels),
                  total_cut_mm=sum(r["cut_mm"] for r in labels), fabrication_released=False,
                  energisation_authorised=False, artifact_sha256={k: digest(v) for k, v in out.items()})
    out["wire-kit.json"] = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wire_list", type=Path)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--wire-spec", required=True)
    parser.add_argument("--output", type=Path, required=True, help="new directory under an existing parent")
    args = parser.parse_args()
    try:
        outputs = build(args.wire_list.read_bytes(), args.revision, args.wire_spec)
        if args.output.exists():
            raise ValueError("Use a new output directory to preserve previous traveller records")
        with TemporaryDirectory(dir=args.output.parent) as temp:
            stage = Path(temp) / "issue"
            stage.mkdir()
            for name, content in outputs.items():
                (stage / name).write_bytes(content)
            stage.rename(args.output)
    except (ValueError, OSError, BadZipFile, KeyError, csv.Error) as error:
        parser.exit(2, f"{parser.prog}: {error}\n")
    print(args.output / "wire-kit.json")


if __name__ == "__main__":
    main()
