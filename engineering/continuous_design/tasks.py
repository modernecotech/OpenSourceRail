"""Controlled candidate domains shared by the planner and independent workers."""
from copy import deepcopy
import ast
import itertools
import json
from pathlib import Path

from engineering.twin_workflow import core

ROOT = core.ROOT
LANES = ("mechanical", "civil", "software", "integration")
KINDS = {"mechanical-cleat": "mechanical", "mechanical-interface": "mechanical",
         "mechanical-detail": "mechanical", "civil-steel-beam": "civil", "civil-bay": "civil",
         "civil-detail": "civil", "software-logic": "software",
         "integration-reference": "integration", "integration-coupling": "integration"}
FACTS = ("train_stopped", "hvil_closed", "insulation_ok", "main_feedback_open",
         "return_feedback_closed", "precharge_feedback_closed", "voltage_ready", "timeout_ok",
         "data_valid", "age_valid", "sequence_valid", "clocks_valid")


def task(kind, parameters, rationale="Declared research candidate", parent=None):
    return dict(kind=kind, parameters=parameters, rationale=rationale, parent=parent)


def expression(source):
    if not isinstance(source, str) or not 1 <= len(source) <= 4000:
        raise ValueError("bounded Boolean policy expression required")
    node = ast.parse(source, mode="eval")
    nodes = list(ast.walk(node))
    if len(nodes) > 200 or any(not isinstance(n, (ast.Expression, ast.BoolOp, ast.UnaryOp,
        ast.And, ast.Or, ast.Not, ast.Name, ast.Load, ast.Constant)) for n in nodes):
        raise ValueError("policy permits Boolean operators and declared facts only")
    if any(isinstance(n, ast.Name) and n.id not in FACTS for n in nodes) or any(
        isinstance(n, ast.Constant) and type(n.value) is not bool for n in nodes):
        raise ValueError("unknown fact or non-Boolean constant")
    return compile(node, "<generated-controller-policy>", "eval")


def contexts(kind):
    from engineering.generative_design import mechanical_detail, civil_detail
    module = mechanical_detail if kind == "mechanical-detail" else civil_detail
    return module, {c["id"]: c for c in module.contexts()}


def validate(value):
    if not isinstance(value, dict) or set(value) != {"kind", "parameters", "rationale", "parent"}:
        raise ValueError("exact task contract required")
    kind, params = value["kind"], value["parameters"]
    if kind not in KINDS or not isinstance(params, dict):
        raise ValueError("unavailable adapter; retain an adapter-development need")
    if not isinstance(value["rationale"], str) or not 1 <= len(value["rationale"]) <= 8000:
        raise ValueError("bounded rationale required")
    if value["parent"] is not None and (not isinstance(value["parent"], str) or len(value["parent"]) != 64):
        raise ValueError("parent must be a design digest")
    if len(core.encoded(value)) > 600_000:
        raise ValueError("candidate exceeds 600 kB")
    if kind in ("mechanical-cleat", "civil-steel-beam", "civil-bay"):
        core.validate(dict(schema="osr-twin-proposal/1", id="worker", baseline_sha256="0" * 64,
            kind=kind, parameters=params, rationale=value["rationale"], sources=[], expected_tests=["fixed worker checks"]), "0" * 64)
    elif kind == "mechanical-interface":
        domains = dict(carrier_wall_m=[.003, .004, .005], sill_wall_m=[.006, .008, .010])
        if set(params) != set(domains) or any(type(v) not in (int, float) or v not in domains[k] for k, v in params.items()):
            raise ValueError("interface dimensions outside research domain")
    elif kind.endswith("-detail"):
        module, mapping = contexts(kind)
        if set(params) != {"context_id", "variables"} or params["context_id"] not in mapping:
            raise ValueError("exact configuration context required")
        spec = core.read(module.DATA if kind == "mechanical-detail" else ROOT / "engineering/generative_design/data/civil-detail-space.json")
        domain = spec["bounds"] if kind == "mechanical-detail" else spec["domains"]
        variables = params["variables"]
        if not isinstance(variables, dict) or set(variables) != set(domain) or any(
            type(v) not in (int, float) or v not in domain[k] for k, v in variables.items()):
            raise ValueError("detail variables outside controlled domains")
    elif kind == "software-logic":
        if set(params) != {"expression"}:
            raise ValueError("software requires one Boolean policy expression")
        expression(params["expression"])
    elif kind == "integration-reference":
        if params:
            raise ValueError("reference integration audit is fixed")
    elif kind == "integration-coupling":
        if set(params) != {"children"} or len(params["children"]) != 3 or any(
            not isinstance(k, str) or len(k) != 64 or any(c not in "0123456789abcdef" for c in k) for k in params["children"]):
            raise ValueError("three exact mechanical/civil/software child digests required")
    return KINDS[kind]


