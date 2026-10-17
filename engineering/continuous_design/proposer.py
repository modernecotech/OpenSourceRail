"""One sequential read-only AI proposer using the existing local CLI login.

No credentials are read/copied by this module. The installed CLI owns its auth.
"""
import json
from pathlib import Path
import subprocess

from engineering.twin_workflow import core


def schema():
    string = {"type": "string"}
    proposal = dict(type="object", properties={k: string for k in ("kind", "parameters_json", "rationale")},
                    required=["kind", "parameters_json", "rationale"], additionalProperties=False)
    need = dict(type="object", properties={k: string for k in ("item_id", "required")},
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
        "Avoid merely renaming or reformatting existing designs.\n" + json.dumps(request, allow_nan=False))
    (output / "prompt.txt").write_text(prompt)
    argv = [executable, "exec", "--sandbox", "read-only", "--ephemeral",
            "-c", 'approval_policy="never"', "--color", "never", "--json",
            "--output-schema", str(output / "schema.json"), "--output-last-message", str(output / "response.json"),
            "-C", str(core.ROOT), "-"]
    if model:
        argv[2:2] = ["--model", model]
    core.write(output / "command.json", argv, exclusive=True)
    # The supervisor owns timeout, output monitoring and descendant cleanup.
    with (output / "prompt.txt").open("rb") as incoming:
        subprocess.run(argv, stdin=incoming, check=True, cwd=core.ROOT)
    response = core.read(output / "response.json")
    return dict(proposal_count=len(response["proposals"]), need_count=len(response["needs"]))
