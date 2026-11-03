# Rust generative design search

The reusable `osr-design-search` Rust kernel generates successor programs and
filters large Pareto pools. The coordinator materialises physical component
graphs, calculates nominal quantities and provisional manufacturing costs, then
runs bounded analytical and optional native axial refinements. Analytical outcomes
now inform parent weights before each Rust generation. The selected
railway and its release status remain unchanged.

```bash
python -m engineering.design_search.native_search build
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python -m engineering.design_search.native_campaign --state build/my-native-search
```

Use the project Python environment and supported Rust toolchain. Building is
explicit and records locked sources, tools and the executable hash. Stale or
modified receipts are rejected. Generated requests, geometries, caches, failed
experiments and immutable solver packages remain under `build/`, outside Git.

The campaign starts with paired braced/unbraced controls for the eighteen
frame/shell/rib compositions: 36 physical seed designs. Nine genome axes vary
spacing, dimensions, bracing, roof integration and structural topology. These
are invocation domains for implemented materialisers, not the entire admissible
engineering design space or acceptance limits.

Two new topology productions change connectivity and actual counted stock:

- `add-longitudinal-spine`: centre nodes, longitudinal members and radial branches.
- `add-cellular-diaphragms`: bay-centre nodes and pyramidal branches between stations.

Each adds explicit RHS geometry, joints, typed ports, assembly operations and
mass/load projections while preserving accommodation, bogie supports and inherited
equipment accounts. The materialisation parent is distinct from the genetic
search parent; both identities are retained. Joint hardware, trimmed/intersecting
stock, installation and clearance evidence remain incomplete. Heavier first
mutations are experiments, not claimed improvements.

Each generation creates up to 1,000 programs. A NumPy stock proxy orders twelve
nominal-geometry/cost evaluations. The initial shortlist targets 50/30/20
exploitation/alternative/unconventional allocations where available and protects
observed topology choices from starvation. The proxy omits detailed ribs and
joints and is uncalibrated; it cannot establish physical quantities or compliance.
Actual geometry and cost are calculated after materialisation. Rust allocation
weights govern attempts; deduplication changes accepted proportions.

Automatic archive dispatch uses the unchanged Python reference at up to 64 rows
and Rust above that. The threshold is provisional and configurable through
`search_archive.archive`; the crossover depends on dominance and cell structure.
Both paths preserve physical IDs, fronts and valid exclusion witnesses. Large
batches stay bounded; persistent Rust workers remain future work.

Before each generation, the coordinator considers all evaluated candidates,
including those excluded by the partial cost archive. It adds up to twelve
analytical observations, prioritising topology coverage and applicable axial
models, and retains up to 64 observations across generations. Immutable feedback
snapshots bind each observation to its physical definition, stage-zero evaluation,
loads, model, sources and runtime. Resume reconstructs the assessments and Rust
parent requests before accepting a saved generation.

Every valid stage-zero design remains an eligible parent. Its positive integer
weight is one, plus one for a cell cost-front position, plus two for a supported
cell axial-front position, capped at four by default. Held and unassessed models
retain positive sampling opportunity; missing stiffness never becomes zero.
Weighted roulette does not guarantee a family quota in any finite generation.
Omitting Rust parent weights retains the previous equal-weight seeded sequence.

Axial archives compare candidates only within explicit material, structural-family,
topology and functional-load-policy cohorts. Each design carries its own stock
self-weight under the same provisional normal-service assumptions. These are not
equal-force tests or complete installed-load comparisons. The final refinement
uses the same cohorts. Separate `maximum_new_assessments` settings bound new
generation and final-stage work; final reports distinguish inherited, additional
and total assessments. At most three candidates receive the fuller DFMA/interface
and immutable refinement packages. Generation feedback dispatches no native jobs.

The assessments distinguish:

- A pin-graph mechanism, which holds that axial model only.
- A rigid axial graph with an independent linear stiffness solution.
- A prediction outside the existing 0.01 member displacement/length model domain,
  held before native dispatch.
- Separate shell-method admission and its missing material/connection evidence.

A pin/axial result neither rejects nor qualifies a bonded shell or rigid frame.
The small-displacement bound is a numerical model domain, not a vehicle acceptance
limit. Bending, buckling, fatigue, joints, fire and complete installed quantities
remain separate requirements.

