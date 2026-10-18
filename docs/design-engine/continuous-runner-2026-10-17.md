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

The follow-up review is implemented in the same runner: transactional follow-up
dispatch, persisted AI fairness, bounded prompts, an explicit verification ladder,
native/numerical promotion, a Pareto archive, runtime identity and an isolated
capability workflow. The first registered extension is a generated packet-receiver
state machine with independent reference tests. Full railway completion remains
subject to the open work packages and acceptance programme.

## What each lane executes

| Lane | Work and actual checks | Retained boundary |
| --- | --- | --- |
| Mechanical | Configuration-specific connected underframe/bolster calculations for LM3 and the six-car planning context; feedback repairs; native cleat alternatives; interface assemblies with coordinated sill/carrier and fastener-grip changes | Full vehicle inventory, fatigue/contact/weld qualification, configured supplier geometry and manufacturing release remain open |
| Civil | Four vehicle/span detail contexts with failure-directed reinforcement/support/footing alternatives; native RHS/I-section models; 20/25 m CAD and IFC research bays with schema checks | Site/ground data, complete reinforcement and anchorage, qualified resistance and construction acceptance remain open |
| Software | Boolean precharge policies: **4,096 combinations** and **20 temporal cases**; registered receiver state machines: independent packet/temporal oracle, bounded state and decoder/history alternatives | Full train software, installed hardware, actual threaded concurrency, target real-time qualification and HIL remain open |
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
| `outbox`, `observations`, `champions`, `promotions` tables | Crash-safe follow-ups, Pareto alternatives, evidence levels and versioned research selections |
| `active.json` | Exact active source baseline and epoch |
| `epochs/<baseline>/baseline.json` | Engineering/controller source digests |
| `epochs/<baseline>/historical-inputs.json` | Verified prior input nominations; no old result/acceptance transfer |
| `epochs/<baseline>/work-orders/` | Inherited 63 work packages, 345 source allocations and 1,219 open baseline requests |
| `epochs/<baseline>/attempts/<design>/<attempt>/` | Task, generated model/code, solver/check records, logs, result and sealed receipt |
| `epochs/<baseline>/provider/` | AI requests, command/schema, raw events and responses |
| `capabilities/<need-key>/` | Isolated proposal worktree, work order, benchmark receipt, exact review and research registration |

Inspect progress:

```bash
tools/automation/osr-python tools/automation/design-continuous.py status
tools/automation/osr-python tools/automation/design-continuous.py dashboard
tools/automation/osr-python tools/automation/design-continuous.py verify
systemctl --user status osr-continuous-design.service
journalctl --user -u osr-continuous-design.service -f
```

`status` reports evaluated work through each lane's `completed` count. That count
includes retained rejections; it does not mean completed railway specifications.
`verify` checks finished attempts while running attempts continue to change. Use
`verify --historical` only for retained integrity after source changes.
`verify` does **not rerun physics**. Its result states `physics_rerun: false`.
Current verification also checks the recorded numerical runtime identity.

## Recovery, fairness and bounded context

Completion and a durable follow-up outbox are committed in one SQLite
transaction. A separate dispatch transaction queues every repair and evidence
need, updates the research archive, and marks the outbox delivered. Interrupted
dispatch rolls back; replay uses existing candidate identities to prevent
duplicates. AI response imports follow the same pattern. Startup also recovers
sealed worker receipts and valid final AI responses, and backfills old completed
results whose follow-ups may have been lost by the previous controller.
Blocked actions remain visible in `outbox_states`; they are not silently discarded.

The proposer selects the least recently served eligible lane using persisted
call history. Each eligible lane receives a turn within four dispatch opportunities;
queue saturation, cadence, backoff and the global hourly budget still apply.
Cadence is measured from completion. Error/no-progress suppression uses useful
progress signatures: champion revisions, new failure categories, context
confirmation and domain coverage, rather than every additional near-duplicate.

Requests contain bounded samples of recent failures, current Pareto alternatives,
domain coverage and compatible children. They omit the full historical design
list. The request limit is **128 KiB**. The prompt refers to the saved request
instead of embedding another copy. Separate allowances are **512 KiB inputs**,
**4 MiB logs**, and **2 MiB final response**. Input checks run before the AI CLI
starts; the supervisor monitors each allowance independently.

Read complete history by keyset pagination:

```bash
tools/automation/osr-python tools/automation/design-continuous.py history \
  --lane mechanical --after 0 --limit 20
```

Pass the returned `next_cursor` as `--after`. Controller-side deduplication always
uses the complete ledger. A 4,000-record regression checks request bounds and
pagination without losing or duplicating entries.

## Verification and useful improvement

Every new result has a `verification` record identifying its evaluated level,
scope, named checks and unexecuted levels. A generic study pass concerns only
the declared executed checks.

