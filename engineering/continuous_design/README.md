# Persistent engineering design runner

The runner executes mechanical, civil, software and integration work continuously
under a durable SQLite queue. A user service keeps it independent of the chat,
resumes interrupted work and restarts after process failure. Read the
[operating guide](../../docs/design-engine/continuous-runner-2026-10-17.md).

The [development plan](data/expansion-plan.json) maps the next six work packages
to implemented research pilots and remaining engineering evidence. The
`process-aware-multidiscipline-search` capability adds three source-bound task
families only after its independent/adverse benchmark receipt and exact-source
review are registered. Unsupported topology optimisers, material systems,
circuits and CFD models remain missing capabilities, not executable AI proposals.

The roof cassette varies explicit ply schedules, skin/core thickness, complete
core-grade records and crown. It calculates laminate A/B/D and strip/hot-wet
screens from those same plies. The current core cards fail the fixed 85°C roof
context; the runner records the required compatible high-temperature material
system and stops repeating that blocked family. Full curved-shell, contact,
resin/cure and complete-stack fire qualification remain open.

The equipment demonstration compiles existing battery/HVAC alternatives and
compares a real RHS ladder with a folded-pan material-region model, an optional
rib and welded/bolted cover. Duct dimensions change both modeled sheet mass
and pressure/fan demand. A two-zone heat/moisture model includes declared
ventilation, door, solar and internal-load hypotheses, failed-module cases and
time refinement. Auxiliary capacity and cooling-loss battery duty can reject
thermal improvements. These are reference planning hypotheses, not measured
Baghdad climate, passenger ventilation requirements or supplier performance maps.
The minimum usable-energy hypothesis stays at the fixed reference pack; a
smaller battery cannot win by silently reducing required function.
Known battery installation-bay failures complete as rejected studies with the
compiler constraint retained. They generate smaller-layout trials and never
request native confirmation of an absent physical model. Unrelated compiler
errors remain execution failures; earlier failed attempts stay in history.

The civil study connects the existing ten deck families and six pier families
with their compatible material/foundation records and bounded dimensions.
Comparison scope remains the existing 100m reference: five 20m two-track bays.
Native material solids and a 2D elastic moving-load static model are evaluated;
defined source research limits are enforced, while unset response limits stay
explicitly unresolved and prevent any claim of engineering feasibility.
Synthetic materials, perfect-bond assumptions, final reinforcement, manufacturing
unit grouping, temporary works and actual Baghdad ground remain unqualified.

The `civil-kit-study` family compares a complete 20m two-track reference cell
with two full supports, retaining that boundary for every alternative. Its
large-span Pi, segmental-box and lighter ribbed examples include piles and
prefabricated cages, foundation caps, piers, pier caps, bearings, track-support
modules, walkways/parapets and separate power/data/drainage provisions. Registered
choices include bored versus conditionally driven foundation bundles, split
foundation/pier caps, six pier forms, segmented columns and service-module length.
Station platform, independent footing/frame, canopy and stair packages use a
separate comparison context so omitting a station can never appear as a saving.
Stair supporting detail, complete services and actual station/railway acceptance
remain open. The reference train is the retained source axle pattern, not an
adopted Baghdad six-car load case.

Manufactured-unit IDs group exact CAD regions and explicit mass allowances.
Those IDs survive native FCStd reopening and are reused in the RFQ CSV, joints,
construction stages and QA templates. A cap-seat geometry revision is accounted
in the material ledger; original reinforcement/prestress and track allowances
are retained, with new kit additions accounted separately. Unknown cable,
connection and reinforcement detail is never represented as qualified hardware.

Construction checks include demoulding, transport and lifting gross-beam demands,
capacity at the declared crane radius, mat pressure, tolerance/engagement and
stage precedence. Bores precede cages; segment assembly precedes post-tensioning;
temporary support cannot be removed before connection and test completion.
Early-age strength, stability, connections and ground still require their own
qualified evidence. The event scheduler holds moulds through cure without charging
passive curing as labour, holds loaded trailers until crane placement, reserves
site waiting spaces, and accounts for bulk mixers, excavation, crews and QA.
Capacity perturbations identify bottlenecks under the declared scheduling policy;
this is a conditional heuristic schedule, not a proven minimum delivery time.

