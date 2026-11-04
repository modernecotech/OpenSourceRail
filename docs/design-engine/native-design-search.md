# Rust generative design search

The reusable `osr-design-search` Rust kernel generates successor programs and
filters large Pareto pools. The coordinator materialises physical component
graphs, calculates nominal quantities and provisional manufacturing costs, then
runs bounded axial and coarse three-dimensional frame refinements. Supported axial
outcomes inform parent weights before each Rust generation; coarse frame results
are retained as separate exploratory evidence. The selected
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

An optional direct PyO3 encoder now moves canonical traversal, key ordering,
ASCII escaping and SHA256 into Rust modules in the existing search crate.
Python remains the coordinator and the unchanged shared encoder remains the
reference/default. Float representation and arbitrary-size integer formatting
deliberately use CPython built-ins; this is a hybrid implementation, not an
independent Rust float-formatting algorithm. NumPy/SciPy and the specialist
solver/CAD adapters retain their existing native calculation engines.

The compatibility contract is the exact output of
`json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False,
ensure_ascii=True) + '\n'`, encoded as ASCII-compatible UTF-8, and SHA256 of
those bytes. Its native domain is exact built-in `None`, `bool`, `int`, finite
`float`, `str`, `list`, `tuple` and string-keyed `dict` objects. Mapping keys sort
by Python Unicode codepoints; there is no Unicode normalisation. Escapes include
controls, DEL, non-ASCII characters, non-BMP surrogate pairs and lone surrogates.
Integer precision, negative floating-point zero, exponent formatting, tuple/list
wire equivalence and the final newline retain their existing meanings. Circular
containers, unknown/subclass objects, non-string keys and nonfinite numbers are
rejected in native mode. The broader shared Python domain remains available;
there is no silent native coercion or fallback. Output defaults to a 64 MiB
limit and depth 128 (maximum 256); these are output/depth limits, not a claim of
fixed input memory or operating-system isolation.

```bash
python -m engineering.design_search.native_search build
python -m engineering.design_search.native_canonical build
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python -m engineering.design_search.native_campaign --state build/my-native-encoding \
    --canonical-backend rust
```

