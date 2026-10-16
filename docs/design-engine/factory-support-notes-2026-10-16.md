# Baghdad factory support and finite resource development

The [visual review](factory-support/index.html) and
[93-object FreeCAD model](factory-support/model.FCStd) extend the common
`factory-precast` problem. Two drilled post baseplates, grout/pad reservations,
anchor envelopes, drilled washers and nut envelopes connect the first pair of
restraint posts to a foundation hypothesis. The original nine factory examples
remain unchanged. The vehicle factory's fixture and locator examples continue
through the same common engine; the machining comparison below exposes a shared
workshop limitation.

This is unissued research. Native geometry passes do not establish structural
resistance, factory output, an accepted supplier configuration or construction
release. Actual soil, connections, installed prices and imported content remain
unknown.

## Support mechanics and results

The selected balanced Pi25 scenario applies 7.392 MN initial bed force, split
between two nominal return rails. Independent lateral and vertical beam-column
models retain the selected ideal springs. Four combinations of imperfection
signs at each of eight matching stations produce 32 support-action cases per
nominal rail. Demands from different stations are not combined. The second rail
is a symmetric reference, rather than a staged three-dimensional torsion solve.

Each support uses a rigid 450 × 450 × 30 mm plate hypothesis, four anchor
positions at ±160 mm, 32 mm holes and a 20 mm grout reservation. Compression-only
grout strips and zero-preload tension-only anchors solve vertical translation
and base rotation together. Anchor springs use nominal gross bar area, not
thread-root or embedment stiffness. Force/moment residuals, reversal, uniform
compression, uplift, strip refinement and independent continuous integration
are tested. Nominal square fillet-weld line demands are retained separately;
neither weld solids, WPS nor resistance are qualified.

The largest calculated anchor tension is **2.499 kN within this final-force
imperfection subset**. It excludes stressing/release torsion and cannot be used
as the complete anchor design load. Pad pressure includes represented dead
weight and checks uniaxial compression equilibrium; bearing resistance, sliding,
reinforcement, settlement and embedment remain unknown.

Post bending, base rotation, connection and ground compliances combine in
series. Vertical post stiffness uses EA/L; lateral stiffness uses 3EI/L³.
The following sensitivity uses the minimum local contact tangent from the
selected ideal-spring cases. It is one pass, not a self-consistent nonlinear
soil/rail iteration.

| Interface hypothesis | Effective lateral MN/m | Effective vertical MN/m | Lateral elastic load factor | Meets selected lateral 1 MN/m? |
| --- | ---: | ---: | ---: | --- |
| Actual, unmeasured | Unknown | Unknown | Unknown | Unknown |
| Soft | 0.04884 | 0.90790 | 0.612 | No; elastic screen also fails |
| Medium | 0.86517 | 6.60305 | 2.570 | No |
| Stiff | 6.63493 | 60.80794 | 7.247 | Conditional hypothesis |

The existing strongback's 1 MN/m compliance reference is labelled separately
when it differs from a selected common spring case. Ideal end-pin grounding,
the remaining fourteen restraint pads, end foundations, local plate flexibility,
rail selfweight/operating actions and full stressing/release combinations remain
open. The represented inventory has about 8,438.94 kg nominal steel; complete
mass, CG and inertia remain unknown because purchased items and envelopes do
not acquire invented properties.

## Coupled machining and British supplier cases

The original CV5 register limits workpiece diameter to 500 mm. The 450 mm square
baseplate has a 636 mm diagonal and exceeds that stated envelope. A 350 mm square
alternative fits the nominal diameter but its fixed holes break the plate edge
by 1 mm. Axis travel alone cannot accept either configuration. The 450 mm plate
therefore needs a qualified subcontract or different-machine route, with exact
workholding, access, payload and inspection confirmed.

| Case | Published evidence checked 16 October 2026 | Application and unresolved return |
| --- | --- | --- |
| Macalloy 1030 carbon bar system | Carbon bar range starts at 26.5 mm; accessories and foundation uses are described. Macalloy documents its Dinnington factory. | British manufacture priority candidate. A former 26 mm hole is too small even for the shaft. The concept's 32 mm hole, thread/fittings, actual origin, stiffness, embedment and resistance require a configuration-specific return. |
| Rapid RP1000 planetary mixer | Model named in the Lagan Tile case study; the planetary family has a published range. Rapid documents Northern Ireland manufacturing. | UK manufacture, with Northern Ireland distinguished from Great Britain. RP1000 useful output, cycle, beam-mix suitability, cooling, utilities and Baghdad installation remain unconfirmed. |
| Pro-Mil Shop Two subcontract | Registered Asquith Butler Starcut 260 travel is 6 × 4.35 × 2.15 m; the shop lists a 50 t crane. | Candidate machining route for the larger plate. Shop crane capacity is not machine-table capacity. No offer or workholding acceptance exists. |

