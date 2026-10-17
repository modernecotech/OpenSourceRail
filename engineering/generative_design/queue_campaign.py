"""Execute every allocated preliminary study and audit actual release evidence.

The queue concerns full engineering packages. Executing a bounded submodel is
recorded separately from completing that package or issuing a production release.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

from . import campaign, coverage, review
from .coverage import ROOT, local, sha

PARENT = ROOT / "docs/design-engine/generative-campaign"
LANES = ("integration", "civil", "mechanical", "factory", "tooling")
RELEASE_FLAGS = (
    "all_systems_design_complete",
    "manufacturing_release",
    "physical_release",
)


def read(path):
    from .evidence_store import read_json

    return read_json(path)


def source_state(value):
    """Bind all input records, including CAD sources and issue/drawing records."""
    from . import manufacturing, mechanical_systems, civil_systems, factory_systems

    names = set(campaign.sources(value))
    names.update(manufacturing.run()["sources_sha256"])
    names.update(mechanical_systems.context()["source_sha256"])
    names.update(civil_systems.SOURCES.values())
    names.update(
        str(p.relative_to(ROOT))
        for p in (
            factory_systems.EQUIPMENT,
            factory_systems.UTILITIES,
            factory_systems.ROUTES,
            factory_systems.SCHEDULE,
            factory_systems.RETAINED,
            factory_systems.BASIS,
        )
    )
    names.update(str(p.relative_to(ROOT)) for p in PARENT.rglob("*") if p.is_file())
    from .evidence_store import source_closure

    result = {name: sha(local(name)) for name in sorted(names)}
    for name in sorted(names):
        result.update(source_closure(local(name)))
    return dict(sorted(result.items()))


def inherited_civil():
    """Reuse numerical evaluations only with unchanged evaluator dependencies."""
    review.verify_snapshot(PARENT, current=False)
    source = read(PARENT / "snapshot.json")["source_sha256"]
    # The parent finite evaluations are reused, rather than run an identical
    # domain again. New six-car responses are calculated independently below.
    required = [
        "engineering/generative_design/civil.py",
        "engineering/generative_design/data/civil-space.json",
        "engineering/factory_examples/data/basis.json",
        "engineering/design_engine/factory_beam.py",
        "engineering/design_engine/civil_qualification.py",
        "engineering/industrialisation/vehicle-civil-load-trace.json",
    ]
    for name in required:
        if name not in source or sha(local(name)) != source[name]:
            raise ValueError("inherited civil evaluator changed: " + name)
    return read(PARENT / "civil/search.json")


def investigation_counts(item):
    """Count explicitly retained alternatives, never imaginary full designs."""
    for key in ("candidates", "finite_cases", "cases"):
        if isinstance(item.get(key), list):
            return len(item[key])
    if "generated_beam_response_count" in item:
        return item["generated_beam_response_count"]
    if "variants" in item:
        return sum(len(v.get("candidates", [])) for v in item["variants"])
    return 1  # fixed-reference demand/coverage calculation, not a variation


def assemble(value, reports, audit):
    """Exact ID join; preserve mandatory scope and additional discipline gates."""
    expected = {p["id"]: p for p in value["work_packages"]}
    actual, unique = {}, {}
    for lane, report in reports.items():
        for study in report["packages"]:
            identity = study["work_package_id"]
            if identity not in expected or identity in actual:
                raise ValueError("duplicate or unknown queued package: " + identity)
            parent = expected[identity]
            investigations = []
            for item in study["investigations"]:
                validate_selections(item)
                count = investigation_counts(item)
                key = lane + "/" + item["id"]
                content = json.dumps(item, sort_keys=True)
                if key in unique and unique[key][1] != content:
                    raise ValueError(
                        "same investigation ID has different content: " + key
                    )
                unique[key] = (count, content)
                investigations.append(dict(id=key, candidate_count=count))
            if not investigations:
                raise ValueError("queued package lacks an executed investigation")
            links = [f"{lane}/report.json"]
            links.extend(
                f"{lane}/{name}"
                for name in study.get("generated_artifacts", [])
                if name.endswith((".json", ".csv", ".svg", ".html"))
            )
            actual[identity] = dict(
                id=identity,
                title=parent["title"],
                domain=parent["domain"],
                owner_agent_role=parent["owner_agent_role"],
                dependencies=deepcopy(parent["dependencies"]),
                authoritative_sources=deepcopy(parent["authoritative_sources"]),
                required_gates=deepcopy(parent["required_gates"]),
                completion_predicate=deepcopy(parent["completion_predicate"]),
                investigation_summary=investigations,
                artifact_links=list(dict.fromkeys(links)),
                preliminary_investigation_executed=True,
                full_discipline_model_qualified=False,
                unresolved_gates=dict(
                    scope=deepcopy(parent["required_gates"]),
                    discipline=study["unresolved_gates"],
                ),
                manufacturing_evidence=manufacturing_evidence(parent, audit),
                design_complete=False,
                manufacturing_release=False,
                physical_release=False,
            )
    if set(actual) != set(expected):
        raise ValueError(
            "queued package IDs differ from exact scope: "
            + str(sorted(set(expected) - set(actual)))
        )
    return (
        [actual[i] for i in coverage.audit(value)["dependency_order"]],
        len(unique),
        sum(v[0] for v in unique.values()),
    )


def validate_selections(investigation):
    """A local geometric repair cannot silently become the source configuration."""
    selected = set(investigation.get("selected_candidate_ids", []))
    proposed = set(investigation.get("proposed_candidate_ids", []))
    if not selected and not proposed:
        return
    candidates = {c["id"]: c for c in investigation.get("candidates", [])}
    if selected & proposed or (selected | proposed) - set(candidates):
        raise ValueError("selected/proposed candidate identities conflict")
    if any(
        candidates[i].get("existing_configuration_compatible") is False
        for i in selected
    ):
        raise ValueError(
            "source-changing proposal cannot be selected as source-compatible"
        )


def manufacturing_evidence(package, audit):
    from .manufacturing import package_evidence

    return package_evidence(package, audit)


def run(output, *, native=False):
    from . import (
        civil,
        civil_systems,
        factory_systems,
        integration,
        manufacturing,
        mechanical,
        mechanical_systems,
        coupling,
        queue_review,
    )
    from engineering.factory_examples.native import generate

    output = Path(output).resolve()
    if output.exists() or not output.is_relative_to(ROOT / "build"):
        raise ValueError("queue run needs a fresh directory under build/")
    value = campaign.scope()
    parent = inherited_civil()
    source, environment = source_state(value), campaign.environment(native)
    output.mkdir(parents=True)
    campaign.write(output / "scope.json", value)
    campaign.write(output / "inventory-audit.json", coverage.audit(value))
    campaign.write(
        output / "request.json",
        dict(
            schema="osr-queued-studies-request/1",
            source_sha256=source,
            environment=environment,
            native=native,
            parent_snapshot_sha256=sha(PARENT / "snapshot.json"),
            physical_release=False,
        ),
    )
    try:
        integrated = integration.run(civil_report=parent)
        shortlist = integrated["provisional_six_car_beam_shortlist"]
        if not shortlist:
            raise ValueError(
                "no new provisional beam available for downstream demand feedback"
            )
        downstream = deepcopy(parent)
        downstream["selected_candidate_ids"] = [s["candidate_id"] for s in shortlist]
        reaction = max(
            r["maximum_live_reaction_n"]
            for case in integrated["load_envelopes"]["cases"]
            for r in case["responses"].values()
        )
        reports = dict(
            integration=integrated,
            civil=civil_systems.run(
                beam_variables=shortlist[0]["variables"],
                provisional_six_car_support_reaction_n=reaction,
            ),
            mechanical=mechanical_systems.run(),
            factory=factory_systems.run(civil_report=downstream),
        )
        tools = mechanical.search(budget=4096)
        reports["tooling"] = dict(
            packages=[
                dict(
                    work_package_id="FACTORY-TOOLING",
                    investigations=[
                        dict(id="connection-tooling-feedback-domain", **tools)
                    ],
                    generated_artifacts=[],
                    unresolved_gates=[
                        "Connection capacities, GD&T, complete fixture force path, machine configuration and physical first article remain unaccepted"
                    ],
                    engineering_design_complete=False,
                    manufacturing_release=False,
                    physical_release=False,
                )
            ]
        )
        native_models = civil_systems.write_artifacts(
            reports["civil"], output / "civil"
        )
        mechanical_systems.write_artifacts(reports["mechanical"], output / "mechanical")
        factory_systems.write_artifacts(reports["factory"], output / "factory")
        models = mechanical.write_artifacts(tools, output / "tooling/models")
        for model in models:
            native_models.append(
                dict(id="tooling/" + Path(model).parent.name, model=str(model))
            )
        for proposal in shortlist:
            candidate = next(
                c for c in parent["candidates"] if c["id"] == proposal["candidate_id"]
            )
            path = output / "integration/models" / candidate["id"] / "model.json"
            campaign.write(path, civil.native_model(candidate))
            native_models.append(
                dict(id="six-car-planning/" + candidate["id"], model=str(path))
            )
        campaign.write(output / "civil/bed-coupling.json", coupling.search(downstream))
        audit = manufacturing.run()
        manufacturing.write_artifacts(audit, output / "manufacturing")
        campaign.write(output / "manufacturing/audit.json", audit)
        for lane, report in reports.items():
            campaign.write(output / lane / "report.json", report)
            print(
                f'{lane}: {len(report["packages"])} preliminary package studies executed',
                flush=True,
            )
        native_records = []
        for item in native_models:
            model = Path(item["model"])
            record = dict(
                label=item["id"],
                model=model.relative_to(output).as_posix(),
                status="not-requested",
                physical_release=False,
            )
            if native:
                try:
                    proof = generate(model, model.parent, ROOT)
                    record.update(
                        status="passed",
                        part_count=proof["part_count"],
                        receipt=(model.parent / "native-cad.json")
                        .relative_to(output)
                        .as_posix(),
                    )
                except Exception as error:
                    record.update(status="failed", error=str(error))
            native_records.append(record)
            print(f'native {record["label"]}: {record["status"]}', flush=True)
        packages, count, candidates = assemble(value, reports, audit)
        result = dict(
            schema="osr-queued-studies/1",
            packages=packages,
            work_package_count=len(packages),
            unique_investigations=count,
            bounded_candidate_records=candidates,
            counting_boundary="Distinct lane/investigation IDs; fixed-reference audits count as one record; includes inherited tool feedback and newly calculated six-car beam responses, not full components or approved designs.",
            native_geometry=native_records,
            manufacturing_evidence_counts=audit["counts"],
            integration=dict(
                previous_civil_selection_responses=[
                    r
                    for r in integrated["all_beam_responses"]
                    if r["candidate_id"] in parent["selected_candidate_ids"]
                ],
                provisional_six_car_beam_shortlist=shortlist,
                provisional_downstream_maximum_live_reaction_n=reaction,
            ),
            all_systems_design_complete=False,
            manufacturing_release=False,
            physical_release=False,
        )
        campaign.write(output / "report.json", result)
        (output / "index.html").write_text(queue_review.render(result))
        if source_state(value) != source or campaign.environment(native) != environment:
            raise ValueError("queue sources or environment changed during execution")
        campaign.write(
            output / "receipt.json",
            dict(
                schema="osr-queued-studies-receipt/1",
                source_sha256=source,
                environment=environment,
                native=native,
                files_sha256=file_hashes(output),
                physical_release=False,
            ),
        )
        return verify(output)
    except Exception as error:
        campaign.write(
            output / "failure.json",
            dict(
                error=type(error).__name__, message=str(error), physical_release=False
            ),
        )
        raise


def file_hashes(folder, exclude=()):
    return {
        p.relative_to(folder).as_posix(): sha(p)
        for p in sorted(folder.rglob("*"))
        if p.is_file() and p.name not in exclude
    }


def validate_report(value, report):
    expected = {p["id"]: p for p in value["work_packages"]}
    ids = [p["id"] for p in report["packages"]]
    if len(ids) != len(set(ids)) or set(ids) != set(expected):
        raise ValueError("queued report package IDs differ from exact scope")
    for row in report["packages"]:
        parent = expected[row["id"]]
        for key in (
            "required_gates",
            "completion_predicate",
            "dependencies",
            "authoritative_sources",
            "owner_agent_role",
        ):
            if row[key] != parent[key]:
                raise ValueError("queued report changed mandatory scope/gates")
        if row["unresolved_gates"]["scope"] != parent["required_gates"]:
            raise ValueError("queued report erased unresolved scope gates")
        if (
            not row["investigation_summary"]
            or row["full_discipline_model_qualified"] is not False
        ):
            raise ValueError("partial submodels cannot qualify a complete discipline")
        if any(
            row[k] is not False
            for k in ("design_complete", "manufacturing_release", "physical_release")
        ):
            raise ValueError("preliminary study cannot grant release")
    if report["work_package_count"] != len(ids) or any(
        report[k] is not False for k in RELEASE_FLAGS
    ):
        raise ValueError("queued rollup cannot grant release")


def verify(folder, *, current=True, snapshot=False):
    from . import evidence_store

    folder = Path(folder).resolve()
    if evidence_store.is_projection(folder):
        with evidence_store.materialized(folder) as original:
            return verify(original, current=current, snapshot=snapshot)
    seal = "snapshot.json" if snapshot else "receipt.json"
    record = read(folder / seal)
    if record.get("schema") != (
        "osr-queued-studies-snapshot/1" if snapshot else "osr-queued-studies-receipt/1"
    ):
        raise ValueError("controlled queued study seal required")
    files = file_hashes(folder, (seal,))
    if set(files) != set(record["files_sha256"]):
        raise ValueError("queued artifact membership differs")
    if files != record["files_sha256"]:
        raise ValueError("queued artifact changed")
    value, report = read(folder / "scope.json"), read(folder / "report.json")
    validate_report(value, report)
    for lane in LANES:
        for package in read(folder / lane / "report.json")["packages"]:
            for investigation in package["investigations"]:
                validate_selections(investigation)
    if current and source_state(value) != record["source_sha256"]:
        raise ValueError("queued study belongs to another source revision")
    if current:
        coverage.audit(value)
    for package in report["packages"]:
        for name in package["artifact_links"]:
            if not local(name, folder).is_file():
                raise ValueError("queued artifact link missing: " + name)
    for native in report["native_geometry"]:
        if native["status"] == "passed":
            proof = read(local(native["receipt"], folder))
            model = local(native["model"], folder)
            definition = read(model)
            if (
                proof.get("schema") != "osr-factory-native-cad/1"
                or proof.get("physical_release") is not False
                or proof.get("fcstd_reopened") is not True
                or proof.get("step_reopened") is not True
                or proof.get("part_count") != len(definition["parts"])
                or native.get("part_count") != len(definition["parts"])
                or {p["id"] for p in proof.get("parts", [])}
                != {p["id"] for p in definition["parts"]}
            ):
                raise ValueError("queued native proof incomplete")
            if sha(model) != proof["input_sha256"]:
                raise ValueError("queued native input differs")
            for name in (
                ("model.FCStd",) if snapshot else ("model.FCStd", "model.step")
            ):
                if sha(model.parent / name) != proof["files_sha256"][name]:
                    raise ValueError("queued native geometry differs")
    return dict(
        integrity_verified=True,
        current_sources_checked=current,
        work_package_count=len(report["packages"]),
        unique_investigations=report["unique_investigations"],
        bounded_candidate_records=report["bounded_candidate_records"],
        native_geometry_passed=sum(
            r["status"] == "passed" for r in report["native_geometry"]
        ),
        native_geometry_failed=sum(
            r["status"] == "failed" for r in report["native_geometry"]
        ),
        all_systems_design_complete=False,
        manufacturing_release=False,
        physical_release=False,
        numerical_recomputation_performed=False,
    )


def publish(output, destination):
    from . import evidence_store

    output, destination = Path(output).resolve(), Path(destination).resolve()
    verified = verify(output)
    if destination.exists() or not destination.is_relative_to(
        ROOT / "docs/design-engine"
    ):
        raise ValueError(
            "queued publication requires a fresh docs/design-engine directory"
        )
    receipt = read(output / "receipt.json")
    files = {
        name: output / name
        for name in receipt["files_sha256"]
        if Path(name).suffix in {".json", ".html", ".csv", ".svg", ".FCStd"}
    }
    seal = dict(
        schema="osr-queued-studies-snapshot/1",
        source_sha256=receipt["source_sha256"],
        parent_receipt_sha256=sha(output / "receipt.json"),
        parent_verified_at_publication=verified,
        files_sha256={name: sha(path) for name, path in files.items()},
        physical_release=False,
    )
    files["snapshot.json"] = evidence_store.pretty(seal)
    evidence_store.publish_files(files, destination)
    return verify(destination, snapshot=True)
