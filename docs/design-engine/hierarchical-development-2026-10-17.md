# Hierarchical engineering experiments and review repairs

The [executed hierarchical pilot](hierarchical-pilot-2026-10-17/index.html)
connects component proposals, affected parents, independent checks and versioned
experimental adoption. The [optimisation review](generative-detail-optimization-2026-10-17/index.html)
continues the detailed search after feasibility. Neither result grants
manufacturing, construction or operational release.

## Review findings resolved

The twelve omitted STEP exports in the original detailed packet and its layout
prototype were recovered byte-for-byte from the existing immutable store. Their
original projection manifests and seals remain unchanged. An explicit Git ignore
exception retains those exports. `verify_git_projection` reads the staged index
or a committed Git tree, including every reachable evidence object, rather than
trusting local files. Tests reproduce the omission and verify a fresh clone;
corrupt/missing indexed objects and symbolic links are rejected.
Original packets remain historical after engine changes: Git-tree integrity and
historical verification check their preserved bytes; current-source runs use
fresh destinations rather than replacing those records.

Interrupted numerical campaigns now write atomic, checksummed execution state
before evaluation and after updating the frontier. The state binds sources,
context, options, numerical environment, completed contexts and active proposal.
Resume accepts this state without a completed receipt, into a fresh directory.
Completed immutable evaluations are reused, including the crash window between
attempt persistence and snapshot replacement. A real killed-worker test exercises
this path. Interrupted directories remain preserved. External CAD/export and
preliminary-baseline stages are rerun when needed; this does not resume an
external solver's internal state. A final receipt seals completed results.
If a larger budget changes the selected mechanical mass, coupled civil descendants
are recalculated under new context hashes. The prior traces and explicit
replacement links remain in the report; previous civil results cannot silently
qualify the changed loading.

Default `repair` mode retains its first feasible research result. Explicit
`optimization` mode continues within the declared finite domain and budget,
deduplicates candidates and retains a deterministic conditional Pareto set using
the existing common frontier function. Comparable objectives are modelled steel
mass and plate-count or link-count proxies with stated definitions. These proxies
do not establish labour hours, price, complete assembly mass or supplier offers.
Unknown cost and material acceptance never become favourable scores.

The executed bounded optimisation run evaluated **192 variants** across six
contexts, with 32 evaluations per context. Five contexts reached passing known
checks and retained **eight conditional Pareto alternatives** in total. The LM3
frame remains unresolved. All variants, dominated results, failures and unknowns
remain inspectable; the budget does not establish a global optimum or release.

## Roles and execution

The implementation was developed and challenged by collaborating specialist
agents. Runtime proposals carry a named producer, exact base commit, patch and
allowed paths. The controller evaluates those records using actual tool calls in
separate detached sparse Git worktrees. It does not launch an LLM service or
describe numerical role adapters as fresh LLM conversations.

| Role | Output and controlling boundary |
| --- | --- |
| Coordinator | Typed jobs, fixed acceptance policy, dependencies, budgets and stop conditions |
| Mechanical and civil designers | Changed geometry and recorded calculations, including adverse cases |
| Software developer | Isolated source patch, exact ancestry and proposed objective |
| Manufacturing specialist | Process, equipment/interface and missing production evidence requests |
| Verification specialist | Separate immutable acceptance fixture and benchmark/regression outcomes |
| Integration specialist | Exact-revision parent checks, coupling residuals and adoption decision |

The existing design-engine SQLite store owns jobs, immutable attempts, requests,
events and artifact manifests. Each tool record contains its actual argv,
return code, explicit state, log hash and resource policy. Concurrency is bounded
to one through three workers; the pilot uses two. Candidates cannot widen allowed
paths or edit acceptance tests. Controller-owned limits bound candidate count,
command duration and log bytes; a timeout or output limit is inconclusive.
Before and after each tool, tracked, untracked and ignored files are compared.
Worktrees isolate source revisions; they are not a security sandbox for hostile
code, and they do not impose a general memory or CPU quota.

