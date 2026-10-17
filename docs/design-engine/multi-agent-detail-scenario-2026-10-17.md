# Generative civil and mechanical design team — detailed development

The [executed design review](generative-detail-2026-10-17/index.html) develops
connected mechanical assemblies and civil details through failure-directed
variations. The executable scenario allocates all 63 existing work packages,
283 distinct controlled inventory IDs, production evidence and interfaces.
It advances the [original scenario](multi-agent-design-scenario-2026-10-16.md)
with geometry, connection, reinforcement, stock, access and process checks.
All packages retain their engineering and manufacturing acceptance gates.

## Team and responsibility

| Role | Design responsibility | Required handover |
| --- | --- | --- |
| Configuration coordinator | Separate LM3 and six-car planning bases; load cases, revision control and dependency propagation | Source-bound contexts, accepted-input requests and exact affected descendants |
| Mechanical designer | Connected underframe, crossbearers, bolsters, diaphragms, pads, bolts, welds and proposed stock segments | Geometry, mass, reactions, stiffness/stress results, joint/access checks and manufacturing proposals |
| Civil designer | Beam geometry, tendon/cage interfaces, link resistance, pad/end reservations and outer-support footing demand | Recomputed beam weight, section and stress responses, link/cage checks, reactions, deflection and site assumptions |
| Manufacturing integrator | Complete inventory allocation, material/stock/machine cases, tooling, drawing and inspection evidence | Package-specific production routes, actual artifact/inspection IDs and supplier configuration requests |
| Independent critic | Challenge calculations and scope without approving their own designs | Adverse counterexamples, unresolved assumptions and corrections before publication |

The implementation was developed by three collaborating specialist agents and
the coordinator. A worker slot rotates to independent critique. The reproducible
runner executes numerical role adapters; it does not simulate new LLM discussions
or appoint an accountable engineer. Automated critique checks contracts and
known failures; qualified independent engineering acceptance remains required.