Required joint retention and inspection coverage are constraints. Inspection
count is diagnostic; inspection effort can only be compared with matching
required coverage. QA records require exact unit revision, serial identity and
interface context; changed definitions request retests. Template hold points are
unexecuted, and record consistency never authenticates a supplier or grants release.
The civil-kit primary policy minimises scenario onsite work, then delivery time,
lift and mass. Complementary leaders remain visible and can earn confirmation
through non-mass improvements, including heavier alternatives. Small final
improvements are still confirmed when a context becomes idle or stagnates.

Reproduce the three complete-scope planning examples in a new output folder:

```bash
tools/automation/osr-python tools/automation/design-civil-kit.py --output /tmp/osr-civil-kit-comparison
```

Outputs include manufactured-unit RFQ tables, material/allowance ledgers,
handling demands, factory/delivery/erection schedules, capacity sensitivities,
QA travellers and identical train/ground/durability/criteria fingerprints.
Default productivity and crane/transport values are declared uncalibrated
hypotheses, not supplier ratings or an erection instruction. Costs stay null
until every unit revision and installation/temporary-work/disruption scope has
input quotations. Factory work included in unit supply is not charged twice.
The comparison does not establish a cheapest accepted railway design.

Fresh site concrete has explicit batching, travel, waiting, discharge and mixer
return events. The pump and crew are reserved before batching; mixer occupancy
continues through unloading and return. Dispatch offsets aim for continuous
placement, but actual batch-to-discharge-end age and gaps between discharges are
independently checked. The reference four-hour age and quarter-hour gap bounds
are **unqualified mix/temperature scenario inputs**, not universal limits,
supplier claims or Baghdad placement acceptance. Tightening them or reducing the
mixer fleet can reject the delivery scenario. Reserved crew waiting time counts
as labour. Batch tickets, weather, admixtures, tests and real continuity/strength
criteria still need qualified records.

Driven piles include pitching, rig occupancy, driving per declared segment,
splicing when declared, installation records and acceptance operations before
the foundation can progress. Registered examples are full-length precast piles;
splice scenarios do not create qualified splice geometry or resistance. The
ground-applicability hold remains mandatory. Falsework tokens are held from
mobilisation through final removal, including partial erection and connection
completion. Temporary units have the same transport, crane-radius, rigging and
ground-pressure screens as permanent units. Their envelope/mass assumptions are
not a detailed temporary-works design.

QA events use content-derived immutable identities and explicit sequence and
interface bindings. Exact replay is idempotent and record ordering cannot clear
a failure. Each failure requires an applicable later passing retest and a
documented later disposition referencing both event identities. Superseding a
test record alone cannot clear a failure; legacy/unidentified records cannot
establish passed-record coverage. These are consistency checks on submitted
history, not an authenticated append-only evidence store or physical acceptance.

The progress table presents modelled mass, largest lift, conditional onsite
labour/delivery, resource-capacity sensitivity and outstanding evidence, linked
to receipt-verified study results. Further development remains necessary for a
single component/connection definition spanning every evaluator; changing-support
and early-age structural analysis beyond the gross beam screens; receipt-bound
train-to-kit integration; shared-support/multi-front corridor optimisation;
qualified lightweight/hybrid kit bundles; and complete train harness/duct
cassettes with mating, locking and bench-to-installed test continuity. The
synthetic two-bay falsework regression checks resource ownership, not a corridor
design or throughput prediction.

Every physical family has an applicable process profile. The new pilots assign
every represented part/material region to one, execute operation prerequisites,
fixture hypotheses, inspection hold points and conservative removal envelopes,
and pack rectangular blanks with gauge separation and kerf. Missing tool sweeps,
clamping, weld distortion, cure, actual inspection and supplier procedures remain
unknown. A simulated inspection point is never human acceptance. Folded-pan
geometry uses sharp-corner regions and conservative blank allowance; bend
material is carried as an unresolved mass allowance without stiffness credit.
Springback and finished corner geometry still need qualification.

Weld/bond operation counts include declared destructive joins; equipment and
removable covers use their selected fastening route. These graphs still describe
represented regions, with final manufacturing-unit grouping unresolved.

Pareto comparison retains mass alongside available scrap, operation, setup,
fixture, inspection and repair counts. These are scoped geometric/count proxies,
not measured labour time, supplier quotations or complete installed mass.
Selected exact revisions receive native FCStd/STEP checks and the explicitly
named discipline numerical confirmations; later failures use the same
eligibility veto and holds as the original frame/Pi-beam pipeline.

