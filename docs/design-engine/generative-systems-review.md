# Generative mechanical and civil design: systems review

Reference date: **15 October 2026**. This review uses official project
documentation, source repositories and vendor documentation. Tool capabilities
below describe the reviewed systems; they do not assert an OpenSourceRail
integration, a successful local run or engineering qualification.

OpenSourceRail already has controlled functional charters, physical assembly
definitions, bounded searches, explicit interaction studies, native domain
solvers and source-bound review packages. The baseline inspected at commit
`23acc230b7bbc7c32cf93132cb4a1c1aa3c4bbd6` has thirteen common charters; its
proxy search and later confirmation do not constitute a general recursive
CAD–mesh–solve–measure–revise loop. See the [engine contract](../../engineering/design_engine/README.md)
and [retained verification limits](verification.md). The recommendations here
address that specific gap. Implementation and actual execution evidence remain
separate from this literature review.

## Functional comparison

These twelve rows cover different stages of the workflow. An optimiser does
not replace a geometry kernel, a mesher does not validate boundary conditions,
and solver convergence alone does not establish a suitable physical model.
License entries identify upstream project terms; bundled dependencies and
optional plug-ins retain their own terms.

| System and distinct capability | Useful functions | Limits relevant to OpenSourceRail | License and primary references |
| --- | --- | --- | --- |
| **FreeCAD: editable native CAD and FEM orchestration** | Parametric documents, solid geometry and scripted FEM preparation; the documented CalculiX helper separates prerequisites, input writing, execution and result loading. | A saved document or successful recompute does not prove valid solids, correct supports or solver agreement. GUI availability does not establish headless execution. Keep controlled object IDs and reopen exported files. | LGPL source; official license guide describes LGPL 2 or later, while the locally installed Flatpak declares LGPL-2.1. [License guide](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/License.md), [FEM Python workflow](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/FEM_Tutorial_Python.md). |
| **Gmsh: geometry-aware meshing** | OpenCASCADE geometry, STEP import, physical groups, local size fields, embedded interfaces and mesh inspection through an API. | Shape entity numbers can change after booleans. Re-establish support/load groups semantically and check their measures. Finer elements do not automatically improve an invalid model. Provider, algorithm and settings affect replay. | GPL 2 or later with the documented linking exception; commercial licensing is also offered. [Manual, copying conditions and tutorials](https://gmsh.info/doc/texinfo/gmsh.html). |
| **CalculiX: structural and thermomechanical response** | Static, dynamic, buckling, thermal and nonlinear analyses, contact and material models; documented examples support independent numerical benchmarks. | An input deck can solve the wrong physical problem. Element formulation, integration, thickness, contact, increments and result completeness require checks. Missing material or joint evidence cannot be inferred from solver success. | GPL v2 published by the project; dependencies have separate notices. [Official project and licensing](https://www.dhondt.de/), [2.23 manual](https://www.dhondt.de/ccx_2.23.pdf). |
| **SALOME / Code_Aster: reproducible study preparation and supervised execution** | SALOME exposes geometry-linked sub-meshes, mesh groups and Python study dumps. Code_Aster provides execution/status handling, test-case tooling and a structural analysis environment. | A substantial optional toolchain, rather than a prerequisite for the existing local loop. Study dumps require version control. Code_Aster's public repository excludes some proprietary validation/material data; their existence is not available validation evidence. | SALOME LGPL 2.1; Code_Aster repository publishes GPL v3. Dependencies and commercial mesh plug-ins differ. [SMESH Python API](https://docs.salome-platform.org/latest/gui/SMESH/smeshpy_interface.html), [SALOME FAQ](https://www.salome-platform.org/?page_id=423), [Code_Aster runner/testing docs](https://codeaster.readthedocs.io/en/latest/), [source/data scope](https://gitlab.com/codeaster/src/-/raw/main/README.md), [solver license](https://gitlab.com/codeaster/src/-/raw/main/LICENSE). |
| **OpenSees: nonlinear civil and earthquake system models** | A structural/geotechnical simulation framework for nonlinear response, useful for pier/foundation interaction and dynamic civil models. | Separate model calibration, constitutive assumptions, soil data and analysis convergence from structural adequacy. A frame model does not resolve every local solid/joint effect. Commercial-product redistribution needs attention to the actual upstream terms. | Berkeley terms permit educational/research/nonprofit noncommercial use and other entities' internal use; commercial-product incorporation requires permission. Do not label this unrestricted open source. [Official framework](https://opensees.berkeley.edu/), [copyright and permissions](https://opensees.berkeley.edu/OpenSees/copyright.php). |
| **OpenMDAO: coupled multidisciplinary models and derivatives** | Explicit/implicit components, nonlinear coupling, units, partial/total derivatives, independent derivative checks and solver/driver/system recordings. | Useful when battery, thermal, mass and structure influence one another. Discrete changes, failed CAD operations and noisy remeshing may defeat smooth derivatives; derivative agreement is not physical validation. | Apache 2.0. [Derivative framework and checks](https://openmdao.org/newdocs/versions/latest/features/core_features/working_with_derivatives/index.html), [recording](https://openmdao.org/newdocs/versions/latest/features/recording/index.html), [license](https://github.com/OpenMDAO/OpenMDAO/blob/master/LICENSE.txt). |
| **Dakota: nested studies and uncertainty propagation** | Distinct variables/interfaces/responses, nested methods, sampling, interval analysis, calibration and restart/refinement of studies. | Distributions require evidence. An interval is not a uniform probability distribution; a finite scenario set does not establish a failure probability. Large nested studies need separately charged solver budgets. | LGPL 2.1; included packages have their own terms. [Study structure](https://snl-dakota.github.io/docs/latest_release/users/usingdakota/reference.html), [uncertainty and restart examples](https://snl-dakota.github.io/docs/latest_release/users/usingdakota/studytypes/uq.html), [license](https://raw.githubusercontent.com/snl-dakota/dakota/devel/LICENSE). |
| **pymoo: mixed-variable and multiobjective search** | Real/integer/binary/choice variables, constrained multiobjective algorithms, ask/tell control, termination and checkpoints. | A Pareto front is conditional on its model, constraints and tested domain. A seed alone does not pin native subprocesses or completion order. Unknown cost/carbon axes cannot become zero-valued objectives. | Apache 2.0. Already used by OpenSourceRail's existing optimisation workflow; this review does not establish new algorithm coverage. [Mixed variables](https://pymoo.org/customization/mixed.html), [framework features](https://pymoo.org/), [license](https://raw.githubusercontent.com/anyoptimization/pymoo/main/LICENSE). |
| **CadQuery / build123d: code-authored exact part families** | Python parametric BRep construction on OpenCASCADE; CadQuery supports GUI-free use and STEP output, while build123d offers explicit geometry classes, locations and composable operations. | Optional alternatives to existing controlled FreeCAD construction. STEP/STL export does not supply FEM, manufacture approval or stable feature identity. Adding another kernel binding requires new compatibility and provenance checks. | Both Apache 2.0 for their own code; kernel dependencies differ. [CadQuery capabilities](https://cadquery.readthedocs.io/en/latest/intro.html), [CadQuery license](https://raw.githubusercontent.com/CadQuery/cadquery/master/LICENSE), [build123d capabilities](https://build123d.readthedocs.io/en/latest/), [build123d license](https://raw.githubusercontent.com/gumyr/build123d/dev/LICENSE). |
| **SU2: adjoint shape optimisation and mesh deformation** | Direct/adjoint flow solves, geometric constraints, mesh deformation/adaptation and a Python-driven shape optimisation cycle. | Relevant to later drag, cooling and ventilation studies. It does not replace structural FEM or the thermal boundary-condition evidence. The official binary-download page warns discrete-adjoint support is unavailable in its supplied binaries; verify the exact build capability. | LGPL 2.1 or later in current source notices. [Module separation](https://su2code.github.io/docs_v7/Software-Components/), [build/download limits](https://su2code.github.io/download.html), [shape driver source](https://github.com/su2code/SU2/blob/master/SU2_PY/shape_optimization.py). |
| **CalculiX beso: topology exploration** | Iterative element/material-domain evolution using CalculiX responses, with documented beam and bracket examples and a FreeCAD interface. | A removed-element field is a concept, not a finished manufacturable solid. Preserve attachment/load regions and translate the result into controlled CAD; re-mesh and solve that reconstructed part before comparing it. | LGPL v3. This is a project implementing BESO, not a claim that every BESO implementation has this license. [Project/prerequisites/license](https://github.com/calculix/beso/blob/master/README.md), [method documentation](https://github.com/calculix/beso/wiki/Basic-description). |
| **Ansys optiSLang: mature commercial exploration workflow** | Sensitivity-led variable selection, surrogate model comparison, optimisation and verification of the predicted best design by an actual solver call. | A useful workflow reference only; no Ansys integration, license or installation is claimed. A predicted best needs its actual objective and constraint values retained independently of surrogate training quality. | Proprietary commercial product. [Metamodel workflow](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/opti_pdo/opti_pdo.metamodeling_techniques.html), [optimisation and actual-solver verification](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/opti_pdo/opti_pdo_single_objective_optim.single_obj.html). |

## Ideas selected for OpenSourceRail's implementation

The following are design decisions to implement and test; they do not imply
installation or integration of every reviewed framework.

| Selected idea | Concrete mapping to the common engine | Evidence needed before claiming it works |
| --- | --- | --- |
| Keep design, execution and response contracts distinct, following Dakota's separation. | Retain the functional charter and complete candidate definition; a recursive policy chooses bounded next candidates while adapters own actual physical evaluation. | Changing length, capacity, required area, span, service loads or support scope cannot silently improve a candidate's objective. |
| Use actual response feedback for refinement. | Advance a documented decimal lattice or declared choice neighbourhood using native-confirmed incumbents; keep an infeasible descent path and global fallback when no feasible incumbent exists. | A real failing design leads to a changed generated part and a fresh native solve; hardcoded synthetic objectives cannot establish this claim. |
| Preserve cheap screening and expensive verification as separate evidence, following the optiSLang verification boundary. | Screen for geometry/coherence/domain limits, then confirm eligible candidates with the exact native CAD, mesh and solver pipeline. | Native failure/unknown/unavailability cannot become the best verified candidate, even if its proxy objective is attractive. |
| Treat CAD/mesh selections as part of the model, following FreeCAD, Gmsh and SALOME. | Stable physical IDs connect the generated solid, material, mesh domains, loads, supports, takeoff and inspection view. | Reopen CAD/STEP, compare solid count, volume, mass/CG and extents; verify support/load group locations and total measures after remeshing. |
| Keep iteration recordings and restart state, following OpenMDAO and Dakota. | Append attempts, ancestry, proposed variables, actual metrics, native case allocations, FIFO confirmation queue and stop reasons to the durable job. | Cancel/resume/recovery retains prior failures and reproduces the next proposal under the same policy and environment. |
| Keep uncertainty explicit. | Extend the existing paired factorial evaluator with declared bounds/scenarios; compare designs under the same actual cases. | Report scenario coverage and missing evidence; do not label bounded scenarios as a probability distribution or reliability qualification. |
| Keep topology and CFD as later optional adapters. | Add bounded design-domain and physics-specific charters only when their complete CAD/FEM or CFD validation chain exists. | Reconstructed CAD plus independent native holdouts, manufacturing constraints and domain-specific verification precede any installed design credit. |

## Determinism and native-verification acceptance criteria

These are proposed acceptance criteria for the new loop. They are stricter than
“the optimiser returned a winner” and can be tested independently of any
particular search library.

1. **Replay the decision process.** Pin the charter, full scope, typed inputs,
   policy revision, variable ordering, choice order, decimal quantisation,
   tie-breaking rules and candidate ancestry. Under the same pinned evaluator
   and evaluation budget, the proposal/confirmation transcript must repeat.
   A wall-time stop can shorten a transcript; record it as incomplete rather
   than promising identical completed work on differently loaded machines.
2. **Identify the actual tools.** Record resolved executable/shared-library
   paths and hashes, package/runtime versions, interpreter, relevant numerical
   thread settings, mesh algorithms and tolerances. Equal version labels do
   not prove equal solver builds. Different Gmsh providers cannot share cached
   native results merely because the Python request is identical.
3. **Preserve the full physical question.** Geometry, material/section/batch
   applicability, loads, interfaces, supports, manufacturing rules, required
   function and objective definitions belong to the candidate/cache identity.
   Reject incomplete or incompatible correspondence instead of manufacturing
   a default load, material strength or support condition.
4. **Check the complete native chain.** Validate/reopen the generated solid;
   mesh that candidate; retain the mesh and actual input deck; execute the
   native solver; parse complete finite results and convergence diagnostics.
   Require nonempty support/load sets, equilibrium checks and the declared
   response limits. A zero subprocess exit by itself is insufficient.
5. **Separate numerical verification from design adequacy.** Declare mesh,
   time-step and domain refinement metrics and tolerances before execution.
   Two meshes can satisfy a declared pairwise tolerance without proving
   asymptotic convergence. Singular peak stresses need a defined physical
   evaluation region or method. An analytical benchmark must represent the
   solved boundary conditions; an independent holdout must not be a copied
   formula from the candidate's screening implementation.
6. **Let adverse evidence control selection.** Retain screening, native and
   physical-evidence checks separately. Only candidates with every required
   numerical check passed and every declared objective finite/known can enter
   the verified ranking. Preserve native-failed, unknown, cancelled,
   unavailable and budget-limited candidates and their raw artifacts. Missing
   physical qualification stays open even when numerical criteria pass.
7. **Bound recursion and restart it honestly.** Count every attempted
   evaluation/cache use according to the declared policy, while charging real
   native calls and subprocess budgets separately. Checkpoints bind the exact
   policy/context, evaluated candidates, pending queue and evidence identities.
   Exhausting a budget does not establish convergence or exhaust the domain.
8. **Constrain the claim.** A finite exhaustive choice study can establish the
   best verified candidate in that declared tested domain only if all required
   assignments were actually confirmed and all relevant outcomes are known.
   A local search or finite continuous lattice cannot establish a global
   optimum. Numerical verification never grants physical acceptance, issued
   drawings, adopted finance or permission to construct.

## Read-only local tooling inventory

The following observations were captured on 15 October 2026 in the repository
environment. They are host observations, not portable installation guarantees.
The local receipt `build/generative-design/tools-inventory.json` retains actual
command arguments, outputs, exit codes, package metadata and selected hashes;
it is ignored local evidence rather than a tracked or qualified tool package.
No packages were installed and no physics jobs were run for this inventory.

| Tool/provider | Actual observation | Consequence for the new loop |
| --- | --- | --- |
| CalculiX `/usr/bin/ccx` | Version 2.23; version-only probe exits 201; executable SHA256 `373f7ef4c118a1b5e1b53041fe4f7ef1f1f854051326e0d3f1eeb890ec34885b`. | Accept the known version-probe behaviour separately from a solve, which needs complete results and its own success checks. |
| Gmsh in `.venv` | Python/API/package 4.14.1; library `libgmsh.so.4.14`, SHA256 `9b6ba60833668f0b36ed503904a6c14032f8885916449d5fe70b43ca3cff4631`. | API available. The executable launcher uses `env python` and failed under the inspected shell PATH; invoking it with the explicit repository interpreter succeeded. |
| Gmsh in FreeCAD Flatpak | Actual `--command=gmsh ... --version` returned `4.15.0-git`. | A distinct provider/build; select and hash the one actually used. |
| FreeCAD Flatpak | Package metadata 1.1.4, commit `e63d66825c4daf9adb09283488c2bc2ace92ed8b24bcf81666933226ed082fd4`. A GUI-binary `FreeCAD --version` probe timed out after 20 seconds. Its exact owned probe processes were removed and the cleanup was recorded separately. | Metadata is not a successful headless-runtime proof. Use the controlled headless resolver and retain the actual application version/build from a successful native invocation. Do not infer it from the package label. |
| Existing Python numerical stack | NumPy 2.3.5, SciPy 1.16.3, pymoo 0.6.1.6; OpenSeesPy package 3.8.0.0. | Package presence is recorded; native import/solve and exact backend compatibility require their own preflight. |
| Reviewed optional systems | OpenMDAO, CadQuery, build123d, SALOME, dolfinx and meshio were absent from the inspected `.venv`; Dakota, SU2 and SALOME CLIs were absent from PATH. | Do not make these dependencies implicit. Their reviewed ideas can inform the existing stack without claiming availability. |
| Available disk | Approximately 6 GiB at capture. | Reuse the installed stack; retain old evidence and checkpoints. Any later larger optional installation needs an explicit resource plan. |

The current common toolchain fingerprint records several Python package versions
and the CalculiX executable hash. Extending it for a CAD→Gmsh→CalculiX recursive
adapter must include that adapter's actual CAD runtime and mesher provider;
otherwise a common request fingerprint cannot establish that the native pipeline
was unchanged. This is a source inspection finding, not a claim that every
existing domain producer lacks its own narrower toolchain receipt.
