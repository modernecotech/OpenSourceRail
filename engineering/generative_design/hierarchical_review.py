"""Static review of exact hierarchy, adverse integration and worker evidence.

Rendering grants no adoption or engineering authority. Counters come from the
supplied report; missing checks and incomplete capabilities remain visible.
"""

from hashlib import sha256
from html import escape
import json
from pathlib import PurePosixPath
from urllib.parse import quote


def _text(value):
    return escape(str(value))


def _json(value):
    return "<pre>" + _text(json.dumps(value, indent=2, allow_nan=False)) + "</pre>"


def _anchor(prefix, identity):
    return prefix + "-" + sha256(str(identity).encode()).hexdigest()[:16]


def _path(value):
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("safe relative review artifact path required")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or any(p in {".", ".."} for p in value.split("/"))
        or ":" in value
    ):
        raise ValueError("safe relative review artifact path required")
    return quote(path.as_posix(), safe="/")


def _link(path, label):
    return '<a href="' + _path(path) + '">' + _text(label) + "</a>"


def _details(title, value):
    return (
        "<details><summary>" + _text(title) + "</summary>" + _json(value) + "</details>"
    )


def _checks(rows):
    return (
        '<ul class="checks">'
        + "".join(
            '<li data-state="'
            + _text(row.get("state", "unknown"))
            + '"><strong>'
            + _text(row.get("state", "unknown"))
            + "</strong> "
            + _text(row.get("id", "unnamed check"))
            + _details("Check evidence", row)
            + "</li>"
            for row in rows
        )
        + "</ul>"
    )


def _changes(candidate, baseline):
    current, previous = candidate.get("variables", {}), baseline.get("variables", {})
    rows = [
        dict(variable=key, previous=previous.get(key), proposed=current.get(key))
        for key in sorted(set(current) | set(previous))
        if current.get(key) != previous.get(key)
    ]
    return _details(
        "Changed design variables",
        rows or "No variable change against the displayed comparison",
    )