The workflow separates iterative design definition, interface control and
verification. This is consistent with the general process described in
[NASA's design-solution definition guidance](https://www.nasa.gov/reference/4-4-design-solution-definition/).
That reference supplies workflow guidance, not a railway design standard.

## Executable design cycle

1. Audit current inventories and source hashes. Every controlled ID must have
   an owner, and all package dependencies must be known and acyclic.
2. Start each context from explicit geometry and unaccepted research inputs.
   LM3 and six-car designs remain separate. Unknown loads, material properties,
   soil or supplier limits cannot become accepted values through iteration.
3. Evaluate an actual variant. Retain its dimensions and units, materials,
   connection assumptions, load case, manufacturing route, failed checks and
   unknown qualification gates. Checkpoint attempts before generating children.
4. Generate changed dimensions in response to failed checks. Prioritise repairs
   of the evaluated parent with the fewest known adverse checks, then generation.
   Recompute self-weight and affected demands after every change. Unknown cost,
   material acceptance and inspection results never improve priority or ranking.
5. Transfer known modelled mechanical steel mass into civil axle-force sensitivities.
   No unidentified original frame mass is subtracted. Net replacement mass, missing accessory mass and
   an approved new CG/axle allocation remain unknown. This is no upper bound on
   complete vehicle mass. Recompute civil moments,
   reactions, section/stress response and deflection before repairing details.
6. Send retained diagnostics and provisional shortlists through a separate
   critique. Native FreeCAD/STEP export and reopen checks confirm declared
   primitive geometry; they cannot qualify resistance or manufacturing processes.
7. Record a provisional local solution, a bounded unresolved search, or a repair
   domain without a solution. Resume an unchanged source/context from its retained
   frontier without re-evaluating identical variants. A changed source or context
   requires a new campaign and review of affected descendants.

The current execution is one orchestration pass, with a default total budget of
256 evaluations per context and an absolute cap of 512. Feedback generations are
bounded by the evaluation budget. Four future review passes are a planning
allocation for controlled input/model changes, not a claim that four generations
or repeated unchanged calculations complete a design.

## What the discipline models actually evaluate

Mechanical variants include longitudinal plates, crossbearers, bolsters,
diaphragms, drilled support pads and calculated bolt/tool reservations. They retain gross steel
mass, statically balanced reactions, overhanging-beam research response,
member stress, local plate buckling, transverse transfer, weld flow, bolt/pad
checks, stock segmentation, tool access, proposed datums and routing. Full
joint flexibility, end-load introduction, fatigue/crash, real material/process
qualification and vehicle integration remain separate gates.

Civil variants change stem width and depth as well as link diameter/spacing,
pad length and footing width. Cage fit can force a wider stem, whose added
weight and changed prestress response can force a deeper beam. The web truss
uses the explicitly declared lower-strand-group centroid as a provisional
chord assumption; ultimate flexure and chord qualification remain open.
Pad and footing checks retain exact equilibrium and explicitly hypothetical
pressure limits. They do not establish soil bearing resistance, settlement,
pier/footing reinforcement, adjacent-span pier loading or bearing capacity.

The detailed component IDs identify proposed research assemblies. Controlled
target mappings and their source revisions identify the intended catalogue
families; they do not adopt a new geometry as a released reusable type.
Other packages retain their actual preliminary evaluations and exact missing
discipline-model, input, interface, supplier and physical-evidence work.

## Executed result

The source-bound run retained **310 detailed variations** across six contexts.
Five contexts reached passing known checks; all six structural models exported
and reopened successfully in FreeCAD and STEP. The existing preliminary campaign
also freshly evaluated all 63 packages: 68 investigations and 2,178 bounded
records, separately from the 310 new detail variations.

| Context | Evaluations | Provisional result |
| --- | ---: | --- |
| LM3 connected frame | 256 | Unresolved: the diagnostic 600 mm side members violate the 260 mm source envelope |
| Six-car connected frame | 21 | Known checks pass under both declared mass cases; 750 mm sides and M27 proposals require unaccepted gauge, joint and supplier qualification |
| LM3 Pi20 detail | 5 | 1.40 m beam, 0.36 m stems, 12 mm links at 0.30 m, 0.35 m pad reservation |
| LM3 Pi25 detail | 10 | 1.70 m beam, 0.36 m stems, 12 mm links at 0.20 m, 0.35 m pad reservation |
| Six-car Pi20 detail | 6 | 1.40 m beam, 0.36 m stems, 12 mm links at 0.20 m, 0.35 m pad reservation |
| Six-car Pi25 detail | 12 | 1.55 m beam, 0.36 m stems, 12 mm links at 0.20 m, 0.50 m pad reservation |

The selected civil screens use 4.5 m square outer-support footing proposals,
under the explicit hypothetical soil limit. A retained independent regression
also shows how the heavier predecessor mechanical proposal exceeds that limit
at 4.5 m and passes its pressure calculation at 5.0 m after adding 9.5 tonnes of
concrete. The final M27/frame proposal has less modelled steel, so its transferred
load permits the smaller footing screen. Neither result establishes a site or
foundation design.

The LM3 analytical bound gives at least **14.36 mm** deflection against an
unaccepted **12.3 mm** criterion, even with optimistic solid members and no
added self-weight, under the declared constant-EI model. It identifies a need
to change or substantiate the structural concept/criteria. It does not prove
that every possible LM3 carbody, shell, truss or variable-stiffness solution is
infeasible. The loop retains its unsuccessful designs and exact next actions.

Native scenes contain **100, 106, 110, 110, 158 and 158 declared primitives**.
These are geometry checks on structural/cage representations, not counts of
completed components, full hardware assemblies or issued fabrication drawings.
The modelled six-car steel subset is approximately **8.56 tonnes per car**;
missing fastener/weld/paint mass and removed existing structure remain unknown.

## Manufacturing and British suppliers

Prioritise evidenced British manufacture for the actual offered configuration.
The mechanical plate route records the British-built Swift-Cut XP4000 published
work envelope and plate limits, while identifying the imported plasma subsystem.
Segmented long-member proposals retain unqualified splice geometry/load paths;
a machine-fit check does not qualify the fabricated frame. Historical Dalzell
plate data does not establish current stock availability. Civil bearing leads
distinguish Ekspan's stated UK manufacture from UK supply/support with origin
still unconfirmed. The dated primary source records and qualifications are in
[mechanical inputs](../../engineering/generative_design/data/mechanical-detail-space.json)
and [civil inputs](../../engineering/generative_design/data/civil-detail-space.json).

Each package must close the complete chain: controlled requirements → part →
joint → assembly → analysis → issued manufacturing information → qualified
process → measured first article → independent exact-revision acceptance.
The scenario maps the current 472 missing/unissued production artifacts, 416
planned inspection characteristics without actual results and 47 unissued
drawing definitions. It does not populate approvals or measurements on their
behalf. Supplier requests are prepared and unsent.

## Run, resume and verify

```sh
./osr design campaign scenario-plan > build/design-scenario-plan.json
./osr design campaign iterate --output build/generative-design/detail-1 \
  --budget 256 --native
./osr design campaign verify-iteration \
  --output build/generative-design/detail-1 --require-native
./osr design campaign iterate --output build/generative-design/detail-2 \
  --budget 512 --native --resume build/generative-design/detail-1
./osr design campaign publish-iteration \
  --output build/generative-design/detail-1 \
  --destination docs/design-engine/generative-detail-new
```

The ordinary run freshly executes the existing 63 preliminary package studies
as well as the new detailed loop. `--no-baseline` runs the new details only.
Resuming uses a larger *total* budget, retaining prior evaluations; source changes
are rejected. Historical integrity verification is available with `--historical`;
it cannot satisfy `--require-native` or assert current numerical applicability.
Publication uses the shared immutable evidence store and preserves the exact
execution seal. Read archived JSON through `evidence_store.read_json`.

`./osr validate run --profile factory-native` now requires fresh detailed models
and their verification in addition to the original factory and architecture
models. Required context membership is independently derived. A missing or
failed native export rejects the profile, including when its CAD model is only
a diagnostic of a known failed design. Its structural failure remains failed.

Completion requires all exact package predicates and accepted integrated
interfaces, with no failed or unknown mandatory checks. An exhausted budget,
CAD export, proposed bar schedule or populated inspection template cannot close
those predicates. The review shows the next required engineering or physical
action for every package.