Sources: [Macalloy system](https://macalloy.com/products-services/post-tensioning/),
[factory history](https://macalloy.com/about/history/),
[Rapid RP1000 case study](https://rapidinternational.com/category/case-studies/page/2/),
[planetary family](https://rapidinternational.com/planetary-concrete-mixer/),
[Rapid corporate brochure, pp. 2–5](https://rapidinternational.com/wp-content/uploads/2024/09/Metric-Version-Corporate-Brochure.pdf),
[Pro-Mil machining capacities](https://www.pro-mil.co.uk/services/precision-cnc-milling--large-cnc-machining-capacities/7.htm).
The [controlled enquiry register](../../engineering/design_engine/data/factory-interface-suppliers.json)
and [unsent RFQs](factory-support/interface-rfq.csv) separate published facts,
OSR assumptions and missing evidence. No supplier was contacted.

## Finite production campaign

The new resource calendar models sixteen Pi25 beams over ten consecutive
calendar days with a 16-hour daily operating window. Two eight-hour teams are
assumed; breaks and handover remain unmodelled. Curing and storage dwell use
elapsed clock hours. Reinforcement benches remain occupied until cage lifts;
beds remain occupied through release/demould; storage remains occupied through
dispatch. Maintenance blocks compete with work on actual resource units.

The **1 m³ useful batch, three-minute mix/load/discharge and six-minute pour
are OSR assumptions, not RP1000 specifications**. A 32.34055 m³ Pi25 pour needs
33 assumed batches. Casting holds mixer, crane and crew continuously for
5.2 hours, including setup/finish. Mixing and pouring do not overlap in this
policy. Each beam prescribes 6.95 crane service hours across all handling stages.
Maturity, concrete mix, reinforcement, delivery route and durations need evidence.

| Beds | Cranes | Crane crews | Dispatched by day 10 | Backlog |
| ---: | ---: | ---: | ---: | ---: |
| 4 | 1 | 1 | 10 | 6 |
| 4 | 2 | 1 | 11 | 5 |
| 4 | 2 | 2 | 16 | 0 |
| 134 | 1 | 1 | 10 | 6 |
| 134 | 2 | 2 | 16 | 0 |

These five actual common candidates are retained in the
[verified comparison record](factory-resource-comparison.json). The default
books 93.8 crane hours inside the horizon and yields a 9.5 accepted-equivalent
planning quantity under an unmeasured 95% yield assumption. Calendar validation
checks units, overlap, resource requirements, task durations, precedence, shifts,
maintenance and continuous holds. A feasible list schedule is neither an optimum
nor steady-state capacity. Additional cranes have no qualified runway coverage,
simultaneous-lift clearance or foundation arrangement. The 54/day programme
target remains unsubstantiated; bed count alone cannot establish it.

## Common evidence and reproduction

Native job `run-263299d7390a4d85` executed FreeCAD and reopened the 93-object
FCStd and STEP. The snapshot is a compact projection of its verified common
export, with exact file hashes, retained request, native receipt, view metadata
and parent export-manifest hash. STEP stays in the ignored local parent export.
The static page does not run a second engineering solver. Source-bound common
exports retain all original attempts; the compact snapshot is not a substitute
for their complete archive. The five-case screen job is
`run-25b8993f39664703`; installed cost stays null and no optimum is claimed.

```sh
./osr design run --problem factory-precast --city baghdad --revision factory-support-1 --refine --evaluations 4 --wall-seconds 180
./osr design export <job-id> --output build/factory-support-<unique-name> --native
.venv/bin/python tools/automation/publish-factory-review.py --export build/factory-support-<unique-name> --output <fresh-snapshot-directory>
.venv/bin/python tools/automation/publish-factory-review.py --check --current --output docs/design-engine/factory-support
```

Publication refuses an existing destination. Exact snapshot integrity can remain
valid historically; `--current` additionally requires the present dependency
closure. Neither mode reruns numerics. Required `factory-native` acceptance
executes all nine original models and both common adapters and verifies this
retained snapshot. Railway beam loading/resistance, full foundation design,
first articles, supplier acceptance and measured production remain next gates.