To permit a new coarse axial CalculiX job:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python -m engineering.design_search.native_campaign --state build/my-native-search --native-jobs 1
```

The default native budget is zero: analytical work only, with no implicit native
receipt adoption. The solver limit is zero to three new jobs per invocation.
Exact existing permitted packages may be verified and reused; new dispatches and
native evidence reuse have separate counters. Requests bind candidate/definition,
graph, loads, source hashes, Python/NumPy runtime, CalculiX binary, subdivisions,
threads, timeout and requested/effective memory limits. The default child solver
limit is 30 seconds and 1 GiB. Verification regenerates the deck and compares
retained native results with the independent analytical reference without running
the solver. Missing tools, interrupted jobs and model-domain holds remain explicit.
This adapter does not dispatch a continuum whole-body shell solve.

Reusing a state resumes queued work and then retained deferred programs:

```bash
python -m engineering.design_search.native_campaign --state build/my-native-search --evaluations 12
python -m engineering.design_search.native_campaign --state build/my-native-search --generations 3 --evaluations 24
```

Initial seeds are separate from the successor-evaluation budget. A nonblocking
advisory lock permits one coordinator per state. Its wall-time budget is
cooperative between tasks, not an OS sandbox. Checkpoints preserve complete unique
seed/program coverage, parent evaluations, feedback snapshots and immutable Rust
generation journals.
Distinct definitions sharing one physical geometry retain separate evaluations.
Cheap geometry/cost records are replay-checked; these cache hits are not claimed
as avoided expensive solver runtime. Price changes need not invalidate geometry
or a structurally unchanged solver request.

The analytical adapter now validates and assembles each graph once, reusing that
prepared system for its rigidity diagnostic, linear solve and stock basis. The
original `grammar_structure` implementation stays unchanged as an independent
oracle. NumPy's compiled SVD and linear solver remain in use; the measured problem
was repeated copying and validation, rather than slow numerical kernels.

A bounded invocation cache keeps only freshly computed analytical observations:
up to 64 records and 16 MiB. It retains neither full body geometries nor prepared
matrices. Keys bind the materialisation inputs, candidate, definition and parent
evaluation; guards check current sources and numerical runtime before and after
reuse. Every invocation starts empty. Resuming reconstructs every unique retained
observation once before sharing it across replayed snapshots; persisted evidence
never seeds the cache. Finalists still receive their independent refinement checks.
`--no-invocation-reuse` enables recomputation under a separate campaign contract.

The reproducible benchmark alternates two runs per policy, with exact equality
checks on all candidate/cost evaluations, Rust requests and proposals, feedback,
analytical results and deferred programs. On the measured local workload:

| Measurement | Recompute | Reuse |
|---|---:|---:|
| One braced-body diagnostic/reference/stock median, three repetitions | 0.03375 s (original oracle) | 0.01459 s (prepared adapter) |
| Full 2,000-program campaign median, two repetitions per policy | 17.84 s | 16.35 s |
| Retained analytical records in reuse runs | — | 29, about 1.34 MB |
| Analytical reuse hits | 0 | 12 |

The campaign timing compares the prepared adapter with invocation reuse disabled
and enabled: 8.35% less wall time in this small local sample. Each run evaluated
60 definitions representing 57 physical designs and 29 analytical assessments,
with no native engineering job. This is not high-fidelity solver throughput.
The initial full-geometry cache trial was slower and was removed. The partial
cProfile experiment was interrupted and is not a completed campaign benchmark.
The final benchmark ID is
`db89b84a265efd75e3ab284e5c15f5f01a911db20d5ce643c17b83eee9637e4c`,
with report SHA-256
`afa8da7c28b6de49be774104d2f46eeccbee645a29c158e59417efcda8ed3892`.
Outputs remain private reproducible artifacts under `build/`.

Independent verification reproduced all four comparison payloads and checked all
35 source bindings. A zero-new-evaluation resume preserved 60 attempts, both
generation journals and 1,976 deferred programs; it freshly computed 29 analytical
records and reused twelve within the invocation, with no native dispatch. Its ID
is `74d999f07ce9b5d4de838a850c99ff7cff23b7d5a50aa5d25ae8caa3df7ea4d3`.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python tools/automation/benchmark-campaign-reuse.py --output build/my-campaign-benchmark --samples 2
```

