"""One sequential read-only AI proposer using the existing local CLI login.

No credentials are read/copied by this module. The installed CLI owns its auth.
"""
import json
from pathlib import Path
import subprocess

from engineering.twin_workflow import core
from . import proposals


def schema():
    string = {"type": "string"}
    proposal = dict(type="object", properties={k: string for k in ("kind", "parameters_json", "rationale")},
                    required=["kind", "parameters_json", "rationale"], additionalProperties=False)
    need = dict(type="object", properties=dict(item_id=dict(type="string",minLength=1,maxLength=200, description="Short capability identifier"),
                required=dict(type="string",minLength=12,maxLength=8000, description="Concrete description of the missing work or evidence, not a boolean")),
                required=["item_id", "required"], additionalProperties=False)
    return dict(type="object", properties=dict(proposals=dict(type="array", items=proposal),
                needs=dict(type="array", items=need)), required=["proposals", "needs"], additionalProperties=False)


def run(request, output, executable, model=""):
    output = Path(output)
    core.write(output / "schema.json", schema(), exclusive=True)
    prompt = ("You are the single design proposer for OpenSourceRail's persistent research runner. "
        "Follow the provided typed domains and exact test feedback. Do not spawn other agents. "
        "Do not modify any files, source, tests, limits or engineering acceptance. "
        "Do not send messages, publish, upload, install or control hardware. "
        "Return at most three useful distinct proposals or ten concrete missing-adapter/evidence needs. "
        "Avoid merely renaming or reformatting existing designs. "
        "Read the complete bounded request JSON from: " + str((output / "request.json").resolve()) + "\n")
    proposals.bounded(request)
    if not (output / "request.json").exists():
        core.write(output / "request.json", request, exclusive=True)
    (output / "prompt.txt").write_text(prompt)
    argv = [executable, "exec", "--sandbox", "read-only", "--ephemeral",
            "-c", 'approval_policy="never"', "--color", "never", "--json",
            "--output-schema", str(output / "schema.json"), "--output-last-message", str(output / "response.json"),
            "-C", str(core.ROOT), "-"]
    if model:
        argv[2:2] = ["--model", model]
    core.write(output / "command.json", argv, exclusive=True)
    error = proposals.budget_error(output)
    if error:
        raise ValueError(error + "; no proposer process started")
    # The supervisor owns timeout, output monitoring and descendant cleanup.
    with (output / "prompt.txt").open("rb") as incoming:
        subprocess.run(argv, stdin=incoming, check=True, cwd=core.ROOT)
    response = core.read(output / "response.json",maximum=proposals.MAX_RESPONSE_BYTES)
    return dict(proposal_count=len(response["proposals"]), need_count=len(response["needs"]))
