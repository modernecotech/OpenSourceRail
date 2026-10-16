"""Review actual investigations, source conflicts and remaining evidence needs."""

from __future__ import annotations

from html import escape
import json


def render(report):
    def e(value):
        return escape(str(value), quote=True)

    rows = []
    for package in report["packages"]:
        investigations = "".join(
            f'<li>{e(r["id"])}: {r["candidate_count"]} bounded alternatives</li>'
            for r in package["investigation_summary"]
        )
        artifacts = " · ".join(
            f'<a href="{e(name)}">{e(name.rsplit("/",1)[-1])}</a>'
            for name in package["artifact_links"]
        )
        rows.append(
            f'<tr><td>{e(package["id"])}<br>{e(package["title"])}</td><td>{e(package["owner_agent_role"])}<ul>{investigations}</ul>{artifacts}</td><td><details><summary>Open design and manufacturing requirements</summary><pre>{e(json.dumps(package["unresolved_gates"],indent=2))}</pre></details><p>{len(package["manufacturing_evidence"]["missing_or_unissued_artifact_ids"])} missing/unissued production artifacts</p></td><td>Open<br>Manufacturing release: false</td></tr>'
        )
    initial = report["integration"]["previous_civil_selection_responses"]
    prior = "".join(
        f'<li>{e(c["candidate_id"])}: {c["minimum_sampled_service_compression_pa"]/1e6:.3f} MPa minimum sampled service compression</li>'
        for c in initial
    )
    new = "".join(
        f'<li>{e(c["candidate_id"])}: depth {c["variables"]["depth_m"]:g} m, {c["variables"]["strand_count"]} strands, lift fraction {c["variables"]["lift_fraction"]:g}; minimum {c["minimum_sampled_service_compression_pa"]/1e6:.3f} MPa; bed {c["initial_bed_force_n"]/1e6:.3f} MN; known hook equivalent {c["hook_equivalent_lower_bound_kg"]/1000:.3f} t</li>'
        for c in report["integration"]["provisional_six_car_beam_shortlist"]
    )
    cad = " · ".join(
        f'<a href="{e(r["model"].rsplit("/",1)[0])}/model.FCStd">{e(r["label"])}</a>'
        for r in report["native_geometry"]
        if r["status"] == "passed"
    )
    counts = report["manufacturing_evidence_counts"]
    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Queued civil, mechanical and factory design work</title><style>body{{font:16px/1.5 system-ui,sans-serif;background:#f4f3ed;color:#17313e;margin:0}}main{{max-width:1250px;margin:auto;padding:24px}}.notice{{background:white;border-left:5px solid #ae553f;padding:16px}}.scroll{{overflow-x:auto;background:#fff}}table{{width:100%;border-collapse:collapse}}td,th{{border:1px solid #cbd0cd;padding:10px;text-align:left;vertical-align:top;overflow-wrap:anywhere}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}}a{{color:#12667a}}@media(max-width:650px){{main{{padding:12px}}table{{min-width:750px}}}}</style><main>
<h1>Queued civil, mechanical and factory design work</h1><p class="notice">All {len(report["packages"])} queued packages have received package-specific preliminary investigations. Engineering completion and manufacturing release remain open. No certificate, test result, supplier acceptance or design approval has been invented.</p>
<p>{report["unique_investigations"]} distinct investigations; {report["bounded_candidate_records"]} unique candidate records across their declared domains. Candidate counts measure computational work, not completed components.</p>
<p><a href="report.json">Whole-package report</a> · <a href="manufacturing/audit.json">Production and first-article evidence audit</a> · <a href="manufacturing/production-artifact-requests.csv">Required production artifacts</a> · <a href="manufacturing/inspection-execution-register.csv">Inspection execution register</a> · <a href="manufacturing/supplier-configuration-requests.csv">Unsent supplier configuration requests</a></p>
<h2>Six-car configuration feedback</h2><p>18 explicit provisional cases use the Baghdad planning mass envelopes, assumed bogie geometry, car CG offsets and axle multipliers. Actual supplier axle positions and load combinations remain absent. The earlier three-car-selected proposals fail the larger planning envelope:</p><ul>{prior}</ul>
<p>Further bounded selection finds these local zero-tension alternatives. The small positive margin is a research diagnostic, not a structural reserve or accepted material resistance:</p><ul>{new}</ul><p>Both source architectures remain separate. The 111 m planning train also requires new station-length branches; the 55.5–59.5 m catalogue platforms cannot be adopted for it. Platform/site/egress and route acceptance remain open.</p>
<p><a href="integration/report.json">All load, platform and interface results</a> · <a href="civil/report.json">Civil structures and tooling</a> · <a href="mechanical/report.json">Mechanical systems</a> · <a href="factory/report.json">Factory MEP, equipment, handling and flow</a></p>
<h2>Actual native geometry checks</h2><p>{cad or "No native geometry confirmation requested."}</p><p>Native checks confirm declared primitive geometry and reopened FCStd/STEP at execution. They do not qualify structural resistance, reinforcement, jack-seat/tail force transfer, building/rail grade changes or manufacturing processes. Full STEP and execution logs remain in the sealed local run.</p>
<h2>Source records preventing manufacturing completion</h2><p>The actual trainset register has {counts["missing_or_unissued_production_artifacts"]} missing/unissued production artifacts across {counts["local_production_products"]} locally made products, {counts["actual_inspection_result_records"]} actual inspection results out of {counts["inspection_characteristics"]} planned characteristics, and {counts["issued_drawing_references"]} issued references in {counts["drawing_definitions"]} drawing definitions. Supplier configurations for {counts["supplier_configuration_products"]} further products remain proposals.</p>
<p>Generated cut/drill schedules and drawings are preliminary definitions. Existing issued-artifact and physical inspection records retain their actual source state. Unknown input and qualification gates remain mandatory.</p>
<h2>All queued packages</h2><div class="scroll"><table><thead><tr><th>Package</th><th>Executed investigations and artifacts</th><th>Remaining requirements</th><th>Completion</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div><p>Supplier enquiries are prepared and unsent. British manufacture remains the priority; an exact offered configuration and Baghdad support require supplier evidence. No background or unbounded agent loop is running.</p></main></html>"""
