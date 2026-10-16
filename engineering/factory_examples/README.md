# Mechanical, civil and factory development examples

Develop representative Baghdad production tooling, pi-beam manufacturing and
factory coordination from versioned inputs and dated UK supplier information.
Start with the [visual review](examples/index.html), [generated design notes](examples/README.md)
and [staged plan](../../docs/design-engine/mechanical-civil-factory-plan-2026-10-16.md).

The first iteration contains four native FreeCAD/STEP models: a datum fixture,
a Pi25 mould/stressing-bed concept, a six-car component/assembly hall and a
four-position pilot precast yard. Equipment solids are sourced external envelopes
or explicitly labelled bespoke space reservations, rather than manufacturer CAD.

Edit [design assumptions](data/basis.json) and the [supplier register](data/equipment.json),
then regenerate locally:

```sh
.venv/bin/python -m engineering.factory_examples.build --native
.venv/bin/python -m engineering.factory_examples.build --check
.venv/bin/python -m pytest engineering/analysis/tests/test_factory_examples.py -q
```

`models.py` owns geometry and demand screens. `build.py` owns deterministic
reports, SVG plans, BOM/cutting plans, process routes, utility gaps and unsent
RFQ registers. `native.py` executes installed FreeCAD, checks actual solid volume,
bounds and fixture interference, and reopens FCStd and STEP. Native logs and
bootstrap scripts remain under ignored `build/factory-examples-native/`.

No supplier quote, contact, physical qualification, adopted city CAPEX or railway
release is created. British manufacture, Northern Ireland manufacture and a
UK-supplied imported saw are distinguished. Factory completeness, civil resistance
and exact process compatibility remain visible review gates in the output.
