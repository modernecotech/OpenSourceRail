# Rust generative design search

The reusable `osr-design-search` Rust library and executable provide deterministic
successor generation and compact Pareto filtering. The Python coordinator connects
them to the existing physical component grammar, material quantities and Class C
manufacturing estimates. This is an additional research search path; it does not
change the selected railway or replace source-bound engineering publications.

```bash
python -m engineering.design_search.native_search build
python -m engineering.design_search.native_campaign --state build/my-native-search
```

Use the project Python environment and the workspace's supported Rust toolchain.
Building is explicit, uses the locked dependencies and records sources, Cargo and
Rustc versions, command and binary hash. A stale or modified receipt/binary is
rejected. Runtime artifacts stay under `build/`, outside Git.

The default campaign starts with eighteen existing frame/shell/rib compositions.
Rust generates new mutation programs across eight dimensional/production axes.
The coordinator materialises actual members, stock and component graphs; it does
not assign a physical candidate identity to an unexecuted gene program.

Each generation applies this bounded progression:

1. Generate up to 1,000 unique mutation programs, with parent identities.
2. Use NumPy to calculate an inexpensive, explicitly uncalibrated stock proxy.
3. Allocate twelve nominal-geometry/cost evaluations across exploitation,
   alternative families and unconventional combinations, using a 50/30/20 target
   where the categories have enough proposals.
4. Feed the exact partial metrics back into the Rust diversity/Pareto archive.
5. Apply existing DFMA/interface checks to at most three experimental finalists.

The Rust generator's weights govern **attempts**. Deduplication can substantially
change its accepted proportions; the coordinator separately apportions each new
generation's initial evaluation shortlist. A proxy's low score is an experiment-ordering
heuristic. It does not establish actual mass, price, stiffness, compatibility or
engineering feasibility. No high-fidelity solver is dispatched by this adapter.

The checked reference run generated 2,000 programs, performed 42 nominal-stock
evaluations and retained 39 distinct physical body designs, including 21 designs
beyond the eighteen seeds. Three received DFMA/interface checks; 1,976 programs
remained deferred. Full invocation wall time was 7.35 s, including imports, with
281,500 KiB peak RSS. Its run ID is
`5a9a93fa643b246adf0732dd752838125ea98e7f9be89be723537edbb0bf396d`.
A repeated invocation evaluated three deferred programs and reduced that frontier
to 1,973 without generating another batch, under run
`c855325d20a9e5afd2f760dceaf3f08a50f0e2bb1a12b4687d35a43ee1bdd817`.
These bounded counts do not establish
an optimised train, structural feasibility or whole-system savings.

Reusing the same state resumes unfinished queued work and, once the requested
generations exist, advances retained deferred programs. For example:

```bash
python -m engineering.design_search.native_campaign --state build/my-native-search --evaluations 12
python -m engineering.design_search.native_campaign --state build/my-native-search --generations 3 --evaluations 24
```

`--evaluations` limits new successor evaluations in that invocation; initial seeds
are separate. The wall-time budget is cooperative, checked between tasks, and
does not provide an OS sandbox. A nonblocking advisory lock permits one coordinator
per state directory; overlapping invocations are rejected. Generated requests, attempts,
failed definitions and deferred work are retained. Large records are rejected
before replacing a checkpoint that the bounded reader could not reopen.

Physical, definition, evaluation and proposal identities remain distinct. An
inactive parameter can yield identical physical geometry with a different
definition: all those evaluations remain linked, and the archive retains its
first exact definition/gene context. Parent evaluation IDs and variable/requirement
contexts accompany successors. Resumption checks the immutable journals against
replayed Rust requests and checks cheap geometry/cost records against their
materialisers. Unknown installed quantities are never substituted with zero.

The cache is partitioned by geometry and cost dependencies. Price changes need
not invalidate geometry; evaluator/runtime changes invalidate their own context.
Cheap cached records are replay-checked for integrity, so cache hits here are not
claimed as avoided expensive simulation time. The existing independent numerical
evaluators retain their own exact source/tool/load/mesh/resource contracts.

Benchmarks on 3 November 2026 used one warmup and three measured repetitions for
small cases. The Rust bridge measurement includes Python normalization, hashing,
receipt checks, process startup and result validation:

| Dataset | Python archive | Rust bridge | Interpretation |
|---|---:|---:|---|
| 600 synthetic nondominated points | 1.312 s | 0.0189 s | About 70× faster in this bounded case |
| Actual 18 civil candidates | 0.00065 s | 0.00624 s | Python remains faster for this small archive |
| Actual 54 body candidates | 0.00223 s | 0.00880 s | Python remains faster for this small archive |
| 100,000 synthetic points, three/four objectives | Not run | 2.06–2.53 s | No unmeasured Python speedup claimed |

All measured small fronts matched the independent Python algorithm. The Rust CLI
alone took 0.269–0.492 s on the large cases, including parsing and serialization;
that is not a pure kernel timing. Generating 10,000 gene programs took 0.050 s;
these were not 10,000 physical geometries or solver evaluations. The compact
archive records one valid exclusion witness instead of a potentially quadratic
list of every dominator. The original Python archive remains unchanged.

Reproduce the performance checks with:

```bash
python tools/automation/benchmark-native-search.py --output build/my-search-benchmark
cargo test --locked -p osr-design-search
python -m pytest -q --import-mode=importlib engineering/design_search/tests/test_native_search.py engineering/design_search/tests/test_native_campaign.py
```

The reference benchmark report has SHA-256
`a81470a1fd0d42add06547416ca7cfa77724ac8ca7e4958b94416ce80be0c0d9`.
Validation passed 11 Rust kernel tests, 45 Python bridge/campaign tests on each of
Python 3.12 and 3.13, the full Rust workspace tests, 80 demonstrator regressions,
and `./osr verify`. The reference run and resume were independently checked for
source, proposal, evaluation, lineage and complete frontier consistency.
These measurements concern search and record processing, not railway physics.
NumPy/SciPy already call compiled numerical routines; FreeCAD, CalculiX, Gmsh and
GetDP remain native engineering backends. Rewriting their Python invocation layer
would not replace the numerical engine.

This first adapter explores the existing structural productions with new
parameters and graph choices. It does not yet implement arbitrary 3D organic
solids, trained Bayesian surrogates, distributed solver scheduling or automatic
whole-railway co-design. Those require compatible materialisers and evaluators;
they remain explicit frontier work. Installed mass, structural performance,
propulsion, braking, safe service and physical release remain unqualified.
