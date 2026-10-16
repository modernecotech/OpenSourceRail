# Mechanical and civil design and factory buildout plan

Build two reproducible Baghdad factory examples around the six-car vehicle
programme and the existing 20/25 m decked pi-beam family. Prioritise machinery
manufactured in Britain, identify Northern Ireland production separately, and
retain foreign-made equipment as explicit alternatives. The examples connect
product geometry, process capability, factory space, handling, utilities and
supplier enquiries. They are engineering development packages, not issued
construction or manufacturing designs.

## Delivery sequence

| Stage | Work and outputs | Completion test |
| --- | --- | --- |
| 1 Establish design basis | Read the canonical six-car factory assumptions, beam sections and industrialisation interfaces; retain a dated official-source equipment register | Each numeric supplier claim has a model, unit, source location and observation date; assumptions and unresolved values remain separate |
| 2 Mechanical first article | Develop a welded datum fixture with real hollow sections, machined plates, locator/fastener geometry, cut list, load/reaction screen and assembly/inspection sequence | Mass and geometry reconcile; fixture restraint and beam calculations have independent controls; selected cutting/machining/metrology envelopes are checked against actual parts |
| 3 Civil first article | Develop Pi20/Pi25 manufacturing sections, mould/bed interfaces, lifting/transport demands and factory frame/foundation concepts | Section/volume/self-weight and demand calculations reconcile with the canonical beam family; site ground, prestress, reinforcement, anchorage, stages and resistance gaps remain explicit |
| 4 Equip factory examples | Lay out vehicle/component production and a pilot precast yard using named UK supplier models and configured bespoke packages | Equipment and reserved service zones fit the site, avoid fixed circulation routes and have process/part links; missing utility and machine-foundation data cannot become zero demand |
| 5 Produce review artifacts | Generate BOMs, equipment/utility/RFQ registers, capacity comparisons, dimensioned plans and native CAD/STEP | Outputs reproduce from versioned inputs; actual CAD opens and geometry/part counts verify; schematic equipment is distinguished from manufacturer CAD |
| 6 Qualify and scale | Obtain technical returns, local capability/site surveys, measured first articles and accepted production records; revise make/buy, installed cost and finance cases | Named reviewers accept exact configurations and evidence; duplicate production cells only against demonstrated bottlenecks and demand |

Stages 1–5 are the software and example-design buildout for this iteration.
Stage 6 needs supplier, owner, laboratory and site participation. No supplier
contact, purchase, staffing appointment or physical acceptance is implied.

## First iteration delivered, 16 October 2026

The [example package](../../engineering/factory_examples/README.md) implements
the representative development work in stages 1–5. Open the
[offline visual review](../../engineering/factory_examples/examples/index.html)
for factory plans, tooling projections and 13 named supplier/model cases.
Four native models contain drilled/hollow fixture solids, pi-beam/mould/bed
concepts and factory coordination geometry. Equipment boxes represent external
envelopes or explicit space allowances; supplier internal CAD is not claimed.

The package includes a fixture BOM and two-bar stock cutting plan, process and
inspection routes, utility gaps, unsent RFQs, gross elastic/handling screens and
a pilot-versus-programme capacity comparison. Fixture retention/clamps/joints,
full mould/bed details, railway load/resistance checks and site structures remain
open development work; stage 6 has not been performed.

The next design gates follow the current adverse results: resolve unsupported
stressing-bed buckling, check the Pi20 transfer top-tension hypothesis against
project concrete limits, develop the 103.56 t Pi25 lifting demand into an actual
crane/rigging/runway design, and establish site ground/foundation inputs. The
four-position pilot's assumed 1.615 accepted beams/working day is separate from
the 54/day programme case; scaling that case requires at least 134 positions
under the same bed assumptions before other production bottlenecks.

## Design scope

The [second iteration](../../engineering/factory_examples/examples/development.md)
develops both factories together: Brauer workholding candidates and connection
demands, three prestress layouts along Pi20/Pi25, ground-spring buckling
and imperfection sensitivity for the 26 m bed return path, and a dedicated
125 t crane-runway bay. The balanced 48-strand candidate stays within a declared
dead-load zero-tension research screen, while increasing initial bed force to
7.392 MN and known Pi25 lifting equivalent to at least 104.69 t. These are new
design alternatives; original failed cases remain retained, and no structural
or supplier acceptance follows from these numerical screens.

The mechanical package covers production tooling and its interfaces with
vehicle parts. It does not release a bogie frame, articulation, lifting appliance
or complete train. Use the existing vehicle geometry and installed inventory;
retain bought-in precision items until compatible products and rights are known.

The civil package covers the canonical beam manufacturing envelope and the
factory/yard coordination structures. Gross elastic demand is a screen. Complete
prestress/reinforcement, cracking, shear/torsion, fatigue, bearings, foundations,
temporary stability, erection and replacement remain design work with their own
inputs and acceptance. Keep factory handling loads separate from railway loads.

Show a pilot precast yard's actual assumed casting positions and bottlenecks
beside the programme's illustrative 54 beams/day case. A small example factory
must not inherit that programme output. Similarly, a single vehicle assembly
lane is not proof of Baghdad's required annual fleet delivery rate.

## Supplier evidence and procurement

Use the [37-case assessment](../commercial/baghdad-uk-factory-suppliers-2026-10-15.md)
as the enquiry map, then identify actual offered models and factories. Record
published machine dimensions, working envelope, table/payload limits, supply
requirements and relevant duty conditions. Where a bespoke supplier publishes
no dimensioned model, reserve a clearly labelled engineering allowance and
request a general arrangement; do not invent a manufacturer specification.

Separate machine purchase, tooling, software, extraction, guarding, handling,
building/foundations, delivery, Iraqi duties, installation, training, qualification,
spares and recurring costs. Published UK retail prices are dated comparisons,
not Baghdad quotations. Keep unknown costs unknown and propagate incompleteness.

Prepare unsent technical RFQ packages with exact process requirements, sample
parts, factory acceptance/site acceptance criteria, origin evidence and Baghdad
service questions. UK-content financing and physical manufacturing origin remain
separate quantities; no revised financing saving is adopted automatically.

## Validation and ownership

Production engineering owns process routes and capability trials; mechanical
engineering owns fixture/vehicle interfaces; civil engineering owns structures,
ground and construction stages; electrical/MEP engineering owns utilities;
procurement owns comparable technical/commercial returns. These are accountable
roles, not appointed people.

Run focused numerical/contract tests, adverse fit/handling/layout cases,
deterministic artifact checks and actual installed CAD export/reopen checks.
Retain original source/toolchain and artifact hashes. Preserve failed or unknown
checks rather than changing limits to manufacture acceptance. Complete the
appropriate repository validation profiles before committing the buildout to
`main`; the separate four-profile software-release gate remains unchanged.
