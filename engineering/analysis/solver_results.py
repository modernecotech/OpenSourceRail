"""Versioned native nodal result adapters for the civil evidence exchange.

Units and node/case allocation come from the independently reviewed model/output
specification. CSV values are generated from these adapters and checked again at
inspection. Unknown response formats fail closed rather than trusting a CSV.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import re

PARSERS = {"opensees": "opensees-node-recorder/1", "calculix": "calculix-nodal-dat/1"}
FIELDS = ("asset_id", "load_case_id", "metric", "value", "unit")
UNITS = {"displacement": {"m": 1., "mm": .001}, "force": {"N": 1., "kN": 1000.}}


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def parser_provenance(solver: str, spec: dict) -> dict:
    return {"id": PARSERS[solver], "version": "1", "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "spec_sha256": digest(spec), "model_sha256": spec["model_sha256"]}


def number(value) -> float:
    if isinstance(value, bool): raise ValueError("boolean measurement")
    n = float(str(value).replace("D", "E"))
    if not math.isfinite(n): raise ValueError("non-finite native value")
    return n


def opensees_value(path: Path, definition: dict, selector: dict) -> float:
    nodes, dofs = definition["nodes"], definition["dofs"]
    if (not nodes or not dofs or len(set(nodes)) != len(nodes) or len(set(dofs)) != len(dofs)
        or any(type(i) is not int or i < 1 for i in (*nodes, *dofs)) or definition["time_column"] is not True):
        raise ValueError("invalid OpenSees recorder definition")
    expected_response = {"displacement": "disp", "force": "reaction"}[selector["quantity"]]
    if definition["response"] != expected_response: raise ValueError("recorder response differs from quantity")
    column = 1 + nodes.index(selector["node_id"])*len(dofs) + dofs.index(selector["dof"])
    samples = {}
    for line in path.read_text().splitlines():
        if not line.strip(): continue
        fields = [number(v) for v in line.split()]
        if len(fields) != 1 + len(nodes)*len(dofs): raise ValueError("OpenSees recorder column count mismatch")
        if fields[0] in samples: raise ValueError("duplicate native recorder time")
        samples[fields[0]] = fields[column]
    target = number(selector["time"])
    matches = [v for t,v in samples.items() if math.isclose(t,target,rel_tol=0.,abs_tol=1e-12)]
    if len(matches) != 1: raise ValueError("native recorder sample missing or ambiguous")
    return matches[0]


def calculix_value(path: Path, definition: dict, selector: dict) -> float:
    if selector["dof"] not in (1,2,3) or type(selector["dof"]) is not int: raise ValueError("unsupported nodal DOF")
    response = {"displacement": "displacements", "force": "forces"}[selector["quantity"]]
    header = re.compile(r"^\s*(displacements|forces)\s+\([^)]+\)\s+for set\s+(\S+)\s+and time\s+(\S+)\s*$", re.I)
    step = None; block = None; values = {}
    for line in path.read_text().splitlines():
        if match := re.search(r"\bS\s*T\s*E\s*P\s+(\d+)", line):
            step = int(match[1]); block = None
        elif match := header.match(line):
            components = "vx,vy,vz" if match[1].lower() == "displacements" else "fx,fy,fz"
            actual_components = re.search(r"\(([^)]+)\)", line)[1].replace(" ", "").lower()
            if actual_components != components: raise ValueError("unsupported native vector component order")
            block = (step, match[1].lower(), match[2].upper(), number(match[3]))
        elif block and line.strip():
            fields = line.split()
            if len(fields) == 4 and fields[0].isdigit():
                key = (*block,int(fields[0]))
                if key in values: raise ValueError("duplicate native nodal result")
                values[key] = [number(v) for v in fields[1:]]
            else:
                block = None
    if type(selector["step"]) is not int or selector["step"] < 1: raise ValueError("invalid native step")
    key = (selector["step"],response,selector["set_name"].upper(),number(selector["time"]),selector["node_id"])
    if key not in values: raise ValueError("native step/set/time/node result missing")
    return values[key][selector["dof"]-1]


def extract_results(report: dict, root: Path, register: dict, solver: str) -> list[dict]:
    try:
        from engineering.analysis.civil_evidence import controlled_path
    except ModuleNotFoundError:
        from civil_evidence import controlled_path
    spec = register["native_output_spec"][solver]
    if spec["parser_id"] != PARSERS[solver] or report.get("native_parser") != parser_provenance(solver,spec):
        raise ValueError("native parser identity/version/source/spec provenance mismatch")
    if not spec["model_sha256"] or spec["model_sha256"] != report.get("input_sha256"):
        raise ValueError("native result specification binds a different model")
    criteria = {(r["asset_id"],r["load_case_id"],r["metric"]): r for r in register["criteria"][solver]}
    keys = [(s["asset_id"],s["load_case_id"],s["metric"]) for s in spec["selectors"]]
    if len(set(keys)) != len(keys) or set(keys) != set(criteria): raise ValueError("native selector asset/case/metric coverage mismatch")
    files = spec["files"]
    if set(files) != set(report["native_output_paths"]): raise ValueError("native file specification coverage mismatch")
    results = []
    for selector,key in zip(spec["selectors"],keys):
        if type(selector["node_id"]) is not int or selector["node_id"] < 1 or type(selector["dof"]) is not int:
            raise ValueError("native node/DOF IDs must be positive integers")
        path = selector["path"]
        if path not in files or path not in report["output_hashes"]: raise ValueError("native selector file not controlled")
        definition = files[path]
        quantity = selector["quantity"]
        unit = criteria[key]["unit"]
        # Native solver output has no intrinsic units: pin the model unit basis
        # in the reviewed spec rather than letting CSV authors choose a scale.
        source_unit = spec["model_units"][quantity]
        scale = UNITS[quantity][source_unit]/UNITS[quantity][unit]
        reader = opensees_value if solver == "opensees" else calculix_value
        value = reader(controlled_path(root,path),definition,selector)*scale
        operation = selector["operation"]
        if operation == "abs": value = abs(value)
        elif operation != "signed": raise ValueError("unsupported native reduction")
        results.append(dict(zip(FIELDS,(*key,number(value),unit))))
    return results


def write_exchange(path: Path, rows: list[dict]) -> None:
    with path.open("w",newline="") as stream:
        writer = csv.DictWriter(stream,fieldnames=FIELDS,lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