The earlier source-pinned feedback reference run is
`c2da549729de610e369db2bdc5014e04e52b424157600365bdc2265a7c7ba424`:

| Scope | Executed result |
|---|---:|
| Rust mutation programs | 2,000 |
| Definitions with nominal-stock cost evaluations | 60 |
| Distinct physical designs | 57 |
| Connectivity-mutation evaluations | 7 spine and 3 cellular |
| Generation feedback snapshots | 2 |
| Accumulated generation observations | 12, then 24 |
| Final analytical assessments | 24 inherited + 5 additional |
| Fuller DFMA/interface packages | 3 |
| New CalculiX axial jobs | 1 |
| Deferred programs | 1,976 |
| Full invocation wall time | 22.11 s |
| Peak command RSS | 280,088 KiB |

Generation one assigned weights 1/2/3 to 11/18/7 parents; generation two assigned
them to 19/20/9 parents. Seven then nine axial observations supported that model's
domain. No candidate received physical or engineering acceptance. Native axial
agreement is a conditional graph-method result, not whole-body validation.
Resuming for three evaluations preserved both generations and all 60 prior
attempts, reduced deferred programs from 1,976 to 1,973, and dispatched no new
native job. Its run ID is
`e5049953cd2d69ba703d183c282f0b32f58df4e74070553bb318e3aef02be98d`.

Independent read-only verification checked all 32 source hashes, regenerated both
feedback snapshots and weighted Rust journals, and verified the three refinement
packages without another solver execution. The native axial result retained
0.0303485 m maximum nodal movement, 7.58e-8 force residual and 7.61e-9 energy
residual. Verification ran under a 1 GiB address-space limit with one numerical
thread; native dispatch was disabled by a throwing replacement, not an OS sandbox.
Current regression checks passed 176 tests on each of Python 3.12 and 3.13, with
the opt-in native axial control separately passing. The unchanged Rust kernel
retains its 15 tests in CI; 29 CI routing tests (101 subtests) passed. `./osr verify` replayed the
current selected publication successfully without regenerating its packets. The
opt-in native control remains a separate CI job.

The refreshed Rust performance benchmark measures archive work:

| Dataset | Python reference | Explicit Rust bridge |
|---|---:|---:|
| 600 synthetic nondominated points | 1.327 s | 0.0191 s |
| Actual 18 civil candidates | 0.00063 s | 0.00709 s |
| Actual 54 body candidates | 0.00200 s | 0.00882 s |
| 100,000 synthetic points, three/four objectives | Not run | 2.12–2.57 s |

Small cases used one warmup and three measured repetitions. The bridge timing
includes normalization, hashing, receipt checks, process startup and validation.
The large-case Rust CLI alone took 0.255–0.533 s including parse/serialization;
that is not pure kernel time. No unmeasured Python speedup is inferred. Generating
10,000 gene programs took 0.061 s; those were not 10,000 physical evaluations.
The benchmark report SHA-256 is
`9e317c4f65dec11b26a33cb9e6224921b3bba57849bb3183fefc0f0662afee24`.

```bash
python tools/automation/benchmark-native-search.py --output build/my-search-benchmark
cargo test --locked -p osr-design-search
python -m pytest -q --import-mode=importlib engineering/design_search/tests/test_native_search.py engineering/design_search/tests/test_native_campaign.py engineering/design_search/tests/test_topology_mutation.py engineering/design_search/tests/test_search_archive.py engineering/design_search/tests/test_native_refinement.py engineering/design_search/tests/test_search_feedback.py engineering/design_search/tests/test_axial_analysis.py engineering/design_search/tests/test_invocation_cache.py
```

NumPy/SciPy and CalculiX retain their compiled numerical engines. Arbitrary organic
solids, full shell/joint/fatigue refinement, parallel solver scheduling, calibrated
surrogates, native/full-shell feedback, whole-railway co-design and new
Workbench views remain explicit adapter/frontier work. Installed mass, propulsion,
braking, protected service and physical release remain unqualified.
