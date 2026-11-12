# v0.7 Samawah corridor continuity

The first milestone is implemented in the existing Workbench: open the city
atlas, select **Samawah**, and choose **Compare Samawah station merge**. It
recalculates the published network and the midpoint edit using the same
explicit-headway evaluator, vehicle inputs and cost policies. The comparison
offers both dossiers, the revised delivery draft and a downloadable report.

The two raw markers are 79.976780 m apart. The edit replaces them with one stop
at chainage 9,339.173756 m without changing the alignment coordinates. The
published example already groups them as one operational complex. The retained
compact-drive midpoint study uses another body candidate; its fleet and cost
results are not transferred to this comparison.

| Measure | Before | Midpoint edit | Change |
|---|---:|---:|---:|
| Raw markers | 26 | 25 | −1 |
| Operational station complexes | 25 | 25 | 0 |
| Route length | 57,873.249527 m | 57,873.249527 m | 0 |
| Total trainsets | 81 | 81 | 0 |
| Base installed capital | $1,141,490,831.10 | $1,141,480,801.60 | −$10,029.49 |
| Base whole-life NPV | $2,258,426,041.73 | $2,258,655,801.42 | +$229,759.68 |

These are provisional model estimates. Line 1's one-way time increases by
1.494405 seconds; the other four lines are unchanged. All fourteen cost scopes
are reported, including zero deltas. The base energy NPV increases by
$239,881.94. The existing 79.976780 m access-repair allowance is replaced by a
70.690214 m revised-access hypothesis with its own explicit risk allowance;
contingency, design provision and disposal also change. This does not establish
a surveyed walking route or a verified local price. The civil quantity identity
and vehicle/manufacturing reference inputs remain unchanged.

The report preserves physical candidate, planning revision, city/service/cost
evaluation, selection, civil quantity, manifest and delivery identities. Unknown
quantities remain unknown. It retains the line-1 coast-reach failure, conditional
powered-axle research comparison, missing actual force/braking evidence,
transferred cost rates, access/catchment/platform questions and open installed
vehicle/manufacturing findings. The passive-wheel reference is not replaced by
the research propulsion policy.

## Measured execution and verification

The real browser run passed on clean commit
`798a2c292acdddde8227c9b9ad49e74bb6e5b561`, comparison
`d66f7add2536a0c678ca5bf56f51d9788cedf8ac402f36b7e4456eaf6cbab88e`.
Desktop and mobile screenshots were inspected. There were no browser errors,
external requests or changes to tracked/untracked source files.

The two numerical studies were produced on `91916d900e` and retained after the
browser exposed an integer JSON transport mismatch in the new helper. Correcting
that helper did not alter their exact request or evaluator source identities.
The successful browser run verified and reused those existing artifacts; its
10.96-second first click is therefore not a cold-calculation measurement. A
second unchanged click reused the same verified job identities in 1.62 seconds.

| Worker measure | Before | Midpoint edit |
|---|---:|---:|
| Worker elapsed | 16.25 s | 16.31 s |
| Evaluation elapsed | 13.73 s | 13.81 s |
| Peak RSS | 302.33 MiB | 419.25 MiB |
| Artifact payload | 24,482,861 bytes | 24,477,356 bytes |
| Native solver / CAD jobs | 0 / 0 | 0 / 0 |

The [compact evidence record](samawah-milestone.json) contains exact identities,
all scope deltas, source hashes, performance, retained failure descriptions and
hashes of external raw reports, logs and screenshots. Raw study packages remain
outside Git. Identity equality alone is not presented as proof of execution
cache reuse; the browser checks stable verified job identities separately.

Focused regression checks passed: 61 tests covering the helper, API cache
custody, city jobs and planning adapter. A read-only specialist review reproduced
those tests and checked the browser numeric-boundary fix; it was not OS-isolated
or a physical design approval. The existing Samawah CI workflow now also runs
this browser comparison from a fresh store and uploads its outputs.

Reproduce in an installed development checkout with an external, empty output
directory (the normal environment supplies `.venv` and Playwright):

```sh
node tools/automation/tests/verify-v07-samawah-corridor.mjs /tmp/osr-v07-samawah-new-run
```

`OSR_PYTHON` selects another Python environment. `OSR_CITY_STUDY_STORE` can point
to retained external verified jobs; the report records that configuration and
does not label it cold execution. Stores inside the source checkout are refused.

## Next integrated work

This closes the first comparison milestone, not the v0.7 programme. Subsequent
native city cycles, project invalidation, counted door views and performance
work are recorded in the [execution update](../v07-execution/README.md). Next bind
one installed six-car candidate, representative civil/station assembly and door
operator to this project, then complete their detailed interfaces, controlled
manufacturing/QA/removal package, native GIS return path, ERPNext/FUXA lifecycle
and Baghdad replay. Supplier information and physical tests retain their own
open milestones. See the [six workstreams](../../ROADMAP.md).

The local coordinator kept the 20 GiB free-space reserve, removed only its known
redundant browser downloads and retained failed and completed study evidence.
The worker reports shared-filesystem admission and bounded output monitoring;
an aggregate filesystem quota is not enforced.