```bash
tools/automation/osr-python tools/automation/design-continuous.py init --with-ai
tools/automation/osr-python tools/automation/design-continuous.py install
tools/automation/osr-python tools/automation/design-continuous.py status
tools/automation/osr-python tools/automation/design-continuous.py dashboard
tools/automation/osr-python tools/automation/design-continuous.py verify
```

The default workspace is `~/.local/state/opensourcerail/continuous-design`.
`status.json` is atomically replaced with the current heartbeat, active workers
and resource state. `queue.sqlite` retains jobs, attempts, results, events and
missing adapter/evidence needs. Every attempt has its own immutable directory.
Completion and follow-up outbox capture are one transaction. Dispatch and AI
imports replay idempotently after a crash; legacy completed results are backfilled.

Computational workers are fixed tools. One optional, sequential AI proposer uses
the installed CLI, saved login and a read-only sandbox to return typed data.
`config.json` controls its model/executable, cadence and call budget. A blank
`provider_model` inherits the CLI model; an explicit value affects only this
runner. The controller rejects unknown variables, changed limits and executable
code in proposals. Software generation uses a restricted Boolean expression
language or separately benchmarked bounded receiver templates. Proposer turns
use persisted least-recently-served order; prompts contain bounded representative
history with paginated lookup and separate input/log/response budgets.

Mechanical and civil failure-directed candidates are generated by existing
numerical adapters even when the AI service is unavailable. Passing detail
designs generate nearby material-saving trials, each subject to the same checks.
The documented incompatible LM3 constant-EI family records an alternative
structural-adapter need instead of repeatedly sampling its unchanged envelope.
Integration uses
receipt-bound mechanical, civil and software children from the same baseline and
train configuration. Automatic couplings use passing children; actual coupled
civil failures generate repair trials. Unknown physical/manufacturing acceptance
stays open.

Research eligibility also incorporates every applicable confirmation for the
exact candidate revision. A mandatory native/numerical failure excludes the
candidate from current champions, Pareto selection and integration admission.
Unavailable tools, incomplete measurements and interrupted execution hold it;
these are distinct from a deterministic design failure. A first confirmation
still pending permits explicitly provisional analytical exploration. Physical
acceptance remains separate in every case.

`integration_dispositions` marks dependent queued, running and completed studies
as held or superseded. Original analytical results, integration results and
champion history stay immutable. Current summaries exclude ineligible studies
and select the next eligible alternative, including a previously dominated one.
Admission, dispatch and worker execution recheck live evidence. Automatically
generated integrations bind an evidence revision, so subsequent receipt changes
can produce a fresh re-evaluation of the same physical candidate combination.

Work is deduplicated by engineering inputs. Software is also deduplicated by its
complete Boolean truth table. A rejected design remains an evaluated experiment;
execution failures get at most two attempts. AI errors have backoff and at most
three attempts for unchanged context. Exhausted queues leave the service watching
for new work instead of repeating identical calculations.

There is no lifetime experiment-count cap. Each lane admits up to 64 queued or
running jobs; further distinct recipes remain durable `deferred` records and
are promoted as capacity returns. The workspace/disk and AI-call limits still
apply. AI feedback includes failed predicates, check details and a context-balanced
child catalogue that prioritizes passing results over recent failed experiments.

Source changes invalidate the active baseline. Dirty edits wait; once the source
change is committed, the service restarts with fresh Python imports and a new
source-bound epoch. Prior attempts remain historical. New baseline evaluations
do not borrow acceptance from old runs. Verified historical passing recipes and
the closest failed detail recipes nominate input values for fresh evaluation;
`historical-inputs.json` records provenance. Previous integration child keys and
results are never reused as current acceptance.

New results name their verification level. Selected detailed children receive
native FCStd/STEP geometry checks and an independent mesh/refinement/benchmark
confirmation of their equivalent one-dimensional elastic beam model. Full
connection, shell/solid strength, soil, dynamic and physical qualification stay
open. `verify` checks source/runtime/artifact applicability and integrity;
it explicitly reports that it does not rerun physics.

