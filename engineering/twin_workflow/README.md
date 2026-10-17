# CAD and BIM proposal execution

Use [`tools/automation/twin-completion.py`](../../tools/automation/twin-completion.py)
through `tools/automation/osr-python`. Read the [tool review and operating
instructions](../../docs/design-engine/ai-cad-bim-workflow-2026-10-17.md) for supported
recipes, provider contract, resource budgets and the full completion programme.

The controller accepts data proposals from a configured provider or reviewed JSON
files, reconstructs native CAD/BIM and retains actual failures and feedback. It
does not itself invoke an LLM unless a provider command is configured. The nine
explicit benchmark seeds do not constitute an LLM service.

`init`, `seed`, `submit`, `request`, `run`, `status` and `verify` all require
`--workspace`. Initialisation requires a fresh directory. Repeating `run` resumes
the queue; changed sources require a new baseline and workspace.

An optional provider is an operator-supplied argv array read from JSON. Its stdin
is `osr-twin-agent-request/1`; stdout must be exactly `{"proposals":[...]}` and stderr
is retained separately. This is a trusted command with timeout/output controls,
not a sandbox. No command is accepted from the proposal itself.

Each `osr-twin-proposal/1` contains `id`, `baseline_sha256`, `kind`, `parameters`,
`rationale`, `sources`, `expected_tests` and `schema`, with no extra fields.
`submit` accepts an array; the provider response wraps the array in `proposals`.
Inputs use strict JSON and supported recipes; source citations do not establish
accepted numerical properties. The controller owns test implementation and limits.

`verify --historical` checks retained artifacts without requiring current source
bytes. It does not make historical evidence applicable to a changed design.

The state and work orders deliberately have no engineering-approval or physical
release setter. All 345 allocated source items and 1,219 inherited requests remain
open. Full BOM decomposition, further solver families, target software/HIL,
instrumented correlation and authenticated acceptance ingestion are required
extensions, specified in the completion programme.

Regression checks:

```bash
tools/automation/osr-python -m pytest \
  engineering/analysis/tests/test_twin_completion_workflow.py -q
```