The [PyO3 0.27.2 manual extension build](https://pyo3.rs/v0.27.2/building-and-distribution.html)
is an optional, locked dependency path. Ordinary Cargo builds do not link
Python. Each extension build records source hashes, compiler tools, exact CPython
ABI/executable and binary digest; there is no implicit build. Guarded sessions
check that context before/after use instead of hashing files for every object.
Sessions close explicitly; aliases restore on exceptions, and other execution
contexts keep the Python reference. Encoder provenance changes the evaluation
contract while physical identities and engineering results remain unchanged.
The same `--canonical-backend rust` option is available on `search_delivery run`.

Parity covers 10,000 distinct retained-record representatives from 300 files,
50,016 float controls, Unicode/alias cases and two larger complete records on
both Python 3.12 and 3.13. One development control exposed an incorrect DEL
escape; the defect and its failed trial were retained before correction.
Four complete 2,000-program campaigns preserve all 60 canonical geometry records,
cost/quantity evaluations, finalists, numerical results/holds, archive witnesses
and ancestry/deferred reasons. In the uninstrumented pair, Python took 13.6165 s
and Rust 12.2856 s (9.77% less wall time), with peak RSS 310,260/310,312 KiB.
This is one local pair, not a universal speedup. The sampled profiles still place
geometry materialisation around 5.96/5.22 s and source checks around 1.07/1.09 s;
compiled SVD/solve/eigenvalue work totals about 0.16/0.17 s. Sampled canonical
timings are inclusive estimates and must not be added to these phases.
Comparison SHA-256:
`292d59352092ad7227e329ea63a499d5b7116bda183571ee19aa95d488078e89`.

The Rust-backed delivery package
`3467a18eba7cf3c389724df318aa51be3025ba7fb3776b8665b5f4a000e69b38`
reuses the exact native geometry with zero new CAD jobs. All twelve engineering
stage payloads match the preceding Python-backed reference byte-for-byte.
Independent read-only replay checked the source/ABI/binary receipt, 199 routes,
14 cost scopes, shifts, identities and unchanged physical holds; it took 10.11 s
and 505,636 KiB peak RSS under a 1 GiB limit. Its audit SHA-256 is
`df402655937e058fadda8bca0724ddbec9385dd6f83308f635b01468044e2846`.

The later `998c0136` native-methods CI failure was a rustup installation conflict
before compilation; the earlier green run had skipped those native jobs. The job
now installs/checks Rust 1.92 in fresh runner directories before the unchanged
five-crate control command. All 158 control tests passed locally. The current
dossier was regenerated with its pinned environment after the workflow/lockfile
changes; selected identities, numerical requests/results and physical holds are
unchanged. Dedicated Python 3.12/3.13 CI jobs build the optional encoder explicitly
and require its parity/campaign checks instead of skipping missing extensions.

The search can now feed one finalist directly into a complete declared railway
delivery study, using the existing canonical P1 research bundle and domain
evaluators rather than running the separate 112-bundle campaign again:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python -m engineering.design_search.search_delivery run \
    --search-state build/my-search --output build/my-delivery --native-cad
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python -m engineering.design_search.search_delivery verify build/my-delivery --replay
```

Use the same project Python environment for generation and verification. Runtime
changes create distinct search/cache contexts. Without `--body-candidate-id`, the
handoff chooses the lowest partial factory-cost member of the frame-assessed
finalist set for demonstration only; this is not an integrated design selection.
The package preserves source-program genes in their declared axis order, primary
cost evidence and search-result identity. It reconstructs the physical body and
primary quantities/cost during verification. Replaying the full parent-selection
sequence additionally requires the retained search journals.

Twelve same-candidate records cover stock geometry/mass properties, inventory,
interfaces, axial/coarse-frame structure, architecture, required propulsion,
supported-motion admission, assumption-only journeys, civil alternatives,
14-scope whole-life economics, delivery and work plans. Structural load mass is
checked against the bundle. Located stock has one provisional manufacturing
route per occurrence. Factory/civil plans retain two shifts; operations retain
two/two/three-shift low/base/high cases. Disabled ERPNext Item/BOM/Routing/
Workstation/Project and Frappe workforce/shift drafts retain their cost links,
assembly precedence, staffing assumptions and import holds. No orders, external
transactions, control commands or movement authority are created.

`--native-cad` explicitly permits one FreeCAD export, including saved CAD/STEP
reopening checks, and an IFC export/reopening. Exact planar box/RHS facets retain
the hollow bore, positions, bundle identities and native stock-volume correlation.
These are one car's nominal stock solids, not an installed six-car train or
fabricated joints/equipment. The CAD child timeout is 180 seconds; IFC has a
60-second cooperative budget. A 4 GiB free-disk preflight precedes work. Without
this option, geometry export is explicitly not requested. Alternatively,
`--reuse-geometry build/earlier-delivery/geometry-export` verifies and copies exact
same-body/bundle/source/tool geometry evidence with zero new CAD jobs. It cannot
be combined with a new CAD budget. Verification reopens IFC and checks saved
original CAD receipts/hashes without another FreeCAD/STEP process.

The complete reference package is
`b07377c204f6ce42bb0e5fad89f532537260ddee1c0b09a2baccbcce1930e3fe`,
under `build/search-delivery-complete-reference-20261104/`: body `883ce3f…`
from the 2,000-program, 59-physical-design campaign propagates into canonical
railway `4907f76f…`, three civil alternatives, 199 located-stock routes and all
14 cost scopes. Twelve compressed stage records plus CAD/STEP/IFC occupy
4,707,697 bytes; the index holds identities instead of duplicating the records.
The final structural consolidation reused the existing native geometry package.
Its independent full replay took 9.96 seconds and 509,144 KiB peak RSS under a
1 GiB address-space limit, with search/CAD/IFC exports blocked. The recorded
frame/bundle sprung-mass difference was 1.82e-12 kg. Audit SHA-256:
`9302ee5b7a289db350e0c9cb1032ec2d0ec2719ea398aba3e660d2fba20be499`.

`computational_workflow_complete` means every declared stage has a result or an
explicit infeasibility/evidence hold. Low/base assumed journeys stop within the
berth hypothesis at 170.40/153.25 seconds; the high case retains its controller
speed-limit failure. Supported motion remains unrun without a valid available
force map. Large-motion/short-member structural holds, complete installed mass,
clearances, actual production capacity, site conditions and physical qualification
remain open. Computational completion grants no engineering or operating release.

The campaign starts with paired braced/unbraced controls for the eighteen
frame/shell/rib compositions: 36 physical seed designs. Nine genome axes vary
spacing, dimensions, bracing, roof integration and structural topology. These
are invocation domains for implemented materialisers, not the entire admissible
engineering design space or acceptance limits.

Registered topology productions change connectivity and actual counted stock:

- `add-longitudinal-spine`: centre nodes, longitudinal members and radial branches.
- `add-cellular-diaphragms`: bay-centre nodes and pyramidal branches between stations.
- `remove-alternate-crossframe-bracing`: remove alternate interior diagonals from
  an already braced parent, protecting end and bogie-support stations.

The additive productions introduce explicit RHS geometry, joints, typed ports, assembly operations and
mass/load projections while preserving accommodation, bogie supports and inherited
equipment accounts. The materialisation parent is distinct from the genetic
search parent; both identities are retained. Joint hardware, trimmed/intersecting
stock, installation and clearance evidence remain incomplete. Heavier first
mutations are experiments, not claimed improvements.

Member removal retires the corresponding stock, component occurrences and end
connections, updates remaining joins/assembly and recalculates own-candidate
gravity loads. Removed stock is not copied into an inherited allowance. It
requires declared existing bracing; ineligible programs remain in the immutable
deferred journal with their definition hold. Full projection reconstruction
rejects resealed accounting, assembly or ancestry changes.

For the default braced control, six removed members reduce gross body stock by
118.583 kg (161 to 155 members) and the scoped body-stock factory estimate by
IQD 4.44 million. Nodes, supports, passenger interfaces and inherited equipment
are unchanged. Pin mechanisms remain zero. Own-load frame displacement falls
26.769 to 26.491 mm, but equal-load-normalised compliance increases 0.0559%.
This does not demonstrate greater stiffness or complete installed savings; the
short-member/shear and joint holds remain. The independent paired-audit SHA is
`4e49b9cccefa2bf591ffd229062895292b15cf09e678828457487be09c148ea4`.

Each generation creates up to 1,000 programs. A NumPy stock proxy orders twelve
nominal-geometry/cost evaluations. The initial shortlist targets 50/30/20
exploitation/alternative/unconventional allocations where available and protects
observed topology choices from starvation. Within the existing twelve-evaluation
budget, the default shortlist also protects all eight topology/material-family
cells where eligible proposals exist. This retains both aluminium and GFRP
experiments rather than letting the light-stock proxy favour only one material.
The proxy omits detailed ribs and
joints and is uncalibrated; it cannot establish physical quantities or compliance.
Actual geometry and cost are calculated after materialisation. Rust allocation
weights govern attempts; deduplication changes accepted proportions.

Automatic archive dispatch uses the unchanged Python reference at up to 64 rows
and Rust above that. The threshold is provisional and configurable through
`search_archive.archive`; the crossover depends on dominance and cell structure.
Both paths preserve physical IDs, fronts and valid exclusion witnesses. Large
batches stay bounded; persistent Rust workers remain future work.

Processor work now avoids checkpoint deep copies and repeated canonical JSON
traversals. Top-level fragments still use the authoritative encoder; inserted
identity hashes and final bytes match the independent full-record encoder,
including floating-point, Unicode and alias cases. Geometry gzip uses level one
with identical decompressed records. In one measured full-call pair, fresh
campaign time fell from 19.943 to 17.959 seconds (9.95%); resume remained about
16.3 seconds. Peak cumulative RSS changed from 306,124/308,016 to
309,152/315,040 KiB. Compression
trades 1.46 MB more cache storage (4.64 to 6.10 MB for 60 records) for less CPU.
These are single-sample local timings, not a high-fidelity solver speed claim.

The read-only comparator verifies 17 physical, cost, ancestry, archive, numerical
and disposition checks. It selects the exact definition/runtime cohorts from the
retained runs, excluding unrelated later contexts in the shared cache. Report
SHA-256: `5cf1fbaaeda184e5740600b18d1ae2b4f1ef1a84b4e74d9ba4de24791b75bb70`.

```bash
python tools/automation/benchmark-campaign-serialization.py \
  --directory build/processor-profile-20261104 --output build/my-serialization-audit.json
```

Disk checks use filesystem free-space counters; directory sizes alone do not
establish reclaimable bytes on a reflink/snapshot filesystem. Four superseded
coupled-campaign trees were retained as compressed restorable archives and every
file's content, path and metadata checked twice before retiring the originals.
Available home space increased from about 26 to 35 GB during this work. Current
publications and numerical evidence remain preserved. The local cleanup script
supports `--disk-status --path /home/hayder --report FRESH_JSON`; its report is
read-only. New delivery packages keep compressed records once and compact indexes.

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

Up to three finalists now also receive a six-DOF Euler–Bernoulli frame evaluation
through NumPy's compiled numerical engine. It includes axial deformation, bending
about both section axes and approximate closed thin-wall torsion. The model covers
one car's underfloor RHS centroid members; other body and equipment stock contributes
load without shell stiffness. Exact translational supports and normal-force vectors
are retained, with a force/mass residual; rotational supports are not invented.

Rigid moment continuity, section roll and an aluminium Poisson ratio of 0.33 are
explicit evaluation hypotheses. The physical pin/clevis interfaces remain in the
candidate. GFRP axial modulus alone cannot supply the required shear/orthotropic
law and produces a model hold. Short-member/shear applicability, large motion,
thin-wall torsion and numerical residuals retain separate domain holds. Solved
frames neither invalidate a pin mechanism nor establish a qualified body. Frame
results do not affect parent weights or integrated selection.

Frame requests first cover observed topologies, preferring an implemented
research material route within each topology. Pin-model failure cannot block a
separate rigid-frame experiment. Unrequested candidates remain in the frame
frontier; unavailable composite laws remain explicit holds.

`--frame-native-jobs 1` requests a separate bounded native comparison budget;
its default is zero, independent of `--native-jobs`. A model-domain hold prevents
dispatch. The optional CalculiX B32R/BOX adapter preserves the hollow section,
local orientation, source/runtime/tool identity, effective 1 GiB/30-second limits,
failed/interrupted attempts and exact model/deck/payload receipts. Read-only
verification regenerates the deck and reanalyses saved outputs without solving.
These are local integrity checks, not authenticated physical measurements.

The hollow-section bending control under the documented
[CalculiX beam formulation](https://www.dhondt.de/ccx_2.23.pdf) differs from the
analytical beam by about 1.04%. Expanded `OUTPUT=3D` displacement fields now
support a labelled end-twist fit for one straight member; full-frame rotations
and reaction moments remain unavailable. Essentially zero centreline translation
cannot verify torsion.

Four bounded torsion controls varied mesh (8/16 elements), length (3/6 m) and wall
(4/2 mm). Energy disagreement with Bredt persists at 21.86–22.30%, while the
8-to-16-element native energy changes only 0.0457%. Baseline expanded-section
twist is about 1.83646e-5 rad versus 1.83692e-5 rad from torque–energy work and
2.35194e-5 rad from Bredt. The manual's restricted BOX warping is a supported
diagnostic hypothesis; a fitted torsion constant is not substituted. Cross-section
model calibration remains open, with no tolerance or physical gate relaxed.
Study SHA-256:
`c405942d35df0b2e22f1f7a4497af35ad768f4f5e584250a7e918b7f79381f6b`;
diagnosis SHA-256:
`e08478cb0b375f9add21209cb25b8c16d732c883e149f1deb6d382f879a83e36`.

An actual-wall Saint-Venant section evaluator now solves the scalar warping
problem on conforming triangular meshes, retaining the hollow interior and free
outer/inner boundaries. Only the additive warping gauge is fixed. Vectorised
NumPy assembly and SciPy's compiled sparse solver handle the numerical work;
Rust remains the high-throughput search kernel. Independent rectangle-series,
gauge, symmetry, scaling, area/inertia and hollow-topology controls accompany
the implementation. This is a sharp-corner, uniform-wall geometry model, with
no assumed joint, material-lot or body qualification.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python -m engineering.design_search.native_campaign --state build/my-section-search --section-torsion-jobs 1
```

This separate opt-in budget permits zero to three new section workers; the
default is zero. Each child has effective limits of at most 1 GiB, 30 CPU/wall
seconds and one numerical thread. Four nested meshes use 1/2/4/8 elements through
each wall, bounded before allocation to 25,000 nodes and 50,000 triangles.
The declared numerical rule requires positive torsion below polar inertia,
equation/energy residuals at most 1e-8, nonincreasing nested energies and at most
1% final successive-mesh change. That rule is not a certified error bound.
Failed, interrupted and nonconverged studies remain holds with no selected J.

Requests bind geometry, producer sources, Python/NumPy/SciPy/SuperLU identities,
thread context, resources and numerical policy. Cached fields are replayed by
rebuilding the mesh and equations, without solving or launching a child. Only
verified converged fields can supply a separately identified frame hypothesis.
It preserves the physical candidate, E/nu, bending inertias, joints, roll,
supports and loads. Short-member/shear and large-motion holds remain; section
refinement grants neither native frame admission nor parent-selection rewards.
Resource limits provide no filesystem sandbox.

Seven independent actual-wall C3D20R/C3D20 solid controls examined the earlier
torsion discrepancy. Full integration changed the long polar-loaded control by
only 0.103%, leaving substantial interior-gradient variation. A distinct,
geometry-normalised closed-wall shear-flow load reduced that variation from
13.10% to 2.124% and produced J = 4.962688e-6 m4, 0.673% above the independent
2D value of 4.929530e-6 m4 for the 80 × 160 × 4 mm section. This supports
load-introduction contamination as a diagnosis of the solid controls; it does
not calibrate the BOX model or establish convergence of the new loading case.
All solid calibration flags remain false. Final held-disposition SHA-256:
`46d9aef3d4d9fdb467f727ed210b9460576c6f0fcfc040655c642f01997fbc97`.
The wall-flow study SHA-256 is
`a7ff41ca89bf02897f71cabbdc5be394002ba5d1372709aaad21e51a9678609b`;
raw immutable controls and retained producer epochs are under
`build/solid-torsion-controls-20261104/`.

The current section-refinement reference run is
`3bcb055e9dccc04a68c31e69c22e0d28d415c86ec977a33d84c59165965b6168`:
2,000 programs, 60 evaluated definitions/59 physical designs, 34 axial assessments
and three novel aluminium frame evaluations (cellular, spine and removal).
Each generation's twelve evaluations cover all eight eligible topology/material
cells. All 162 unbraced removal proposals remain deferred. The three frames retain
small-displacement and short-member/shear holds. One new section worker serves
all three frames, with two replayed reuses and zero CalculiX campaign dispatches.
For their 100 × 180 × 2 mm section, refined J = 4.440309e-6 m4 versus Bredt's
4.410045e-6 m4; last mesh change is 0.0415%. Maximum displacements change by
less than 0.01%, without resolving those holds. Full invocation wall time was
23.46 s, peak command RSS 309,096 KiB, measured alongside regression checks;
this is workload evidence, not a speedup comparison.

A zero-new-evaluation resume preserved candidate, generation, cost, model and
numerical payloads, replayed all three section uses and dispatched no new solver.
Throwing replacements blocked section children and sparse solves during that
audit. Resume-audit SHA-256:
`25d9c50ad0f9cd8e3eef4662c19973ecf3bf2ca13af58b0e0f95d1d8e94ff981`.
An independent read-only audit checked all three frame replays, the four saved
section fields, unchanged physical/load/material models and source bindings;
SHA-256: `80586204cf92d5b50322d2e3eceaecdaf9934e2e4fbe3e6bba09c9c14f722431`.

The source-pinned lightweight phase profile before member removal produced run
`ce32143bc9b1d76d0b3745f87c90cfabc2c41e5e8fbb385e6fd2bf14b184d2bb`:
2,000 programs, 60 evaluated definitions representing 57 physical designs,
29 axial assessments and three coarse frame assessments, with zero native jobs.
All three frames balanced forces and energy but remained held for short-member
applicability. Instrumented full-call time was 16.82 s, with 280,372 KiB peak RSS.

| Profile phase | Calls | Inclusive wall time |
|---|---:|---:|
| Geometry materialisation | 92 | 5.91 s |
| Canonical identities | 40,823 | 7.23 s |
| Canonical JSON encoding | 41,065 | 8.58 s |
| Campaign source checks | 149 | 0.94 s |
| Axial and frame matrix assembly | 35 + 3 | 0.24 + 0.086 s |
| Compiled SVD / linear solve / frame rank check | 35 / 34 / 3 | 0.181 / 0.011 / 0.011 s |
| Rust process and tool communication | 4 | 0.044 s |

These phase measurements overlap and must not be added. They are instrumented
timings for this workload, not uninstrumented throughput or a general solver
performance claim. The completed profile SHA-256 is
`20442744bc90d6e4e7a638c118b9ca1f96b9cdb9ef3bd73d9be2cc9c1ea4e148`.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python tools/automation/profile-design-campaign.py --output build/my-phase-profile
```

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
The full regression run passed 468 tests on each of Python 3.12 and 3.13,
including the native backend and entrypoint contracts. The added legacy Unicode
compatibility control also passed separately on both versions, with
the opt-in native bending control separately passing and both native controls
required in CI. The unchanged search kernel retains its 15 Rust tests, with
three new canonical-core controls; 36 CI routing tests passed. `./osr verify` replayed the
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
python -m pytest -q --import-mode=importlib engineering/design_search/tests/test_native_search.py engineering/design_search/tests/test_native_campaign.py engineering/design_search/tests/test_topology_mutation.py engineering/design_search/tests/test_topology_revision.py engineering/design_search/tests/test_search_archive.py engineering/design_search/tests/test_native_refinement.py engineering/design_search/tests/test_search_feedback.py engineering/design_search/tests/test_axial_analysis.py engineering/design_search/tests/test_invocation_cache.py engineering/design_search/tests/test_frame_analysis.py engineering/design_search/tests/test_frame_refinement.py engineering/design_search/tests/test_frame_native.py
```

NumPy/SciPy and CalculiX retain their compiled numerical engines. Arbitrary organic
solids, full shell/joint/fatigue refinement, parallel solver scheduling, calibrated
surrogates, native/full-shell feedback, whole-railway co-design and new
Workbench views remain explicit adapter/frontier work. Installed mass, propulsion,
braking, protected service and physical release remain unqualified.
