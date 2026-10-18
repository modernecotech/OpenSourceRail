# Continuous mechanical civil software and integration runner

17 October 2026. OpenSourceRail now has a persistent runner for the
[CAD and BIM proposal workflow](ai-cad-bim-workflow-2026-10-17.md). It evaluates
distinct designs, turns numerical failures into new candidates, requests typed
AI proposals and recalculates affected integrations. The service stays alive
after this conversation, retains its queue and resumes after interruptions.

The initial programme has **27 distinct seeds across four lanes**. Failure-directed
repairs and useful AI proposals extend that queue. This is a computational
research programme: missing manufacturing, site, supplier, target-software and
physical acceptance evidence remains open.

Updated 18 October: the scheduler now explores compatible passing children,
repairs actual coupled civil failures and tests material-saving neighbors of
passing detail designs. Lifetime task caps have been replaced with a rolling
queue. Historical recipes nominate fresh evaluations after source changes.

## What each lane executes

| Lane | Work and actual checks | Retained boundary |
| --- | --- | --- |
| Mechanical | Configuration-specific connected underframe/bolster calculations for LM3 and the six-car planning context; feedback repairs; native cleat alternatives; interface assemblies with coordinated sill/carrier and fastener-grip changes | Full vehicle inventory, fatigue/contact/weld qualification, configured supplier geometry and manufacturing release remain open |
| Civil | Four vehicle/span detail contexts with failure-directed reinforcement/support/footing alternatives; native RHS/I-section models; 20/25 m CAD and IFC research bays with schema checks | Site/ground data, complete reinforcement and anchorage, qualified resistance and construction acceptance remain open |
| Software | Generate executable Boolean precharge guard policies within a fixed latch/replay wrapper; test all **4,096 Boolean combinations** and **20 temporal cases**, including a healthy voltage ramp | These are generated policy functions, not full train software, installed hardware, real-time qualification or HIL |
| Integration | Audit the current federated reference; combine exact mechanical/civil/software receipts; propagate mechanical gross mass into configuration-matched civil axle forces and recalculate the civil candidate | One-way static sensitivity with no removal credit; rejected children stay diagnostic, and no physical or dynamic system acceptance is inferred |

Every result remains tied to source hashes, task parameters, exact child revisions
and actual artifact bytes. A successful process can still produce a rejected
design. Research rejections do not become worker errors or trigger identical
retries. Unexpected execution failures receive at most two retained attempts.

The native trial caught a real interface problem: increasing sill flange thickness
without moving the nut embedded the nut in the flange. The recipe now updates
nut position and shank grip with the sill wall and regenerates mass properties.
Native geometry checks remain responsible for rejecting collisions. Threads,
preload, contact and supplier acceptance are still unresolved.

## Installed service and live records

Service: `osr-continuous-design.service`, managed by the existing user systemd
instance. It is enabled for future user-manager starts. This machine already has
user lingering enabled, so the service can survive logout. Service restart does
not depend on keeping the chat or its terminal session open.

The workspace is `/home/hayder/.local/state/opensourcerail/continuous-design`:

| Record | Purpose |
| --- | --- |
| `config.json` | Live resource and proposer settings |
| `status.json` | Atomic heartbeat, active worker identities and resource state |
| `queue.sqlite` | Durable tasks, states, events, proposer attempts and open needs |
| `active.json` | Exact active source baseline and epoch |
| `epochs/<baseline>/baseline.json` | Engineering/controller source digests |
| `epochs/<baseline>/historical-inputs.json` | Verified prior input nominations; no old result/acceptance transfer |
| `epochs/<baseline>/work-orders/` | Inherited 63 work packages, 345 source allocations and 1,219 open baseline requests |
| `epochs/<baseline>/attempts/<design>/<attempt>/` | Task, generated model/code, solver/check records, logs, result and sealed receipt |
| `epochs/<baseline>/provider/` | AI requests, command/schema, raw events and responses |

Inspect progress:

```bash
tools/automation/osr-python tools/automation/design-continuous.py status
tools/automation/osr-python tools/automation/design-continuous.py verify
systemctl --user status osr-continuous-design.service
journalctl --user -u osr-continuous-design.service -f
```

`status` reports evaluated work through each lane's `completed` count. That count
includes retained rejections; it does not mean completed railway specifications.
`verify` checks finished attempts while running attempts continue to change. Use
`verify --historical` only for retained integrity after source changes.

## Continuous operation and limits

The service runs up to **three concurrent processes**, with at most one numerical
worker per lane and one AI proposer at a time. It reserves a slot when a useful
AI request is due, so a replenished numerical queue cannot starve the proposer.
The four lanes receive turns as capacity becomes available.

Default limits are **8 GiB of workspace output**, **10 GiB free disk reserve**,
**512 MiB per numerical attempt**, a **15-minute numerical timeout**, and a
**5-minute proposer timeout**. The systemd unit applies a 250% CPU quota, lower
scheduling priority, a 6 GiB memory high watermark and an 8 GiB maximum.
These values control resource use; they do not change engineering acceptance.