def render(report, execution=None, *, artifact_prefix="execution/"):
    """Return responsive HTML beside report.json and optional execution artifacts.

    ``execution`` is the actual bounded executor report, copied under
    ``artifact_prefix`` with its recorded artifact_directory layout. No absolute
    workspace paths, external scripts or injected report markup are followed.
    """
    if report.get("schema") != "osr-hierarchical-pilot/1":
        raise ValueError("hierarchical pilot report required")
    if any(
        report.get(flag) is not False
        for flag in (
            "engineering_design_complete",
            "manufacturing_release",
            "physical_release",
        )
    ):
        raise ValueError("unreleased hierarchical research report required")
    plan = report["plan"]
    items, requests = plan["items"], plan["missing_capabilities"]
    engineering = report["engineering"]
    if execution is None and isinstance(report.get("software_execution"), dict):
        execution = report["software_execution"]
    if (
        execution is not None
        and execution.get("schema") != "osr-bounded-agent-execution/1"
    ):
        raise ValueError("bounded execution report required")
    _path(artifact_prefix.rstrip("/"))
    prefix = artifact_prefix.rstrip("/") + "/"
    promotions = {row["candidate_id"]: row for row in report.get("promotions", [])}
    adverse = engineering.get("adverse_cases", [])
    cases = {row.get("parent_candidate_id"): row for row in adverse}
    headings = [
        ("<span>" + str(len(items)) + "</span>", "controlled hierarchy items"),
        (
            "<span>"
            + str(sum(row["kind"] == "work-package" for row in items))
            + "</span>",
            "work packages mapped",
        ),
        ("<span>" + str(len(requests)) + "</span>", "missing capability requests"),
        (
            "<span>" + str(len((execution or {}).get("results", []))) + "</span>",
            "actual isolated worker evaluations",
        ),
    ]
    body = "<header><p>OpenSourceRail · experimental design review</p><h1>Hierarchical design pilot</h1><p>Changes, evidence, affected parents and the next controlled action.</p></header><main>"
    body += '<aside class="notice">Experimental computational work only. Engineering design completion, manufacturing release and physical release remain false. Deterministic worker roles do not establish an LLM service invocation or appointed independent engineering acceptance.</aside>'
    body += '<nav aria-label="Review sections"><a href="#candidates">Candidates</a><a href="#integration">Parent integration</a><a href="#workers">Worker execution</a><a href="#hierarchy">Hierarchy</a><a href="#requests">Missing capabilities</a></nav>'
    body += (
        '<section class="metrics" aria-label="Report counts">'
        + "".join(
            "<div>" + value + _text(label) + "</div>" for value, label in headings
        )
        + "</section>"
    )
    body += (
        "<p>"
        + _link("report.json", "Complete numerical report")
        + ' · All counts and decisions below come from that report.</p><h2 id="candidates">Candidate changes and decisions</h2>'
    )
    for discipline in ("mechanical", "civil"):
        records = engineering.get(discipline, {})
        baseline = records.get("ordinary", records.get("adverse", {}))
        for label, candidate in records.items():
            if not isinstance(candidate, dict) or "id" not in candidate:
                continue
            parent = (
                "vehicle-assembly"
                if discipline == "mechanical"
                else "complete-viaduct-bay"
            )
            decision = promotions.get(candidate["id"], cases.get(candidate["id"], {}))
            disposition = decision.get("disposition", "HOLD")
            failed = [
                row["id"]
                for row in candidate.get("checks", [])
                if row.get("state") == "fail"
            ]
            unknown = [
                row["id"]
                for row in candidate.get("checks", [])
                if row.get("state") == "unknown"
            ]
            body += (
                '<article class="candidate" data-disposition="'
                + _text(disposition)
                + '"><h3>'
                + _text(discipline + " / " + label)
                + '</h3><p class="identity">'
                + _text(candidate["id"])
                + "</p><p><strong>"
                + _text(disposition)
                + '</strong> · Affected parent: <a href="#'
                + _anchor("item", parent)
                + '">'
                + _text(parent)
                + "</a></p>"
            )
            body += (
                "<p>"
                + str(len(failed))
                + " known failed checks; "
                + str(len(unknown))
                + " unknown checks. A local pass does not establish parent integration.</p>"
            )
            body += _changes(candidate, baseline)
            body += _details(
                "Objectives and declared units", candidate.get("objectives", {})
            )
            body += _details(
                "Adoption decision evidence",
                decision
                or dict(
                    disposition="HOLD",
                    reasons=["No complete controlled promotion evidence supplied"],
                ),
            )
            body += (
                "<p>Next action: "
                + _text(
                    "; ".join(decision.get("reasons", []))
                    or (
                        "Resolve known failed checks and retain independent parent evaluation"
                        if failed
                        else "Obtain missing capability and accepted input evidence before promotion"
                    )
                )
                + ".</p>"
            )
            body += (
                "<details><summary>All candidate checks, including unknowns</summary>"
                + _checks(candidate.get("checks", []))
                + "</details><p>"
                + _link("report.json", "Exact report evidence")
                + " <code>"
                + _text("/engineering/" + discipline + "/" + label)
                + "</code></p></article>"
            )
    body += '<h2 id="integration">Parent integration and coupled iterations</h2>'
    for row in adverse:
        body += (
            '<article class="adverse"><h3>'
            + _text(row["id"])
            + "</h3><p><strong>"
            + _text(row.get("disposition", "HOLD"))
            + "</strong> · Local checks passing: "
            + _text(row.get("locally_passing", "unknown"))
            + "</p>"
            + _details("Actual local and parent evidence", row)
            + "</article>"
        )
    bay = engineering.get("complete_bay", {})
    body += (
        '<article id="bay"><h3>Complete viaduct bay</h3><p><strong>'
        + _text(bay.get("disposition", "HOLD"))
        + "</strong> · Complete bay evaluator executed: "
        + _text(bay.get("complete_bay_evaluator_executed", False))
        + "</p>"
        + _details("Both declared support records and missing analyses", bay)
        + "</article>"
    )
    coupling = engineering.get("coupling", {})
    body += (
        '<article id="coupling"><h3>Bounded coupled evaluation</h3><p>'
        + _text(coupling.get("status", "not executed"))
        + " · "
        + str(len(coupling.get("trace", [])))
        + " recorded iterations</p><p>"
        + _text(coupling.get("scope", "Coupled physical scope not supplied"))
        + "</p>"
        + _details("Interface states, residuals and checks", coupling)
        + "</article>"
    )
    body += '<h2 id="workers">Isolated worker execution</h2>'
    if execution is None:
        body += (
            "<p>Not executed in this report. "
            + _text(report.get("software_execution", "No executor evidence supplied"))
            + "</p>"
        )
    else:
        body += (
            "<p>Declared concurrency: "
            + _text(execution.get("concurrency"))
            + ". Tool results are execution evidence; promotion requires a separate controlled decision.</p>"
        )
        for row in execution.get("results", []):
            _path(row["artifact_directory"])
            directory = prefix + row["artifact_directory"]
            body += (
                '<article class="worker"><h3>'
                + _text(row["proposal_id"])
                + "</h3><p><strong>"
                + _text(row["status"])
                + "</strong> · Role: "
                + _text(row["role"])
                + "</p><p>Base revision: <code>"
                + _text(row["base_commit"])
                + "</code></p><p>"
                + _link(directory + "/candidate.patch", "Proposed patch")
                + " · "
                + _link(directory + "/evaluation.json", "Recorded evaluation")
                + "</p>"
                + _details("Changed paths", row.get("changed_paths", []))
            )
            for tool in row.get("tools", []):
                body += (
                    "<p><strong>"
                    + _text(tool["state"])
                    + "</strong> "
                    + _link(directory + "/" + tool["log"], "Actual tool log")
                    + "</p>"
                    + _details("Recorded command and limits", tool)
                )
            body += (
                _details("Execution error", row.get("error"))
                + "<p>Next action: inspect the immutable logs and evaluate independent and affected parent checks under the controller policy.</p></article>"
            )
    body += '<h2 id="promotion">Controlled promotion decisions</h2>'
    if not promotions:
        body += "<p>HOLD: no controlled promotion decisions supplied. Passing tool execution alone does not adopt a revision.</p>"
    for identity, decision in promotions.items():
        body += (
            '<article class="promotion"><h3>'
            + _text(identity)
            + "</h3><p><strong>"
            + _text(decision["disposition"])
            + "</strong> · Baseline: "
            + _text(decision.get("baseline_id", "unspecified"))
            + "</p>"
            + _details("Actual reasons and experimental revision ancestry", decision)
            + "<p>Next action: "
            + _text(
                "; ".join(decision.get("reasons", []))
                or "Retain the experimental ancestry and evidence; keep physical qualification gates open"
            )
            + ".</p></article>"
        )
    body += '<h2 id="hierarchy">Controlled items and affected parents</h2><p>Every item retains its evaluator scope or a named missing capability request. Mapping an item does not complete it.</p>'
    for row in items:
        body += (
            '<details class="item" id="'
            + _anchor("item", row["id"])
            + '"><summary>'
            + _text(row["id"] + " · " + row["kind"])
            + "</summary><p>"
            + _text(row.get("function", ""))
            + "</p><p>Affected parents: "
            + (
                ", ".join(
                    '<a href="#'
                    + _anchor("item", parent)
                    + '">'
                    + _text(parent)
                    + "</a>"
                    for parent in row["parents"]
                )
                or "System root"
            )
            + "</p>"
            + _details("Requirements, scenarios and evaluator scope", row)
            + "<p>Missing capabilities: "
            + ", ".join(
                '<a href="#'
                + _anchor("request", identity)
                + '">'
                + _text(identity)
                + "</a>"
                for identity in row.get("missing_capability_ids", [])
            )
            + "</p></details>"
        )
    body += '<h2 id="requests">Precise missing capability requests</h2>'
    for row in requests:
        body += (
            '<details class="request" id="'
            + _anchor("request", row["id"])
            + '"><summary>'
            + _text(row.get("state", "HOLD") + " · " + row["item_id"])
            + "</summary><h3>"
            + _text(row["capability"])
            + "</h3>"
            + _details("Missing inputs, scenarios and acceptance demonstration", row)
            + "<p>Next action: obtain the named inputs and independently benchmark the capability before ordinary use.</p></details>"
        )
    body += "<footer><p>Source records and adverse outcomes remain visible. Experimental adoption is separate from engineering, construction and operational release.</p></footer></main>"
    css = """*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f5f5f0;color:#18352e;font:16px/1.55 system-ui,sans-serif}header,main{max-width:1120px;margin:auto;padding:28px}header{padding-top:48px}h1{font-size:clamp(2rem,5vw,3.5rem);line-height:1.1;margin:8px 0 16px}h2{margin-top:42px}h3{margin:4px 0 12px}a{color:#086552;text-underline-offset:3px}p,li,summary,.identity,code{overflow-wrap:anywhere}nav{display:flex;flex-wrap:wrap;gap:12px 22px;margin:24px 0}.notice{border-left:5px solid #986b17;background:#fff4cf;padding:18px}.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:28px 0}.metrics div{padding:18px;background:#dce8df;border-radius:8px}.metrics span{display:block;font-size:2rem;font-weight:700}.candidate,.adverse,#bay,#coupling,.worker,.promotion{padding:22px;margin:16px 0;background:#fff;border:1px solid #cad7cd;border-radius:10px;min-width:0}details{min-width:0;margin:12px 0}summary{cursor:pointer;font-weight:650}details[open]>summary{margin-bottom:12px}pre{white-space:pre-wrap;overflow-wrap:anywhere;padding:14px;background:#edf2ee;border-radius:6px;font-size:13px;max-width:100%}.item,.request{padding:14px;background:#fff;border-bottom:1px solid #d9dfd8}.checks{padding-left:20px}.checks li{padding:8px;border-bottom:1px solid #ddd}.checks li[data-state=fail]{border-left:4px solid #ad4234}.checks li[data-state=unknown]{border-left:4px solid #b28c2c}footer{margin-top:36px;border-top:1px solid #cad7cd;padding-top:20px}@media(max-width:650px){header,main{padding:18px}.metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.metrics div{padding:12px}.candidate,.adverse,#bay,#coupling,.worker,.promotion{padding:15px}pre{padding:10px}}"""
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Hierarchical design pilot · OpenSourceRail</title><style>'
        + css
        + "</style></head><body>"
        + body
        + "</body></html>\n"
    )
