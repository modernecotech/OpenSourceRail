"""Portable review projection; full native FEM evidence remains in sealed jobs."""

from __future__ import annotations

from html import escape
import json
from pathlib import Path

from .coverage import sha, local, ROOT, audit, validate_ledger


def page(summary, closure, lanes, coupled):
    def e(value):
        return escape(str(value), quote=True)

    sections = []
    for name, report in lanes.items():
        selected = [
            r
            for r in report["candidates"]
            if r["id"] in report["selected_candidate_ids"]
        ]
        rows = []
        for row in selected:
            models = [
                r
                for r in summary["native_geometry"]
                if r["lane"] == name
                and row["id"] in r["model"]
                and r["status"] == "passed"
            ]
            links = " · ".join(
                f'<a href="{e(Path(r["model"]).parent.as_posix())}/model.FCStd">{e(Path(r["model"]).parent.name)} CAD</a>'
                for r in models
            )
            rows.append(
                f'<tr><td>{e(row["id"])}<br>{links}</td><td><pre>{e(json.dumps(row["variables"],indent=2))}</pre></td><td><pre>{e(json.dumps(row["metrics"],indent=2))}</pre></td></tr>'
            )
        sections.append(
            f'<h2>{name.capitalize()} agent lane</h2><p>{len(report["candidates"])} evaluations; {len(report["selected_candidate_ids"])} selected local research alternatives. Stop: {e(report["termination"])}. These selections do not establish complete manufacturable designs.</p><p><a href="{name}/search.json">All candidates, failed checks, ancestry and unknowns</a></p><div class="scroll"><table><thead><tr><th>Candidate</th><th>Variables [SI]</th><th>Metrics [SI; see field units]</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
        )
    common_rows = "".join(
        f'<tr><td>{e(problem)}</td><td>{e(r["status"])}</td><td>{r["candidate_count"]}</td><td>{e(r["recursive_termination"] or "one-coordinate screening")}</td><td>{e(r["native_domain_complete"])}</td><td><a href="common/{e(problem)}/{"comparison.json" if r["comparison_sha256"] else "evidence.json"}">All results</a></td></tr>'
        for problem, r in summary["common"].items()
    )
    package_rows = "".join(
        f'<tr><td>{e(r["id"])}<br>{e(r["title"])}</td><td>{e(r["owner_agent_role"])}</td><td>{e(r["exploration"])}</td><td><details><summary>Required closure</summary><pre>{e(json.dumps(r["required_gates"],indent=2))}</pre></details></td><td>Open</td></tr>'
        for r in closure["work_packages"]
    )
    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Baghdad multi-agent generative design campaign</title><style>
