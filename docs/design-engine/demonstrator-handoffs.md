# Civil and station demonstrator handoffs

These compact handoffs connect existing calculations to the next engineering
experiments. They do not generate another design portfolio or run native solvers.
Generate them from the repository root into fresh directories:

```bash
python -m engineering.design_search.civil_demonstrator build --output build/civil-demonstrator
python -m engineering.design_search.civil_demonstrator verify --output build/civil-demonstrator
python -m engineering.design_search.station_demonstrator build --output build/station-demonstrator
python -m engineering.design_search.station_demonstrator verify --output build/station-demonstrator
```

Use the project's Python environment. Existing output directories are refused;
choose a new directory for a subsequent source revision. Keep these reproducible
outputs outside Git. Verification rejects changed sources, mixed identities and
resealed edits; it does not authenticate measurements or grant physical approval.

The **civil handoff** joins the current 18 geometries to their material quantities,
manufacturing routes, low/base/high scoped costs, handling assumptions and 189
conditional mechanics cases. It preserves the load context, vehicle selection,
quantity, section and evaluation identities. A bounded shortlist retains a
representative of each of the six structural families for further experiments;
the remaining candidates stay available with deferred reasons. This is an
experimental ordering, not a selected bridge or railway.

Partial analytical mechanics do not complete the first engineering stage.
Resistance, cracking, reinforcement/prestress, shear, torsion, fatigue, local
connections, temporary stability, bearings, foundations and site evidence remain
open. Costed mass reserves add gravity and price, not stiffness or strength.
Lifting still needs actual crane capacity at radius, lift points and ground
support. The two-shift factory and civil resource estimates are not executable
machine, crew, curing, transport or erection schedules. Global beam deflection
does not establish relative rail-to-stator or vehicle-to-primary clearances.

The **station handoff** uses the selected vehicle schema directly. It keeps the
physical vehicle, journey adapter, selection, requirements, motor and brake
identities distinct, and binds the existing T05 force/thermal, T07 independent
braking and T08 full-train service protocols to that subject. These are three
unexecuted requests within the wider test programme; approved procedures,
acceptance limits, as-built articles, measurements and independent review remain
required.

The civil load record and station subject must share the exact selected vehicle,
vehicle evaluation and selection identities. A regression checks this common
context; it does not equate a civil alternative with the journey adapter or select
a combined railway.

For the current normal-load 2 km analytical case, required peak launch force is
about **11.10 kN per car**. That is demand, not available motor thrust. The station
screen identifies a **900 m shared winding**; the separate conditional journey
uses a **500 m leading-point command window**. They have different coordinate and
engagement meanings, and their equivalence has not been established. This handoff
imports no synthetic journey results or motor map. T05 records secondary position
relative to the primary; T08 records leading-nose route chainage.

The 120-second headway and 8,280 passengers/hour/direction remain a target and
formation arithmetic. Section handoff, protected separation, berth and tail
clearance, repeated thermal duty, adverse journeys, stopping and recovery require
their own evidence. Neither handoff selects a new physical reference or grants
manufacturing or operating release.

Regression check:

```bash
python -m pytest -q --import-mode=importlib \
  engineering/design_search/tests/test_civil_demonstrator.py \
  engineering/design_search/tests/test_station_demonstrator.py
./osr verify
```

On 3 November 2026, all 80 focused tests passed under both Python 3.12 and 3.13;
the current dossier verification also passed. The checked civil handoff is
`746c67ef934565353694e138e7c7ef94c9e63608cb7ccd61850d235e9df45fda`;
the station evaluation is
`4257c863079dee9cd58ac323b9099811e7b42362934e48d3aaf6fd22c46b0fe2`.
Neither command performs a new physical test or independently reproduces the
stored civil mechanics. The handoff tests exercise consistency and planning
contracts, including adversarial source, identity and payload changes.
