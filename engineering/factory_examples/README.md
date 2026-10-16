# Mechanical, civil and factory development examples

The [development handover](../../docs/design-engine/factory-buildout/index.html)
records delivered stages 1–5 and remaining engineering/qualification work.
The common adapter now includes a
[376-object complete nominal bed](../../docs/design-engine/factory-whole-bed/index.html)
and an independently checked gross spatial frame. These original nine model
files and reports remain unchanged.

Develop representative Baghdad production tooling, pi-beam manufacturing and
factory coordination from versioned inputs and dated UK supplier information.
Start with the [visual review](examples/index.html), [generated design notes](examples/README.md)
and [staged plan](../../docs/design-engine/mechanical-civil-factory-plan-2026-10-16.md).

The first iteration contains four native FreeCAD/STEP models: a datum fixture,
a Pi25 mould/stressing-bed concept, a six-car component/assembly hall and a
four-position pilot precast yard. Equipment solids are sourced external envelopes
or explicitly labelled bespoke space reservations, rather than manufacturer CAD.

The [second iteration](examples/development.md) adds fixture workholding,
three full-span prestress alternatives, a bed-restraint stiffness and
imperfection study, and a dedicated crane-runway bay. The package retains
seven native models and a [standalone engineering figure](examples/development.svg).
The [development inputs](data/development.json) keep proposed loads, layouts and
unknown material/site/supplier limits separate.

The [fabrication iteration](examples/connections.md) adds a perforated strongback
end and retained locator-button coupon, taking the package to nine native models.
It retains failed grip/plate fits, individual-strand stressing stages, nominal
section/contact demands, restraint-compliance budgets and UK subcontract routes.
Edit [connection inputs](data/connections.json) and
[fabrication supplier facts](data/fabrication-suppliers.json) for that work.

Edit [design assumptions](data/basis.json) and the [supplier register](data/equipment.json),
then regenerate locally:

```sh
.venv/bin/python -m engineering.factory_examples.build --output build/factory-examples-new --native
.venv/bin/python -m engineering.factory_examples.build --check
.venv/bin/python -m pytest engineering/analysis/tests/test_factory_examples.py engineering/analysis/tests/test_factory_development.py engineering/analysis/tests/test_factory_connections.py -q
```

`models.py` owns geometry and demand screens. `build.py` owns deterministic
reports, SVG plans, BOM/cutting plans, process routes, utility gaps and unsent
RFQ registers. `native.py` executes installed FreeCAD, checks actual solid volume,
bounds and fixture interference, and reopens FCStd and STEP. Native logs and
bootstrap scripts remain under ignored `build/factory-examples-native/`.

`development.py` owns the new contact, full-span prestress, beam-column restraint
and runway interface calculations. Its buckling and imperfection solvers have
independent Euler and sinusoidal-bow controls; proposed ground stiffness and
clamp preload remain unmeasured. Numerical dependencies use the existing local
engineering Python toolchain, with versions recorded in the development output.

`connections.py` owns grip/plate clearances, aligned-return-axis and individual
stressing sequences, nominal strongback demands and the locator's fit/retention
concept. Native export checks actual drilled/stepped solids and positive-volume
interference for the declared steel subsets. Grip, screw and thread envelopes
remain distinct from the solids checked for fabrication correspondence.

The [common-engine integration](../../docs/design-engine/factory-integration-2026-10-16.md)
registers `factory-fixture` and `factory-precast` problems for shared jobs, budgets,
comparison views, per-instance inventories and source-bound native exports.
Run `./osr validate run --profile factory-native` for mandatory fresh execution
of all nine original models and both common adapters. Impact selection includes
this profile for factory inputs, code and retained evidence.

The [common support/scheduling continuation](../../docs/design-engine/factory-support-notes-2026-10-16.md)
extends that adapter to 93 native objects and resource-calendar comparisons.
Its inputs and review belong to the common engine; these nine original model
files and reports remain retained unchanged.

`--check` now checks retained byte integrity separately from numerical
recomputation using declared SI tolerances. Original reports and CAD remain
unchanged; [reproduction.json](examples/reproduction.json) distinguishes their
producer identity from the current verifier. Matplotlib paths are views of the
checked JSON, not portable numerical evidence. Explicit `--seal-retained`
re-verifies unchanged originals after verifier changes; it refuses altered
original files. Generate changed engineering examples into a fresh directory.

No supplier quote, contact, physical qualification, adopted city CAPEX or railway
release is created. British manufacture, Northern Ireland manufacture and a
UK-supplied imported saw are distinguished. Factory completeness, civil resistance
and exact process compatibility remain visible review gates in the output.