Confirmation independently measures section area, centroid, inertia and volumes
from reopened B-rep solids, using two prismatic stations and an independent box
control. The equivalent beam solver uses this recovered stiffness, while keeping
the existing material, loading, support and compatibility hypotheses explicit.
Mechanical mass covers the modeled solids. Civil represented mass recovers gross
concrete and strand length; metallic strand area remains a declared material
input, and analytically estimated links remain an unrepresented mass allowance.
Neither full reinforcement geometry nor complete assembled mass is inferred.
After a context becomes idle or its best candidate stagnates for 15 minutes,
the exact best unconfirmed revision is nominated even below the usual five-percent
improvement threshold, subject to the existing pending-confirmation resource cap.

`integration-protocol` adds a fourth exact child, the registered receiver, through
the experimental `osr-precharge-link/1` interface. It executes the retained
generated receiver and controller together: corrupt/stale/duplicate packets,
sequence wrap, independent local vetoes, a normal voltage ramp and stopped/moving
reset paths propagate to modeled closure permission. Independent event-sequence
controls and a deliberately broken bridge test the composition. This remains an
offline interface model, with physical network, target timing and SIL/HIL open.

SQLite observations retain Pareto alternatives, constraint margins and versioned
research champions. Cost and assembly time stay unknown without evidence.
Runtime identity binds numerical package bytes, solver binaries, linked libraries
and FreeCAD runtime commits. The dashboard reports useful improvements and
separate evidence counts, including unsuccessful calls and waiting work.

Missing capabilities can be developed through `capability-prepare`,
`capability-check` and `capability-register` in an isolated Git worktree. Passing
independent/adverse benchmarks and a review of the exact receipt must match the
installed bytes. Ordinary proposals cannot register arbitrary new code.

```bash
tools/automation/osr-python tools/automation/design-continuous.py history \
  --lane mechanical --after 0 --limit 20
```

```bash
systemctl --user status osr-continuous-design.service
journalctl --user -u osr-continuous-design.service -f
systemctl --user stop osr-continuous-design.service
systemctl --user start osr-continuous-design.service
```

`verify --historical` checks retained identity/artifact integrity without asserting
current source applicability. Neither verification mode provides engineering
acceptance or physical release.

Hourly progress pictures are available through a separate, read-only reporter:

```bash
tools/automation/osr-python tools/automation/design-progress.py snapshot --notify
tools/automation/osr-python tools/automation/design-progress.py install
systemctl --user list-timers osr-design-progress.timer
```

Open `~/.local/state/opensourcerail/continuous-design/progress/latest.html` for
the latest report; it refreshes every minute while the hourly timer generates
new snapshots. Reports show all four lanes, research rejections separately from
execution errors, evidence counts, changes since the previous snapshot in the
same epoch, and changes to research candidates within the same context. Counts
are experiments, not completed railway components. Epoch changes reset comparisons.

Pictures tessellate retained, receipt-checked FreeCAD solids, with candidate IDs,
contexts and exact proportions. Confirmed passing examples are selected ahead of
unconfirmed analytical candidates; geometry gaps and rendering failures remain
visible. No CAD is regenerated or saved, and no acceptance is inferred from a
picture. Native input hashes and image hashes are retained in each snapshot.
The numerical evidence remains scoped to equivalent 1D elastic bending.

The timer runs independently of the engineering service, catches up after missed
hours and uses bounded CPU, memory and execution time. It retains at most 48
presentation snapshots within a 256 MiB budget (always preserving the newest);
original experiments and native evidence are untouched. `--notify` requests a
local desktop notification with a geometry icon and report link through the
session notification service. When logged out or notifications are unavailable,
the report still updates and `progress/notification.json` records delivery state.
This local timer does not post messages into the chat. Disable it with
`systemctl --user disable --now osr-design-progress.timer`.

Tests:

```bash
tools/automation/osr-python -m pytest \
  engineering/analysis/tests/test_continuous_design.py \
  engineering/analysis/tests/test_continuous_planning.py \
  engineering/analysis/tests/test_continuous_reliability.py \
  engineering/analysis/tests/test_continuous_verification.py \
  engineering/analysis/tests/test_continuous_eligibility.py \
  engineering/analysis/tests/test_protocol_receiver.py \
  engineering/analysis/tests/test_protocol_system.py \
  tools/automation/tests/test_design_progress.py -q
```
