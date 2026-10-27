# Executed generative structural design

The selected v0.6 railway is a reference, not the boundary of the design space. This new layer generates physical stock, load-path graphs, apertures, material assignments, joints, typed interfaces and assembly operations. Five initial recipes compose shared productions; a new recipe can combine those productions without adding another hardcoded body mesh. New primitive types and unsupported physics still require a generator/evaluator development task.

**8 physical candidates, 3 executed rewrites, 6 native CAD exports and 2 native axial design calculations.** Four independent native method fixtures passed. No complete carriage, physical journey or economic winner is qualified.

## What can actually change

The demonstrated productions vary aluminium versus research GFRP members, skin versus foam/honeycomb sandwich layers, rib spacing, repeated modular segments, underfloor triangulation, member proportions and separate versus shared roof/PV/channel manufacture. Car length, width, formation and support positions are explicit parameters with new requirement contexts. The existing 102-variable adaptive registry covers further railway domains; a descriptor is distinct from an executable, validated adapter.

The current competition preserves the 17 m reference envelope, passenger accommodation and door/window openings. A separate test generates a shorter body and propagates its geometry, stock and requirement context. Passenger fitout itself remains an unlocated source-bound account, so a new length is a research proposal rather than an accepted seating or evacuation layout.

| Generated recipe | Gross body stock | Pin-graph mechanisms | Declared manufactured groups |
|---|---:|---:|---:|
| aluminium_spaceframe | 2108.7 kg | 49 | 158 |
| gfrp_semimonocoque | 2653.8 kg | 49 | 159 |
| hybrid_structural_panels | 2924.8 kg | 49 | 158 |
| pultruded_gfrp_frame | 1687.8 kg | 49 | 158 |
| modular_segments | 3077.5 kg | 49 | 183 |
| aluminium_spaceframe | 3242.5 kg | 0 | 219 |
| aluminium_spaceframe | 2064.4 kg | 49 | 155 |
| aluminium_spaceframe | 2328.2 kg | 61 | 191 |

**These are gross body-stock subtotals, not vehicle tare.** Prismatic members are untrimmed nominal stock and can overlap at nodes. Joint cuts, actual joint hardware, fasteners, installed fitout positions and complete geometry remain unresolved. Known-stock CG and inertia are calculated; complete installed mass, CG and inertia are unknown.

## A failure produces an actual new load path

The initial underfloor is explicitly pin-jointed. Its rectangular cells have 49 mechanisms, so this particular axial load path cannot carry the declared load without further restraint or a different joint model. The engine diagnoses this conditional design failure, inserts physical diagonals below passenger openings, assigns a fresh physical identity, rebuilds stock and loads, and evaluates the child. It does not add fictitious ground restraints or reject all frame/sandwich bodies.

The rewritten graph has zero mechanisms. Two CalculiX T3D2 runs, with one and two axial subdivisions per member, agree with an independent stiffness-matrix solution and satisfy force, moment and energy residual checks. Maximum displacement is about 30.35 mm in this **underfloor-only axial hypothesis**. This is not comparable to the previous complete-body displacement and is not a pass/fail judgement against L/500.

The subdivision test checks straight-member axial invariance, not shell/solid mesh convergence. Pin joints carry no bending moments; real tube-end cuts, joint stiffness, local/global buckling, member strength, floor load introduction, laminate behaviour, fatigue, modes, thermal effects, fire and physical correlation remain open. The other shell/monocoque recipes have geometry and stock, but lack a suitable full-body evaluator. Their pin-graph mechanisms do not establish that their manufactured bonded or rigid-jointed bodies would fail.

## Numerical errors produce model repair

The first independent tripod subdivision run exposed an input-writer error: a long oblique constraint exceeded CalculiX input-line capacity. That failed execution and its exact producer are retained. The writer was corrected, then all four new axial-bar/tripod fixtures were rerun successfully. The bar fixture includes a load at its restrained node to independently check the solver reaction convention. The corrected method is admitted only for its axial scope.

## Integration, materials and manufacture

A separate rewrite integrates roof/PV/channel stock into fewer declared manufacturing groups, changing the counted subtotal by -44.33 kg. Required function tags remain covered; equivalent performance, net installed savings, fabrication feasibility, repair consequences and cost are unproven. Another rewrite changes rib positions. Both are executed geometry experiments, not automatic acceptance.

The material search filters retained primary supplier facts by component function, stock form, temperature, directional properties and declared processes. PET/PVC foams, aluminium/aramid honeycombs, joining products and equipment leads retain missing hot/wet, fatigue, fire and design-allowable data. Current GFRP axial stiffness is an explicit research assumption; no isotropic substitute is used to qualify a laminate. A honeycomb density does not supply a full orthotropic law.

The interface graph checks units, frames, directions, declared capacities, simultaneous demands, aperture keepouts, function coverage and assembly dependencies. Unsupported interface capacity or unlocated equipment remains unknown. DFMA generates fabrication/join/inspection operations and distinguishes geometric prisms from declared manufactured occurrences. Unknown tooling, labour, purchased price, QA, access and repair data remain unknown.

## Same-candidate propagation and continuation

Each design carries one physical identity through actual nominal solids, stock mass properties, load graph, CAD, interface checks, assembly, required-motion profiles and preliminary civil comparisons. Changed counted mass propagates into 1.5/2/3 km required-force/energy calculations and box/twin/U crowd-load studies. This is account propagation, not a converged force–motion–thermal simulation: actual moving LIM capability, full installed vehicle properties and installed economics remain missing.

The coordinator resumes exact-source native/CAD packets under bounded jobs/time. It preserves model-development tasks and all rejected/interrupted/invalid evidence. OpenMDAO, pymoo, build123d and Dakota are optional tools, not evidence: none was executed for this competition. FreeCAD and CalculiX performed the native work. A general autonomous search over every railway subsystem remains further work.

```bash
./osr design generative plan
./osr design generative run
./osr design generative publish
./osr design generative verify
```

[Summary](summary.json) · [Complete generated campaign](campaign.json.gz) · [Materials](materials.json.gz) · [Native/CAD index](native-index.json) · [Source epochs](source-epochs.json) · [Manifest](manifest.json)

Large native fields and CAD solids stay in indexed local runs or regenerate from exact-source inputs. Small input decks, geometry definitions, logs, results, checks and full raw-payload hashes are retained here. No remote artifact store or physically released design is claimed. The selected reference and all 266 city packages are unchanged.
