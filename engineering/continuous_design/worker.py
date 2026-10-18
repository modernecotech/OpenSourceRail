"""Fixed evaluation tools. Generated software is a restricted Boolean AST only."""
from copy import deepcopy
import ast
import itertools
import math
from pathlib import Path

from engineering.twin_workflow import core
from . import tasks, planning, evidence, eligibility


def software(source):
    code = tasks.expression(source)
    def decide(facts):
        return eval(code, {"__builtins__": {}}, facts)
    mismatches = []
    for values in itertools.product((False, True), repeat=len(tasks.FACTS)):
        facts = dict(zip(tasks.FACTS, values))
        actual = decide(facts)
        if type(actual) is not bool or actual is not all(values):
            if len(mismatches) < 20:
                mismatches.append(dict(facts=facts, expected=all(values), actual=actual))
    from engineering.generative_design.twin_software_factory import fault_suite, GUARDS
    rows = []
    cases = fault_suite()
    healthy = deepcopy(cases[0]["frames"][0])
    ramp = deepcopy(healthy)
    ramp.update(sequence=0, observed_s=.2, received_s=.21)
    ramp["signals"].update(elapsed_s=.2, link_voltage_ratio=.5)
    cases.append(dict(id="normal-voltage-ramp-can-complete", frames=[ramp, healthy], expected_request=True))
    for case in cases:
        locked, previous_seq, previous_time, previous_receipt = False, -1, -1., -1.
        actuals = []
        for frame in case["frames"]:
            facts = {name: False for name in tasks.FACTS}
            try:
                signals = frame["signals"]
                seq, observed, received = frame["sequence"], frame["observed_s"], frame["received_s"]
                numeric = [observed, received, signals["elapsed_s"], signals["link_voltage_ratio"]]
                valid = all(type(x) in (int, float) and math.isfinite(x) and x >= 0 for x in numeric)
                valid = valid and type(seq) is int and seq >= 0 and signals["link_voltage_ratio"] <= 1.05
                valid = valid and all(type(signals[k]) is bool for k in GUARDS)
                if valid:
                    facts.update({k: signals[k] for k in GUARDS})
                    facts.update(data_valid=True, voltage_ready=signals["link_voltage_ratio"] >= .95,
                        timeout_ok=signals["elapsed_s"] <= 5., age_valid=0 <= received - observed <= .1,
                        sequence_valid=seq > previous_seq and observed >= previous_time,
                        clocks_valid=received >= previous_receipt and abs(signals["elapsed_s"] - observed) <= 1e-6)
                    previous_seq, previous_time, previous_receipt = seq, observed, received
            except (KeyError, TypeError, ValueError):
                pass
            request = decide(facts) and not locked
            # Low voltage during an otherwise healthy precharge is not a fault.
            # A premature close must fail; the subsequent valid ramp may finish.
            if not all(v for k, v in facts.items() if k != "voltage_ready"):
                locked = True
            actuals.append(bool(request))
        rows.append(dict(id=case["id"], expected=case["expected_request"], actual=actuals[-1],
                         passed=actuals[-1] is case["expected_request"], requests=actuals))
    return dict(study_pass=not mismatches and all(r["passed"] for r in rows),
        metrics=dict(truth_table_cases=2**len(tasks.FACTS), temporal_cases=len(rows),
                     failed_temporal_cases=sum(not r["passed"] for r in rows)),
        checks=dict(exhaustive_guard_logic=not mismatches, temporal_fault_suite=all(r["passed"] for r in rows)),
        counterexamples=mismatches, replay=rows,
        open_evidence=["target executable and platform", "full train software", "SIL/HIL and real-time timing", "physical switching and independent acceptance"],
        scope="Generated Boolean control policy in a fixed offline latch/replay wrapper; no live command", **core.FLAGS)


def child_records(envelope):
    rows = []
    for child in envelope["dependencies"]:
        folder = Path(child["folder"])
        if core.sha(folder / "receipt.json") != child["receipt_sha256"]:
            raise ValueError("child receipt changed")
        receipt = core.read(folder / "receipt.json", maximum=10_000_000)
        if receipt["baseline_sha256"] != envelope["baseline_sha256"] or receipt["key"] != child["key"]:
            raise ValueError("child belongs to another exact baseline")
        for relative, expected in receipt["files_sha256"].items():
            path = (folder / relative).resolve()
            if not path.is_relative_to(folder.resolve()) or core.sha(path) != expected:
                raise ValueError("child artifact changed")
        rows.append(dict(key=child["key"], task=child["task"], folder=str(folder),result=core.read(folder / "result.json", maximum=10_000_000)))
    return rows