For this installed run, the proposer interval is two minutes and its timeout is
15 minutes to accommodate the existing high reasoning setting. The eight-call
hourly cap remains in place; numerical workers keep their 15-minute timeout.

The AI proposer has a maximum of **eight service calls per hour** and at least
ten minutes between calls for the same lane. Unchanged successful or no-progress
requests are not repeated. Transient errors can retry the same context at most
three times with a 30-minute backoff. The numerical programme continues when
the AI provider is unavailable. A disk limit leaves the service waiting for
capacity, preserving evidence instead of deleting it.

There is no lifetime candidate-count cap. Each lane has up to **64 queued or
running tasks**. Additional distinct recipes remain durable `deferred` records;
they enter the live queue as capacity becomes available. Status reports both
states. The workspace output limit still bounds retained data, and a saturated
lane does not consume new AI proposal calls. Reaching a resource or finite-domain
boundary leaves the supervisor watching for new evidence and restored capacity;
it does not mark engineering complete.

Automatic integration dispatch admits up to eight new triples per frontier
update, using mechanical, civil and software children that pass their implemented
checks and match the train configuration. It covers civil span contexts before
deepening an individual context. Manual diagnostic rejected-child combinations
remain permitted and retain their failed predicates. Coupled civil failures
produce geometry repairs against the original context, followed by new exact
child coupling checks. Fixed loads and screening limits remain unchanged.

Passing mechanical/civil detail candidates also produce one-coordinate
material-saving trials within the registered domains. These trials can fail;
their full checks are re-evaluated and retained. The existing LM3 analytical
stiffness bound proves incompatibility only for its declared constant-EI family
and unaccepted research target. That family records a need for a different load
path/envelope adapter instead of endlessly sampling unchanged hypotheses.

Edit `config.json` with valid JSON and replace it atomically; settings reload on
the next polling cycle. Stop/start controls are:

```bash
systemctl --user stop osr-continuous-design.service
systemctl --user start osr-continuous-design.service
systemctl --user restart osr-continuous-design.service
```

On restart, interrupted attempts remain available. Eligible tasks return to the
queue and receive a new attempt directory. Completed attempts retain their results
and are not repeated. A source edit suspends dispatch; after the change is
committed, the supervisor restarts into a fresh baseline and Python process.
Verified historical passing recipes and the closest failed detail recipes can
nominate inputs in the new epoch. Those jobs start without result receipts and
must rebuild/re-evaluate. Historical integration jobs are excluded because their
child keys belong to the old baseline.

## AI proposal interface

The runner uses the installed Codex CLI's saved login. It does not copy tokens,
edit global model settings or configure an API key. The proposer operates with
`read-only`, `--ephemeral` and structured JSON output. These mechanisms are
documented in [official OpenAI documentation](https://developers.openai.com/codex/noninteractive).
The single proposer is instructed to avoid edits, deployment, messages, uploads,
hardware control and spawning other agents.

The installed CLI initially rejected the inherited `gpt-6.1-sol` model for the
local account. Its live model catalogue listed `gpt-5.6-sol`; this workspace's
`provider_model` selects that model explicitly while leaving the global setting
unchanged. Model availability depends on the account/client rollout; the
[official model guidance](https://developers.openai.com/codex/models/) also retains
the 5.6 models during rollout. Actual proposer errors and responses stay in the
local records rather than being counted as successful AI design work.

Responses contain up to three proposals and ten concrete missing-model/evidence
needs. Parameters are data within registered domains; no arbitrary code or altered
test thresholds is accepted. Software permits only Boolean names/operators from
the fixed fact interface. Equivalent software truth tables deduplicate even if
their expression text differs.

The proposer receives actual failed predicates and check details, existing designs,
relevant work-package requirements and available child identities. The child
catalogue balances kinds/contexts and prioritizes passing children, so a useful
older frame is not hidden by a stream of recent failures. Its entries identify
configuration, study state and exact receipt. A study pass concerns implemented
offline checks; the false physical/manufacturing release flags remain independent.
Integration proposals must use
completed mechanical/civil/software children from the same baseline and train
configuration. Missing capabilities are recorded as open needs. This interface
does not automatically develop or merge new solver families into the controller.

An operator can add reviewed tasks while the service runs:

```bash
tools/automation/osr-python tools/automation/design-continuous.py submit \
  --tasks /absolute/path/tasks.json
```

Each task has `kind`, `parameters`, `rationale` and `parent` (a design digest or
`null`). The [implementation guide](../../engineering/continuous_design/README.md)
links the controller and tests. `submit` expects a JSON array, capped at 32 tasks.

The [full completion programme](ai-cad-bim-workflow-2026-10-17.md#expanding-the-adapters-to-complete-the-railway)
still governs progress beyond these adapters. Continuous execution cannot replace
an exhaustive installed BOM, dimensioned manufacturing packs, calibrated physical
tests, complete executable train software or accountable engineering acceptance.