This uses [Git's documented worktree mechanism](https://git-scm.com/docs/git-worktree.html)
and [Python's subprocess process-group facilities](https://docs.python.org/3/library/subprocess.html).
Optional orchestration frameworks have not been added: existing execution and
evidence infrastructure are sufficient for this bounded pilot.

## Hierarchy and actual demonstrations

The plan allocates **63 work packages and 345 source-qualified controlled items**.
The latter count distinguishes identical catalogue labels used by different
source files; it is not the earlier count of 283 distinct unqualified labels.
Every one of the 415 hierarchy nodes has an evaluator or a precise missing
capability request. Six package mappings have partial detailed adapters. Requests
specify the missing input/model and independent benchmark, adverse-case and
parent-integration acceptance needed before use.

| Pilot | Actual outcome and remaining scope |
| --- | --- |
| Connected mechanical frame | A heavier section passes selected section checks, but its connected frame fails a weld check; parent-level rejection is retained |
| 25 m civil beam and supports | A passing beam screen fails its footing-pressure screen; an enlarged footing is recomputed with its own added mass |
| Complete viaduct bay | Both support identities are retained, with explicit holds for support compatibility, transverse distribution, substructure reinforcement, settlement and construction stages |
| Software baseline | Boolean dimensions are accepted as numbers by the existing section routines; the independent fixture fails |
| Software repair | A strict numeric-type guard preserves valid section results, passes all 17 original mechanical regressions and the separate input/closed-form fixture, and enters an experimental baseline |
| Attractive software regression | Returning zero beam deflection is rejected by the original regression suite; an apparent improvement cannot bypass parent checks |

The software objective is a counted failure of the declared validation fixture,
with zero counting uncertainty. It is neither a population defect rate nor a
performance measurement. Its parent evidence covers the existing connected-frame
research regressions, not whole-vehicle or operational software qualification.
The repair is retained as a versioned experimental patch, rather than silently
replacing the original baseline used by the comparison.

The coupled iteration records a bounded, dimensionally scaled residual for
mechanical gross-steel transfer into the civil calculation. This demonstrates
one-way transfer consistency only. It does not establish two-way train–structure
interaction or convergence of a complete physical design.

Experimental promotion requires unchanged function, requirements and scenarios;
complete passing mandatory, independent and affected-parent checks; objective
improvement beyond declared uncertainty; and retained exact revision ancestry.
Any recorded adverse check vetoes promotion. Missing evidence produces named work
requests. Acceptance-policy, test or solver-assumption changes require a separate
review path. Acyclic item/revision graphs and bounded physical-feedback loops are
validated separately.

## Reproduce and inspect

```bash
tools/automation/osr-python tools/automation/hierarchical-design.py plan
tools/automation/osr-python tools/automation/hierarchical-design.py run \
  --output /tmp/osr-new-hierarchy --concurrency 2
tools/automation/osr-python tools/automation/hierarchical-design.py verify \
  --output /tmp/osr-new-hierarchy
tools/automation/osr-python tools/automation/design-iteration.py run \
  --output /tmp/osr-new-optimization --mode optimization --budget 64 --no-baseline
tools/automation/osr-python tools/automation/design-iteration.py run \
  --output /tmp/osr-recovered --resume /tmp/osr-interrupted --budget 64 --no-baseline
tools/automation/osr-python tools/automation/local-validation.py run \
  --profile hierarchical-design --output build/validation/hierarchy-example
```

Resume must retain the original mode and options, including `--mode optimization`
when applicable. An increased evaluation budget may extend the retained frontier;
changed sources or context require a fresh campaign. The software pilot is tied to
the actual Boolean-input defect; once its source changes, reauthor proposals
against the new exact baseline rather than replaying an obsolete patch.

The review shows changes, failed and unknown checks, affected parents, actual
tool artifacts, adoption decisions, ancestry and next actions. Repository-root
and docs-root browser matrices cover desktop and mobile layouts and fetch the
linked artifacts. Verification binds source membership, policy semantics,
interpreter identity, candidate/evidence identities, tool outcomes and every
sealed artifact. Archived verification preserves historical identities without
requiring the original absolute workspace paths to exist.

These demonstrations complete the seven initial implementation work packages
from the review. Expansion remains controlled by capability and qualification
requests: no additional agent can substitute for a missing physical evaluator,
accepted load/site/material basis, supplier configuration, issued drawing or
measured first article. The original LM3 envelope/stiffness conflict remains open.