body{{font:16px/1.5 system-ui,sans-serif;margin:0;background:#f4f3ed;color:#192b36}}main{{max-width:1250px;margin:auto;padding:24px}}h1,h2{{line-height:1.2}}a{{color:#126077}}.notice{{padding:16px;border-left:5px solid #a24b35;background:#fff}}.scroll{{overflow-x:auto;background:white}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #c7cdc9;padding:10px;text-align:left;vertical-align:top}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px;margin:0}}td{{overflow-wrap:anywhere}}@media(max-width:600px){{main{{padding:12px}}table{{min-width:660px}}}} </style><main>
<h1>Baghdad multi-agent generative design campaign</h1><p class="notice">Unissued research. {summary["work_package_count"]} work packages tracked; 0 complete engineering/manufacturing releases. Architecture reconciliation, accepted loading/materials, detailed manufacturing and physical qualification remain open. An agent search pass is a local research result.</p>
<p>Roles: civil variations, mechanical variations, system scope and integration/critique. The deterministic runner executes controlled evaluators; it does not simulate an approval authority or invent additional AI agents.</p>
<p><a href="scope.json">Scope and agent tasks</a> · <a href="inventory-audit.json">Exact source-ID coverage</a> · <a href="closure-ledger.json">All closure gates</a> · <a href="work-queue.json">Remaining agent tasks</a> · <a href="summary.json">Campaign summary</a></p>
<p>Keep LM3 three-car catalogue identities and metro-six-car research examples distinct. No railway load, component suitability or release is transferred between them.</p>
{"".join(sections)}
<h2>Coupled stressing-bed feedback</h2><p>{len(coupled["candidates"])} axial rail sensitivities propagate new beam prestressing forces into 16/20/25 mm wall and three hypothetical spring-stiffness cases. Existing strongbacks, moulds, foundations and crane systems acquire no capacity credit. Gross elastic stability does not qualify local resistance, staged eccentric loading or measured support stiffness.</p><p><a href="bed-coupling.json">All coupled demand results</a></p>
<h2>Existing common design jobs</h2><p>Finite native domains refer only to the two small generated-part charters. Other rows are bounded screening variations or a single fixed reference, with failed and unknown checks retained. Full native meshes, decks and logs remain in sealed local parent jobs; this page is a compact review projection.</p><div class="scroll"><table><thead><tr><th>Problem</th><th>Job</th><th>Candidates</th><th>Termination</th><th>Native finite domain complete</th><th>Evidence</th></tr></thead><tbody>{common_rows}</tbody></table></div>
<h2>Whole-scope manufacturing closure</h2><p>Every inventory item is assigned. A representative part search does not establish coverage of every component in its parent package. Missing adapters and mandatory evidence remain visible in the ledger and work queue.</p><div class="scroll"><table><thead><tr><th>Work package</th><th>Agent role</th><th>Exploration coverage</th><th>Design/manufacturing gates</th><th>Release</th></tr></thead><tbody>{package_rows}</tbody></table></div>
<p>British manufacture has priority; UK integration and imported machine origins remain separately identified. Supplier enquiries remain unsent.</p></main></html>"""


def publish(output, destination):
    from .campaign import verify
    from . import evidence_store

    output, destination = Path(output).resolve(), Path(destination).resolve()
    verified = verify(output)
    if destination.exists() or not destination.is_relative_to(
        ROOT / "docs/design-engine"
    ):
        raise ValueError(
            "review projection requires a fresh docs/design-engine directory"
        )
    record = json.loads((output / "receipt.json").read_text())
    files = {
        name: output / name
        for name in record["files_sha256"]
        if Path(name).suffix in {".json", ".html", ".FCStd"}
    }
    seal = dict(
        schema="osr-generative-campaign-snapshot/1",
        parent_receipt_sha256=sha(output / "receipt.json"),
        parent_verified_at_publication=verified,
        source_sha256=record["source_sha256"],
        files_sha256={name: sha(path) for name, path in files.items()},
        all_systems_design_complete=False,
        physical_release=False,
        scope="Source-bound research projection; original evidence is losslessly archived in the shared content-addressed store. FCStd retained locally; STEP and full common native logs remain in sealed parent jobs. No numerical recomputation by snapshot verification.",
    )
    files["snapshot.json"] = evidence_store.pretty(seal)
    evidence_store.publish_files(files, destination)
    return verify_snapshot(destination)


def verify_snapshot(destination, *, current=True):
    from .campaign import sources

    from . import evidence_store

    destination = Path(destination).resolve()
    if evidence_store.is_projection(destination):
        with evidence_store.materialized(destination) as original:
            return verify_snapshot(original, current=current)
    record = json.loads((destination / "snapshot.json").read_text())
    if (
        record.get("schema") != "osr-generative-campaign-snapshot/1"
        or record.get("physical_release") is not False
        or record.get("all_systems_design_complete") is not False
    ):
        raise ValueError("unreleased generative review required")
    actual = {
        p.relative_to(destination).as_posix()
        for p in destination.rglob("*")
        if p.is_file() and p != destination / "snapshot.json"
    }
    if actual != set(record["files_sha256"]):
        raise ValueError("generative snapshot artifact membership differs")
    for name, digest in record["files_sha256"].items():
        if sha(local(name, destination)) != digest:
            raise ValueError("generative snapshot artifact changed: " + name)
    if (
        current
        and sources(json.loads((destination / "scope.json").read_text()))
        != record["source_sha256"]
    ):
        raise ValueError("generative snapshot belongs to another source revision")
    summary = json.loads((destination / "summary.json").read_text())
    closure = json.loads((destination / "closure-ledger.json").read_text())
    value = json.loads((destination / "scope.json").read_text())
    if current:
        audit(value)
    validate_ledger(value, closure)
    if any(
        summary[k] is not False
        for k in (
            "all_systems_design_complete",
            "manufacturing_release",
            "physical_release",
        )
    ) or any(
        p["design_complete"] or p["physical_release"] or p["manufacturing_release"]
        for p in closure["work_packages"]
    ):
        raise ValueError(
            "snapshot cannot promote research into design/manufacturing release"
        )
    for native in summary["native_geometry"]:
        if native["status"] == "passed":
            proof = json.loads((destination / native["receipt"]).read_text())
            model = destination / native["model"]
            if (
                sha(model) != proof["input_sha256"]
                or sha(model.parent / "model.FCStd")
                != proof["files_sha256"]["model.FCStd"]
            ):
                raise ValueError("snapshot native correspondence differs")
    return dict(
        integrity_verified=True,
        current_sources_checked=current,
        numerical_recomputation_performed=False,
        all_systems_design_complete=False,
        physical_release=False,
    )
