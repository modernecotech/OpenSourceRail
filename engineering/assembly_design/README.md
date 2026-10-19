# Baghdad assembly development

This programme enriches source requirements and executes provisional assembly
experiments. Its initial supported scope is one LV/ventilation cassette, one
replaceable bearing seat and an executable cassette interlock. It does not
complete the train, civil works or all remaining component generators.

The input registry separates published supplier/reference facts, repository
planning values and proposed pilot assumptions. Every fact has a source,
locator, unit, scope and non-approved status. Country climate observations do
not establish a site design extreme. Supplier headline limits do not establish
combined performance or an offered railway configuration. Proposed manufacturing
tolerances, loads, stress screens and productivity values are not approved limits.

The 345 pre-existing records retain their identities and architecture boundaries;
246 have the LM3 namespace. The 69 Baghdad reference-part records are separately
allocated, giving 414 scoped records without claiming physical BOM completeness.
Three Baghdad records currently connect to the two pilot generators. Remaining
records produce explicit component-specific generator/evaluator work orders.

Cassette definitions include a perforated tray, individual rail plates/webs,
mount pads and fasteners, duct walls/feet, eight conductors and jackets, drilled
clamp bars/standoffs, earth hardware and an exact GB-origin Harwin reference
connector. The connector is a coordination envelope with published mass, not a
reconstruction of its internals. Mating/termination geometry, clamp retention,
seals, bond conductors, insulation/derating, vibration and whole-car HVAC remain
open. The software trials test a latching permission interface, not train control.

Bearing-seat studies include drilled plates, guide members, grout, anchor
hardware envelopes, local uniform-bedding/plate-strip and elastic bolt-group
screens, and thermal travel. Deck mass comes from the existing compiler geometry;
six-car demand is separately recomputed from declared 384/460.8t uniform planning
cases. No LM3 force result is reused. Axle loads, dynamic interaction, contact,
prying, fatigue, local concrete/anchor resistance, offered bearing configurations
and the fixed/guided/free arrangement still require their own verification.

Candidate revisions cover the actual generated geometry, interfaces, materials
and metadata. A source/runtime-bound SQLite queue deduplicates trials, recovers
sealed results after interrupted database writes, retains partial evidence and
vetoes failed native confirmations. Native checks reopen FCStd, reconcile mass,
CG/inertia and STEP, and screen static solid intersections. They do not verify
moving paths, welds, threads, anchor development or physical performance.

```bash
tools/automation/osr-python tools/automation/design-assemblies.py qualify
tools/automation/osr-python tools/automation/design-assemblies.py run --budget 40
tools/automation/osr-python tools/automation/design-assemblies.py cycle --budget 6
tools/automation/osr-python tools/automation/design-assemblies.py install
tools/automation/osr-python tools/automation/design-assemblies.py status
tools/automation/osr-python tools/automation/design-assemblies.py develop
```

The five-minute timer runs six pending experiments per cycle and retains a
portable local report at `~/.local/state/opensourcerail/assembly-design/latest/`.
The fixed first campaign has 36 physical recipes and two software implementations.
After exhaustion it explicitly waits for new requirements or capabilities; it
does not repeat identical trials. A separate hourly capability service assigns
missing Baghdad component work to an isolated developer and a separate critic.
It retains proposed source, declared assumptions, native evidence and the exact
review, with two provider calls per hour and at most two attempts per component.
A known native failure or unavailable tool cannot become a successful research
improvement. Reviewed proposals are not automatically imported into the runner;
independent numerical benchmarks and adapter/interface registration remain
required before a new evaluator becomes trusted research infrastructure. Resource limits are 2 GiB of programme output, a 20 GiB
free-space reserve, 2 GiB service memory and a 15-minute service timeout.

Exports contain exact original receipts/evidence, the requirements and fact
registry, qualification log, candidate CAD, drawings, BOM/process data, unexecuted
QA plans and software tests. Verification compares exported copies and report
metrics with archived originals, including after outer checksums are regenerated.
XY inspection layouts and native previews are explicitly unissued. The initial
repository snapshot is under `docs/design-engine/assembly-design`; subsequent
automatic reports remain local until a reviewed repository publication.

The capability worker reuses the already configured proposal executable/model.
It writes only to an owned sparse Git worktree, checks that protected tracked
source remains unchanged, executes the proposed generator with bounded time and
output, and runs the trusted native-contract checks. A separate read-only critic
reviews exact proposal/source digests. Git worktrees isolate source changes, not
the operating system. All qualification/release flags remain false. The worker
preserves private source/output before deleting reproducible clean checkouts;
failed protected-source edits remain held for inspection. It does not contact
suppliers, send messages, merge code or claim an approved design.
