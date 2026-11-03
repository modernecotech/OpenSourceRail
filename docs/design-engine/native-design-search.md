# Rust generative design search

The reusable `osr-design-search` Rust kernel generates successor programs and
filters large Pareto pools. The coordinator materialises physical component
graphs, calculates nominal quantities and provisional manufacturing costs, then
runs bounded analytical and optional native axial refinements. The selected
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

Refinement considers all evaluated candidates, including those excluded by the
partial cost archive. It prioritises topology coverage and applicable axial
models rather than declaring a cheapest body structurally adequate. Up to twelve
candidates receive analytical assessments; at most three receive the fuller
DFMA/interface and immutable refinement packages.

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
seed/program coverage, parent evaluations and immutable Rust generation journals.
Distinct definitions sharing one physical geometry retain separate evaluations.
Cheap geometry/cost records are replay-checked; these cache hits are not claimed
as avoided expensive solver runtime. Price changes need not invalidate geometry
or a structurally unchanged solver request.

The checked reference run is
`92c04676449802aac05ff69b9b245cda9b60f8e3fc1d35fb700e79c05f4190f5`:

| Scope | Executed result |
|---|---:|
| Rust mutation programs | 2,000 |
| Physical designs and nominal-stock cost evaluations | 60 |
| Connectivity mutations | 5 spine and 5 cellular |
| Analytical assessments | 12 |
| Fuller DFMA/interface packages | 3 |
| New CalculiX axial jobs | 1 |
| Deferred programs | 1,976 |
| Full invocation wall time | 16.76 s |
| Peak command RSS | 279,908 KiB |

The native axial method was numerically verified, with a maximum model nodal
movement of 0.03035 m and a relative displacement difference of approximately
1.54e-7 against the independent analytical solution. These are conditional graph
results, not a whole-body deflection acceptance or physical railway validation.
Independent read-only verification reproduced all 31 source bindings, 60
geometries/costs, mutation load projections and three refinement packages without
another solver execution. Validation passed 118 tests on each of Python 3.12
and 3.13 (with the opt-in native control separately passing), 29 CI routing checks,
and `./osr verify`.

The original Rust performance benchmark remains useful for archive work:

| Dataset | Python reference | Explicit Rust bridge |
|---|---:|---:|
| 600 synthetic nondominated points | 1.312 s | 0.0189 s |
| Actual 18 civil candidates | 0.00065 s | 0.00624 s |
| Actual 54 body candidates | 0.00223 s | 0.00880 s |
| 100,000 synthetic points, three/four objectives | Not run | 2.06–2.53 s |

Small cases used one warmup and three measured repetitions. The bridge timing
includes normalization, hashing, receipt checks, process startup and validation.
The large-case Rust CLI alone took 0.269–0.492 s including parse/serialization;
that is not pure kernel time. No unmeasured Python speedup is inferred. Generating
10,000 gene programs took 0.050 s; those were not 10,000 physical evaluations.
The benchmark report SHA-256 is
`a81470a1fd0d42add06547416ca7cfa77724ac8ca7e4958b94416ce80be0c0d9`.

```bash
python tools/automation/benchmark-native-search.py --output build/my-search-benchmark
cargo test --locked -p osr-design-search
python -m pytest -q --import-mode=importlib engineering/design_search/tests/test_native_search.py engineering/design_search/tests/test_native_campaign.py engineering/design_search/tests/test_topology_mutation.py engineering/design_search/tests/test_search_archive.py engineering/design_search/tests/test_native_refinement.py
```

NumPy/SciPy and CalculiX retain their compiled numerical engines. Arbitrary organic
solids, full shell/joint/fatigue refinement, parallel solver scheduling, calibrated
surrogates, physics-adaptive parent allocation, whole-railway co-design and new
Workbench views remain explicit adapter/frontier work. Installed mass, propulsion,
braking, protected service and physical release remain unqualified.
