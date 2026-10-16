# Factory review follow-up: portable evidence and common design jobs

The review of `cd0ca78a39` identified numerical-platform sensitivity and an
isolated factory workflow. This change preserves every original factory report,
drawing, native model and receipt, and adds a separate reproduction seal and two
controlled problems in the common design engine. It does not reissue those
original examples as newly manufactured or physically qualified designs.

## Reproduction policy

`engineering/factory_examples/examples/reproduction.json` binds the exact bytes
of every retained generated artifact, native receipt and FCStd. It records the
original producer source hashes and toolchain separately from the current
verification source/input hashes. A changed source requires explicit
re-verification; it cannot pass merely because a numerical result is close.

Independently recomputed floating values use a relative tolerance of `1e-9`,
with these absolute floors for SI cancellation near zero:

| Field suffix | Absolute floor |
| --- | --- |
| `_n`, `_nm` | 1e-5 N or N m |
| `_pa` | 1e-4 Pa |
| `_kg` | 1e-7 kg |
| `_m` | 1e-10 m |
| `_m2`, `_m3` | 1e-12 m² or m³ |
| `_m4` | 1e-14 m⁴ |
| Other floating results | 1e-12 in the declared field units |

These are computational comparison tolerances, not engineering allowables.
Counts, states, booleans, unknown values, dictionary fields, array lengths and
native geometry definitions compare exactly. CSV result values follow the same
policy. Prose uses the existing explicitly rounded presentation. Retained SVG
bytes are exact; regenerated Matplotlib paths may differ across fonts/backends.
Their underlying numerical JSON is checked separately; no pixel equivalence is
claimed. Original environment metadata are never overwritten by the verifier's
versions.

```sh
.venv/bin/python -m engineering.factory_examples.build --check --verification-report build/factory-recomputation.json
```

After a reviewed verifier change, `--seal-retained` creates an updated seal by
recomputing and comparing against unchanged originals. It refuses to reseal
modified originals. Changed engineering examples must be built in a fresh
directory with `--output <directory> --native`, retaining the previous evidence.

## Common controlled problems

| Problem | Variables | Represented native inventory |
| --- | --- | --- |
| `factory-fixture` | Payload 250/500/750 kg; requested preload 250/500/1000 N | Fixed 1.6 × 1.0 m fixture and clamp envelopes, 32 objects |
| `factory-precast` | Pi20/Pi25; three prestress layouts; independent lateral/vertical restraint cases; 4/16/134 casting positions; 1/2 cranes and crane crews; 100/125 t handling scenario; stressing/unloading and frame-ground hypotheses | Historical end assemblies have 63/93 objects; current nominal whole bed has 376 |

All candidates retain the common city/project/environment/revision identity,
declared domains, evaluation/wall/memory/artifact budgets, source and toolchain
hashes, immutable attempts, mandatory check matrix and physical-release boundary.
These charters apply to simulation/training. Position count changes a capacity
scenario; it does not silently enlarge the four-position yard layout. The
precast native inventory represents one end assembly; the remaining bed, product,
reinforcement, crane, foundations and factory remain named unresolved allocations.

Native primitive definitions cross into `osr-factory-definition/1` per-instance
inventories. Nominal steel mass is reported separately. Supplier/envelope masses,
CG and inertia are not invented; complete inventory mass stays unknown. Common
BOM reconciliation checks identities, quantities and properties against this
definition. Offline exports retain original attempts, sources, BOM, checks and
RFQ requirements. Native confirmation executes the existing factory exporter,
with a common wall-budget supervisor and owned-process cleanup; it never forks
a second geometry implementation.

```sh
./osr design run --problem factory-fixture --city baghdad --revision factory-integration-1 --refine --evaluations 4 --wall-seconds 180
./osr design run --problem factory-precast --city baghdad --revision factory-integration-1 --refine --evaluations 4 --wall-seconds 180
./osr design export <job-id> --output build/factory-review-<unique-name> --native
```

The common [comparison interface](index.html) exposes the new problems and shows
their factory demands, both-plane elastic factors and resource bounds alongside
the shared verification matrix. Different functional problems are not directly
ranked as interchangeable products. Within each fixed problem, scenarios expose
trade-offs across product, tooling and plant through the same candidate data.
Installed cost, imported content and a complete mass objective remain unknown,
so no cost optimum or verified design frontier is claimed.

## Coupled engineering findings and next work

The default balanced Pi25 scenario reproduces approximately 7.392 MN bed force
and a 104.69 t handling-equivalent lower bound. Lower-strand-count candidates
reduce these demands but retain their failed dead-load zero-tension screens.
Changing the handling scenario changes runway wheel demand; a 100 t scenario
fails the known handling lower bound. A 125 t scenario remains unknown because
additional reinforcement, attachments and a qualified lift plan are absent.

Independent lateral and vertical return-rail eigenvalue/imperfection models use
the same nominal RHS section and restraint stations. Either plane can fail when
its ground springs are removed. Passing a hypothetical spring case does not
establish the foundation, anchor, base rotation or connection load path. Local
strongback plate/opening/weld resistance and controlled release remain open.

The initial production input register names reinforcement, stressing/release, batching,
crane handling, storage/dispatch, haulage, labour and maintenance. Missing resource
counts, cycle times or availability remain unknown. Known stage capacities give
necessary upper bounds and required resource counts, not an executable schedule.
Four beds retain the 1.615/day planning bound and fail the 54/day case. At 134
positions, the bed bound alone clears that target, while end-to-end output stays
unknown. Shared resources, queues, curing maturity, storage dwell, maintenance,
transport and actual shifts still require a validated production model.

The [support and finite-calendar continuation](factory-support-notes-2026-10-16.md)
adds compression-only grout/tension-only anchors, pad and weld demand screens,
series interface sensitivity and an executable shared-resource planning calendar.
Its [native review](factory-support/index.html) retains failed soft support and
production backlog cases. These synthetic scenarios do not close the physical
foundation, local resistance, crane coverage or measured-output gates above.

Remaining engineering priorities are railway loading/compression/transmission,
reinforcement/shear/fatigue/deflection, local and foundation resistance, measured
process scheduling, configuration-specific supplier returns and installed-cost
evidence. The prior 20-case independent vehicle refinement remains inconclusive;
this factory software change does not alter its results or claim convergence.

## Required local acceptance

```sh
./osr check --scope impact --changed engineering/factory_examples/native.py --plan
./osr validate run --profile factory-native --output build/validation/factory-native-<unique-name>
./osr validate verify build/validation/factory-native-<unique-name>
```

Factory source/input changes identify both affected problems. Factory retained
artifacts and acceptance tests also select `factory-native`. The profile fails
on missing FreeCAD, omitted models/jobs, export/reopen failures, altered artifacts
or stale sources. It executes nine fresh FCStd/STEP exports and two actual common
jobs, then verifies their source-bound offline exports. Exact artifact membership
and file hashes are retained by the outer local-validation receipt. This gate is
geometry/software acceptance; the separate four-profile software-release gate
and physical engineering acceptance remain unchanged.
