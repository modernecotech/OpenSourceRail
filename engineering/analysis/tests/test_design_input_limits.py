"""All four engineering input kinds fit; repeated kinds remain invalid."""

import json

from engineering.analysis.tests.test_design_input_revisions import (
    panel_context,
    api,
    proposal_data,
)
from engineering.design_engine.contracts import fingerprint


def test_four_retained_drafts_reach_per_kind_validation_and_five_exceed_the_bound(
    panel_context,
):
    context = panel_context
    retained = []
    # Four differently formatted retained requests carry the same actual facts.
    # They must reach the one-per-kind guard, rather than exceed an old 3-kind cap.
    for indent in range(4):
        code, result = api(
            context,
            "jobs/" + context.parent["id"] + "/qualification-draft",
            dict(
                identity=context.scope,
                candidate=context.candidate["id"],
                contract_sha256=fingerprint(context.contract),
                kind="manufacturing",
                input_json=json.dumps(context.plan, indent=indent),
            ),
        )
        assert code == 200, result
        retained.append(result["draft_sha256"])
    assert len(set(retained)) == 4
    data = proposal_data(context, "four-input-kinds-limit")
    data["drafts"] = retained
    code, result = api(
        context, "jobs/" + context.parent["id"] + "/input-revisions", data
    )
    assert code == 400
    assert "one draft per applicable engineering input kind" in result["error"]
    for values in ([], retained + ["0" * 64]):
        data["drafts"] = values
        code, result = api(
            context, "jobs/" + context.parent["id"] + "/input-revisions", data
        )
        assert code == 400
        assert "one to four distinct retained input drafts" in result["error"]