def integration(envelope):
    rows = child_records(envelope)
    by_kind = {r["task"]["kind"]: r for r in rows}
    protocol='software-receiver' in by_kind
    kinds={"mechanical-detail", "civil-detail", "software-logic"}|({'software-receiver'} if protocol else set())
    if len(rows) != len(kinds) or set(by_kind) != kinds:
        raise ValueError("integration requires exact mechanical/civil/software children")
    from engineering.generative_design import civil_detail
    mechanical = by_kind["mechanical-detail"]["result"]["assessment"]
    civil = by_kind["civil-detail"]["result"]["assessment"]
    context = next(c for c in civil_detail.contexts() if c["id"] == civil["context_id"])
    if context["architecture_id"] != mechanical["configuration_id"]:
        raise ValueError("mechanical and civil configurations differ")
    mass = mechanical["objectives"]["mass_kg"]
    cars = 3 if mechanical["configuration_id"] == "LM3" else 6
    coupled = civil_detail.coupled_context(context, mass * cars)
    reassessed = civil_detail.assess(civil["variables"], coupled)
    baseline_force = sum(a["force_n"] for a in context["source_case"]["axles"])
    coupled_force = sum(a["force_n"] for a in coupled["source_case"]["axles"])
    live=eligibility.live_dependencies(envelope)
    expected_revision=envelope.get('task',{}).get('parameters',{}).get('evidence_revision')
    checks = dict(exact_child_revisions=True, same_configuration=True,
        applicable_child_evidence=live['eligible'] and (expected_revision is None or expected_revision==core.digest(live)),
        positive_gross_mass_increases_axle_force=coupled_force > baseline_force,
        civil_response_recomputed=not reassessed["failed_checks"],
        civil_child_study=by_kind["civil-detail"]["result"]["study_pass"],
        mechanical_child_study=by_kind["mechanical-detail"]["result"]["study_pass"],
        software_child_study=by_kind["software-logic"]["result"]["study_pass"])
    protocol_result=None
    if protocol:
        from . import protocol_system
        protocol_result=protocol_system.evaluate(by_kind)
        checks.update(protocol_child_study=by_kind['software-receiver']['result']['study_pass'],
            protocol_fault_propagation=protocol_result['study_pass'])
    parameters=dict(children=[r['key'] for r in rows])
    if protocol:parameters['interface_id']='osr-precharge-link/1'
    parent = envelope.get("key") or tasks.identity(tasks.task('integration-protocol' if protocol else "integration-coupling", parameters), envelope["baseline_sha256"])
    repairs = [tasks.task("civil-detail", dict(context_id=context["id"], variables=p),
        "Repair actual coupled-load failures: " + ", ".join(reassessed["failed_checks"]) +
        "; re-evaluate base context first, then recompute exact coupling", parent=parent)
        for p in civil_detail.propose(reassessed, coupled)[:4]]
    return dict(study_pass=all(checks.values()), checks=checks,
        failed_checks=[name for name, passed in checks.items() if not passed],
        check_details=reassessed["checks"], repairs=repairs,
        metrics=dict(gross_added_mass_kg=mass*cars, baseline_axle_force_n=baseline_force,
                     coupled_axle_force_n=coupled_force, failed_civil_checks=reassessed["failed_checks"]),
        assessment=reassessed, children=[dict(key=r["key"], kind=r["task"]["kind"], study_pass=r["result"]["study_pass"]) for r in rows],
        protocol_link=protocol_result,
        input_evidence=live,
        evaluation_disposition='superseded' if expected_revision is not None and expected_revision!=core.digest(live) else 'current',
        adopted=False, scope="One-way gross-mass sensitivity on exact child revisions; additional protocol tasks compose receiver/control executables through a declared offline interface. No removal credit, dynamic coupling or hardware integration",
        open_evidence=["net installed vehicle mass/CG", "coupled vehicle-track-structure dynamics", "hardware/software interfaces", "physical correlation"], **core.FLAGS)