| Level | Implemented evidence and boundary |
| --- | --- |
| Analytical screening | Existing configuration-specific detail checks, with unknown acceptance retained |
| Native geometry | Exact simplified child solids, physical identities, occupied volumes/bounds and FCStd/STEP reopen; interference checks apply to the declared mechanical parts |
| Numerical confirmation | Independent Hermite beam FEM with candidate-specific equivalent EI, supports, loads and actual mesh/displacement/reaction records |
| Numerical robustness | Mesh refinement, closed-form simple-beam/cantilever controls and adverse-load linear response for that equivalent 1D model |
| Physical correlation | Open: requires applicable physical measurements and tests |

The numerical promotion confirms **gross elastic equivalent-beam bending**.
It does not supply shell/solid joint stresses, weld/contact/fatigue qualification,
prestressed cracked behaviour, complete reinforcement, soil interaction or
train-track-structure dynamics. Civil CAD retains intentional concrete/strand
overlays and gross support reservations. Complete interference and construction
acceptance remain open.

Promising detail candidates and representative adverse candidates automatically
queue receipt-bound confirmation jobs. Pending confirmation work is bounded;
later mass improvements of at least five percent can earn another promotion
after the initial samples. Research comparisons use a declared two-percent
agreement/refinement tolerance, independently of the existing design thresholds.
An installed-kernel pilot reopened a 142-part frame and a 158-part civil model,
and both passed their equivalent-beam comparison/refinement checks.

The persistent Pareto archive retains modeled mass and counted-part effort
proxies within each context and concept/manufacturing route. Quoted cost and
assembly time remain unknown until supported. Constraint records show signed
normalised distances to declared limits and preserve unknown/failed checks.
Versioned champions retain predecessors, selection reasons, evidence levels
and affected exact child/parent checks. Failed coupled candidates cannot replace
passing integration champions. Research adoption means selection for the
declared study scope, with every manufacturing and physical gate still open.

Integration explores a bounded set of light and robust representatives rather
than materialising every pair of locally similar frames and beams. Selected
Pareto neighbors receive scheduling priority. Historical warm starts retain
representative recipes per context; original attempts and unselected queues
remain historical and never transfer acceptance into the new epoch.

The dashboard separates evaluated/rejected, analytically passing, native-confirmed,
numerically confirmed, integrated and adopted-for-research counts. Categories
overlap. It also reports champion changes, oldest waiting work, blocked
capabilities, outbox state, unsuccessful AI calls and output consumption.

Source epochs bind Python, numerical package source/native bytes, solver binaries,
linked numerical libraries, and FreeCAD application/runtime commits where
applicable. A changed runtime invalidates current applicability and requires a
fresh epoch; historical integrity can still be inspected.

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

The default AI proposer has a maximum of **eight service calls per hour** and at least
ten minutes after completion between calls for the same lane. Unchanged successful or no-progress
requests are not repeated. Transient errors can retry the same context at most
three times with a 30-minute backoff. The installed two-minute cadence overrides
the default, while retaining the hourly limit. The numerical programme continues when
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
test thresholds is accepted. The original Boolean policy adapter keeps its fixed
fact interface and truth-table deduplication. The separately benchmarked receiver
adapter varies controlled decoding, bounded history, sequence and reset
implementations against its independent fixed state/temporal oracle.

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

## Missing-capability development

Missing capabilities can become scoped proposals in sparse, detached Git worktrees.
The workflow requires separate benchmark modules, adverse cases, resource bounds,
limitations, a passing benchmark receipt and a review bound to that exact receipt.
Registration checks that installed adapter/test bytes match the reviewed bytes.
This is repository-level research registration, not independent engineering
acceptance. Git worktrees isolate changes, not the operating system.

```bash
tools/automation/osr-python tools/automation/design-continuous.py capability-prepare --need NEED_KEY
tools/automation/osr-python tools/automation/design-continuous.py capability-check --need NEED_KEY
tools/automation/osr-python tools/automation/design-continuous.py capability-register --need NEED_KEY
```

Define `modules`, `benchmarks` and `limitations` in the generated work order;
implement and review the proposal before registration. The ordinary AI proposal
interface remains data-only and cannot register arbitrary code.

The first completed example is `software-frame-receiver`: generated executable
receivers test CRC/malformed packets, sequence rollover, freshness and clock
regression, fault latching, reset at standstill, bounded retained state and
enumerated event interleavings. Six valid decoder/history variants and two
negative controls seed the installed registered capability. Timing samples are
host observations, with target real-time behaviour, actual threaded concurrency,
full train protocols and SIL/HIL still open. It does not inherit the Boolean
precharge adapter's acceptance as evidence for this new behaviour.

LM3 alternative load paths and richer civil connection/ground models still need
their own implementations, independent benchmarks and reviews through this
workflow. Their present models do not represent those capabilities.

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