def identity(value, baseline):
    validate(value)
    parameters = value["parameters"]
    if value["kind"] == "software-logic":
        # Syntactically different expressions with identical behaviour are not
        # new designs. Preserve the first source and deduplicate its truth table.
        code = expression(parameters["expression"])
        table = [eval(code, {"__builtins__": {}}, dict(zip(FACTS, values)))
                 for values in itertools.product((False, True), repeat=len(FACTS))]
        parameters = dict(guard_truth_table_sha256=core.digest(table))
    return core.digest(dict(baseline=baseline, kind=value["kind"], parameters=parameters))


def seeds():
    from engineering.design_engine.generated_parts import variables
    values = [task("integration-reference", {})]
    # Negative controls are retained alongside a complete Boolean guard policy.
    for source in ("voltage_ready", "voltage_ready and timeout_ok", " and ".join(FACTS)):
        values.append(task("software-logic", dict(expression=source)))
    for kind in ("mechanical-detail", "civil-detail"):
        module, mapping = contexts(kind)
        values += [task(kind, dict(context_id=k, variables=module.seed(v))) for k, v in mapping.items()]
    for carrier, sill in ((.003, .008), (.004, .008), (.004, .010)):
        values.append(task("mechanical-interface", dict(carrier_wall_m=carrier, sill_wall_m=sill)))
    for length in (20., 25.):
        values.append(task("civil-bay", dict(length=length, pier_height=8., pile_length=15., pile_spacing=2.)))
    for kind in ("mechanical-cleat", "civil-steel-beam"):
        domain = variables(kind)
        for row in itertools.product(*(v["choices"] for v in domain.values())):
            values.append(task(kind, dict(zip(domain, row))))
    return values


def interface(parameters):
    from engineering.design_consistency import demonstrators as d
    from engineering.design_consistency.contracts import member, part
    contract = d.interface()
    for i, original in enumerate(contract["parts"]):
        name = original["id"]
        if name.startswith("battery-carrier-"):
            contract["parts"][i] = member(name, 1.2, .08, .05, parameters["carrier_wall_m"], "steel",
                contract["materials"], (0, -.22 if name.endswith("0") else .22, -.19))
        if name.startswith("sill-"):
            new = member(name, 2., .16, .28, parameters["sill_wall_m"], "steel", contract["materials"],
                         (0, -.45 if name.endswith("0") else .45, 0))
            top = new["manufacturing"]["primitives"][0]
            top.update(kind="plate", holes_xy_m=[[x, 0] for x in [-.9, -.6, .6, .9]], hole_radius_m=.007)
            contract["parts"][i] = part(name, "steel", new["manufacturing"], contract["materials"], section=new["analysis"]["section"])
        if name.startswith("bolt-"):
            # Keep the nut under the changed sill flange and regenerate the
            # shank grip length. A wall edit alone otherwise embeds the nut in
            # the flange; native collision checking caught that initial trial.
            spec = deepcopy(original["manufacturing"])
            delta = .008 - parameters["sill_wall_m"]
            for primitive in spec["primitives"]:
                if primitive["id"] == "nut":
                    primitive["centre_m"][2] += delta
                if primitive["id"] == "bolt":
                    primitive["length_m"] -= delta
                    primitive["centre_m"][2] += delta / 2
            contract["parts"][i] = part(name, "fastener", spec, contract["materials"],
                inspections=["research grip and underside clearance", "supplier threads/preload remain open"])
    contract["revision"] = "CONTINUOUS-INTERFACE-" + core.digest(parameters)[:12]
    return contract


def domain_description(lane):
    if lane in ("mechanical", "civil"):
        kind = lane + "-detail"
        module, mapping = contexts(kind)
        spec = core.read(module.DATA if lane == "mechanical" else ROOT / "engineering/generative_design/data/civil-detail-space.json")
        result = {kind: dict(context_ids=list(mapping), variables=spec["bounds" if lane == "mechanical" else "domains"])}
        if lane == "mechanical":
            result["mechanical-interface"] = dict(carrier_wall_m=[.003, .004, .005], sill_wall_m=[.006, .008, .010])
            result[kind]["family_bounds"] = {k: module.stiffness_bound(v) for k, v in mapping.items()}
            result[kind]["search_instruction"] = "Do not resample an incompatible constant-EI LM3 family. Record an alternative-load-path adapter need; six-car hypotheses remain independent."
        else:
            result["civil-bay"] = dict(length=[20., 25.], pier_height=[6., 8.], pile_length=[12., 15.], pile_spacing=[2., 2.5])
        from engineering.design_engine.generated_parts import variables
        family = "mechanical-cleat" if lane == "mechanical" else "civil-steel-beam"
        result[family] = variables(family)
        return result
    if lane == "software":
        return {"software-logic": dict(expression="Boolean and/or/not expression over " + ", ".join(FACTS),
                acceptance="Fixed exhaustive truth table plus independently specified temporal replay; no calls/imports")}
    return {"integration-coupling": dict(children="Exactly three completed mechanical-detail, matching civil-detail and software-logic design keys")}