def evaluate(envelope, output):
    value = envelope["task"]
    tasks.validate(value)
    kind, params = value["kind"], value["parameters"]
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    if kind in tasks.STUDY_KINDS:
        from . import expansion
        result=expansion.evaluate(kind,params,output)
        result['repairs']=expansion.repair_tasks(kind,params,result,envelope)
    elif kind in ('mechanical-study-confirmation','civil-study-confirmation'):
        from . import study_confirmation
        result=study_confirmation.evaluate(envelope,output,child_records(envelope))
    elif kind in ("mechanical-detail", "civil-detail"):
        module, mapping = tasks.contexts(kind)
        assessed = module.assess(params["variables"], mapping[params["context_id"]])
        failed = assessed["failed_check_ids"] if kind == "mechanical-detail" else assessed["failed_checks"]
        bound = assessed.get("basis", {}).get("constant_ei_family_stiffness_bound")
        blocked = bound if bound and bound["research_family_screen_incompatible"] else None
        proposals = [] if blocked else (module.propose(assessed, mapping[params["context_id"]])[:4]
            if failed else planning.lighter_neighbors(kind, params))
        result = dict(study_pass=not failed, assessment=assessed, metrics=assessed["objectives"],
            failed_checks=failed, checks={r["id"]: r["state"] for r in assessed["checks"]},
            check_details=assessed["checks"], search_blocked=blocked,
            needs=[dict(item_id="LM3-alternative-load-path-adapter", required=blocked["required_decision"])] if blocked else [],
            repairs=[tasks.task(kind, dict(context_id=params["context_id"], variables=p),
                rationale=("Repair proposed from actual failed checks: " + ", ".join(failed) if failed else
                    "Explore a nearby material-saving geometry; re-evaluate all fixed checks"), parent=envelope["key"]) for p in proposals],
            scope="Configuration-specific analytical detail screens; unknown acceptance remains open", **core.FLAGS)
        core.write(output / "model-definition.json", module.model_definition(assessed), exclusive=True)
    elif kind == "software-logic":
        result = software(params["expression"])
        (output / "generated-controller.py").write_text(
            "# Research policy only; fixed wrapper validates facts and latches faults.\n"
            "def closure_request(*, " + ", ".join(tasks.FACTS) + "):\n    return " +
            ast.unparse(ast.parse(params["expression"], mode="eval").body) + "\n")
    elif kind == "software-receiver":
        from . import protocol_receiver
        result=protocol_receiver.evaluate(params,output)
    elif kind == "integration-reference":
        from engineering.generative_design import digital_thread
        checked = digital_thread.verify(core.PACKET)
        result = dict(study_pass=checked["integrity_verified"], checks=dict(current_reference_integrity=checked["integrity_verified"]),
            metrics=checked["summary"], scope="Current federated configuration/source audit; open interfaces retained", **core.FLAGS)
    elif kind in {"integration-coupling",'integration-protocol'}:
        result = integration(envelope)
    elif kind.endswith("-confirmation"):
        from . import confirmation
        result=confirmation.evaluate(envelope,output,child_records(envelope))
    else:
        from engineering.twin_workflow.adapters import evaluate as native_evaluate
        native_kind = "controlled-assembly" if kind == "mechanical-interface" else kind
        native_params = dict(contract=tasks.interface(params)) if kind == "mechanical-interface" else params
        proposal = dict(schema="osr-twin-proposal/1", id=envelope["key"], baseline_sha256=envelope["baseline_sha256"],
            kind=native_kind, parameters=native_params, rationale=value["rationale"], sources=[], expected_tests=["fixed native checks"])
        try:
            result = native_evaluate(proposal, output / "native")
        except RuntimeError:
            logs = list((output / "native").rglob("freecad.log"))
            collision = any("defined materials collide" in p.read_text(errors="replace") for p in logs)
            if not collision:
                raise
            result = dict(study_pass=False, checks=dict(native_material_collision=False),
                failed_checks=["native_material_collision"],
                scope="Deterministic geometry rejection; retained CAD/logs require a revised assembly, not an identical retry", **core.FLAGS)
    from . import processes
    processes.attach(value,result,output)
    evidence.label(kind,result)
    result["runtime_sha256"]=envelope.get("runtime_sha256")
    core.write(output / "result.json", result, exclusive=True)
    return result
