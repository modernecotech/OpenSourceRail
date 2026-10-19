# Continuous design delivery

This pipeline turns eligible, confirmed runner revisions into a portable review
package at `docs/design-engine/continuous-delivery`. It does not infer complete
engineering designs from experiment counts. The completion ledger retains every
authoritative component, work package, required detail section and acceptance
gate; unresolved and unallocated requirements stay open.

The publication includes exact child/confirmation receipts and their files in
a bounded compressed archive; source/runtime and test receipts; editable native
FreeCAD and compressed STEP; selected simulation, manufacturing and QA records;
generated controller/receiver implementations; images; and eight-second H.264
assembly or construction sequence illustrations. Underframes without an
evaluated assembly graph receive a labelled camera inspection tour. Videos
reveal retained solids at final positions using evaluated operation or schedule
events; they do not prove crane motion, insertion paths, collision freedom,
temporary restraint or connection resistance. Physical tests, accepted loads,
full train-to-kit dynamics and independent authority acceptance remain open.

```bash
tools/automation/osr-python tools/automation/design-publish.py qualify --output /absolute/new/qualification
tools/automation/osr-python tools/automation/design-publish.py build --qualification /absolute/new/qualification/qualification.json --output /absolute/new/package
tools/automation/osr-python tools/automation/design-publish.py verify --package /absolute/new/package --media
tools/automation/osr-python tools/automation/design-publish.py cycle --qualification /absolute/new/qualification/qualification.json --push
tools/automation/osr-python tools/automation/design-publish.py install --qualification /absolute/new/qualification/qualification.json
```

Qualification executes the publication adverse/native tests, civil handling and
delivery controls, process adapters, failed-confirmation veto/recovery, protocol
tests and reporter regressions. Input code and data are hashed before/after.
Changed code requires fresh qualification. Exporting rechecks current source,
runtime, receipt integrity, eligibility and exact child/confirmation links.
Offline verification needs no private runner workspace and does not rerun
physics; `--media` also decodes the videos with ffmpeg.

The daily publisher creates a package only when selected confirmed revisions or
their evidence/source identities change, caps each package at 64 MiB (256 MiB
uncompressed raw evidence), and retains two prior local publication generations.
It refuses a dirty checkout, a stale source/test epoch, changed Git head,
unrelated staged changes, bad receipts, unavailable native tooling or oversized
outputs. It commits only the owned publication directory to `main` and uses a
normal non-force push. Existing worker evidence is never pruned. Git retains
history, so daily deduplication and the byte cap reduce growth but do not make
repository history size constant. Failed cycles leave existing publications
unchanged; the package is explicitly a dated snapshot, not continuing acceptance.

A separate 15-minute task-family coverage timer gives one waiting case per
starved family a slot, including whole civil kits and integration. It preserves
the 64-job lane limit, existing jobs and receipts, and records every priority
change. It does not bypass worker checks or solve missing evaluator capabilities.
The design runner's disk/output and physical evidence limits remain in force.

Services: `osr-design-publication.timer` (daily compact Git publication) and
`osr-design-coverage.timer` (15-minute family coverage), alongside the existing
continuous design service and hourly local geometry reports.

Publication uses the optimiser's delivery policy, rather than a separate mass
ranking. For each civil architecture/function it also retains eligible mass,
lift and onsite-work leaders sharing the primary's context and comparison-basis
identity. Extra leaders carry their selection roles and exact candidate keys;
all remain subject to the same native/confirmation vetoes and archive budgets
(at most 64 dependency jobs).

Offline verification compares exported results, metrics, verification claims,
open evidence, implementations, manufacturing tables and compressed schedules/QA
records directly with the archived originals. It regenerates summaries and
report text from those inputs. The requirement inventory is bound to the source
epoch, and the maturity ledger is recomputed from archived unit definitions,
exact native confirmations and individual handling/numerical checks. Five
explicit civil catalogue allocations currently link requirements to
representative unit revisions, joints and evidence paths/hashes. Similar names
create no allocation. Geometry and research screens remain separate from
manufacturing qualification, authenticated acceptance and complete design.

The publisher persists built, committed and pushed transaction phases outside
Git. Recovery precedes selection deduplication and the daily binary budget.
An interrupted installation or commit is reconciled using the exact parent,
owned-path diff and manifest bytes. Failed pushes retain the committed revision
and retry that exact commit with a non-force refspec, including when selected
designs have not changed. A 15-minute timer check retries transactions while the
one-generation-per-day budget still controls new binary publications. Failed
scratch builds are removed before any journal/Git mutation; journalled evidence
remains until push succeeds.
