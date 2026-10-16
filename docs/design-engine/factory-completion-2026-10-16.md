# Mechanical and civil factory development delivery record

**The representative development and review package in plan stages 1–5 is
complete. Engineering design for manufacture/construction and stage 6
qualification remain incomplete.** The [handover index](factory-buildout/index.html)
maps every planned development output to retained evidence and names seven
remaining engineering/evidence work groups. Its record distinguishes those
completion states; a missing artifact cannot become a completed stage. No
physical release or independent acceptance is granted.

## Delivered scope

| Planned stage | Retained development outputs |
| --- | --- |
| 1 Design basis | Versioned Baghdad assumptions; 37 case-by-case British-priority supplier assessments; model-specific equipment/fabrication/interface registers with sources, dates, origin distinctions and missing returns |
| 2 Mechanical first article example | Datum fixture, hollow/drilled solids, retained locator coupon, workholding candidates, six-restraint kinematic check, BOM/stock cuts, process/inspection route and machining/handling limitations |
| 3 Civil first article example | Pi20/Pi25 sections and prestress layouts, mould/bed concepts, elastic/handling screens, strongback fits and staged force histories, runway bay, complete nominal bed CAD and connected spatial study |
| 4 Both factory examples | Six-car component/assembly hall and pilot precast yard, sourced machine envelopes, service/circulation allowances, utility gaps, process resources and finite shared crane/crew schedules |
| 5 Review and reproduction | Nine unchanged original CAD models and reproduction seal; common controlled jobs, budgets, comparisons, native exports, exact snapshot integrity, portable numerical checks and unsent supplier enquiries |

Open the [original two-factory review](../../engineering/factory_examples/examples/index.html),
[current whole-bed review](factory-whole-bed/index.html),
[staged-load study](factory-stages/index.html), and
[37 supplier cases](../commercial/baghdad-uk-factory-suppliers-2026-10-15.md).
British manufacture is prioritised; Northern Ireland and overseas manufacture
are distinguished. Manufacturing origin, UK supply/integration, financing content
and offered configuration remain separate questions. No suppliers were contacted.

## Connected whole-bed model

The latest common `factory-precast` definition has **376 native objects**:
both strongbacks with grip envelopes, two full 26 m RHS return rails,
sixteen posts/baseplates and their nominal anchor/washer/nut/grout/pad details.
The original nine models and earlier 93-object snapshots remain unchanged.
Native primitives supply about 25,757.18 kg nominal represented steel. Purchased
envelopes and site reservations retain unknown properties; complete installed
mass, CG, inertia and price remain unknown.

The connected gross frame contains 112 nodes and 112 members. Physical end
offsets connect head centroids to rail faces and rail axes to post tops;
rigid-arm transformations preserve virtual work and resultants. All sixteen
bases have six finite translational/rotational springs from a synthetic ground
case. This separate model has **no ideal end pins**. All 145 stressing/unloading
states retain six-axis base wrenches, movement and global equilibrium residuals.
Signed CSV values act on the base foundations.

Steel gravity comes from the same nominal native volumes. Rail gravity uses
consistent uniform member loads; other steel masses are allocated at their
centroids. This does not establish local gravity stress distribution or measured
equipment mass. The force sum reconciles with represented steel mass.

The implementation reuses existing three-dimensional stiffness and RHS section
contracts. Closed-cell thin-wall torsion uses a torsional constant, separate from
polar area inertia. Native confirmation executes OpenSees `elasticBeamColumn`,
rigid links and six-axis zero-length base springs for two retained cases. It
compares all master-node translations/rotations and base reactions. This is an
independent stiffness/constraint implementation over shared loads/definitions,
not independent acceptance of the physical model.
[OpenSees element documentation](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/elasticBeamColumn.html),
[closed-section torsion formulation](https://abaqus.uclouvain.be/English/SIMACAEELMRefMap/simaelm-c-beamsectionbehavior.htm).

Global equilibrium uses `1e-7` of summed applied/reaction magnitudes plus
absolute floors of `1e-4 N` and `1e-3 Nm`. Native displacement comparison uses
relative `1e-5`, absolute `1e-9 m/rad`; reaction comparison uses relative `1e-5`,
absolute `1e-4 N/Nm`. These are numerical comparison tolerances, not engineering
allowables. Raw differences remain retained. Closed-form controls cover axial
extension, bending in both planes, torsion, rigid-arm work/resultants,
missing-ground mechanisms and gravity reconciliation.

| Ground hypothesis | Stressing order | Largest base force resultant, kN | Maximum translation, mm |
| --- | --- | ---: | ---: |
| Soft | Balanced pairs | 44.57 | 91.12 |
| Medium | Balanced pairs | 79.45 | 23.34 |
| Stiff | Balanced pairs | 127.97 | 13.66 |
| Medium | Lower first | 213.19 | 84.10 |

These four [verified scenarios](factory-whole-bed-comparison.json) show
sensitivity, not a qualified support selection. Base force resultants are neither
anchor tensions nor earlier ideal end-pin demands. Base moments, torsion and
biaxial effects must accompany them into connection/foundation design.

The first-order gross frame assumes rigid joints and linear ground. It omits
shear deformation, distortion/warping, local holes/diaphragms, contact/slip,
material nonlinearity and connected second-order interaction. Short deep
strongback segments especially require a suitable local/shear model. Earlier
failed/unknown second-order rail and one-axis contact screens remain separate
mandatory checks; this solve cannot clear them. No material, connection, ground
or displacement acceptance criterion has been adopted.

## Evidence and completion checks

Native common job `run-942f9b4d93dd499a` spent four charged evaluations: candidate
compilation, fresh FreeCAD confirmation and two OpenSees cases. It reopened
FCStd and STEP; original attempts and logs stay in the verified local export.
Screen job `run-ba8f21f9ab6c4b9c` executed four ground/stressing comparisons.
Publication preserves these results without another physics run. STEP stays in
the ignored parent export.

```sh
.venv/bin/python tools/automation/publish-factory-review.py --check --current --output docs/design-engine/factory-whole-bed
.venv/bin/python tools/automation/factory-buildout.py --check --current --output docs/design-engine/factory-buildout
./osr validate run --profile factory-native --output build/validation/factory-buildout-<unique-name>
```

The handover seals its publisher/basis, listed development evidence and index.
It verifies unchanged original artifact hashes and all three review snapshots.
Historical integrity is distinct from current applicability. Required local
acceptance freshly executes nine original CAD models and both common adapters,
including spatial native comparisons. This does not replace the separate
software-release gate.

## Remaining work before issued engineering designs

The [controlled delivery basis](../../engineering/design_engine/data/factory-delivery.json)
retains seven open groups: owner/site/design-basis inputs; structural design;
handling/erection; supplier returns; physical first articles; factory/site
qualification; and commercial/independent acceptance.

Further engineering includes railway loading, transmission/end zones,
reinforcement, shear/torsion/fatigue/deflection, local strongback/anchor/weld
resistance, nonlinear/second-order coupling, foundations, lifts, crane/runway and
haulage. It requires an accepted basis and relevant properties, followed by
review of actual configurations. Site/building/MEP/fire/extraction designs,
supplier GAs/utilities, calibrated tests, material/process evidence and measured
production are outstanding. Installed quotations and financing transaction
evidence are absent. These gaps require further engineering and external records;
the research software cannot close them by assigning a pass.
