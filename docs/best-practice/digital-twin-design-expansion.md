# Research incorporated into the design twin

The [interactive design review](../../engineering/models/digital-twins/best-practice/index.html)
and [native FreeCAD assembly](../../engineering/models/digital-twins/best-practice/reference-twin.FCStd)
contain original OSR study designs installed in the shared six-car model.
The [STEP detail export](../../engineering/models/digital-twins/best-practice/reference-twin.step)
provides portable geometry for one car's additions and the infrastructure study.
The [complete twin JSON](../../engineering/models/digital-twins/best-practice/reference-twin.json)
contains the actual shared model, interfaces, infrastructure and analytical cases.
The [machine review](../../engineering/models/digital-twins/best-practice/review.json)
is the authority for counts, source hashes, mass changes and open gates.

These are concrete parameterised designs and executable model additions.
Supplier selection, construction release and physical acceptance remain open.
The existing catalogue and its 24 kW HVAC default have not been silently promoted
to this alternative configuration.

## Research traversal

The [research graph](../../engineering/twin_design/data/research-graph.json)
records the executed search queries, reviewed primary-source nodes, followed
publisher links and remaining branches. Research followed product pages into
technical documents and verification context, for example:

- [Liebherr modular HVAC](https://www.liebherr.com/en-int/aerospace-and-transportation-systems/solutions-and-services/solutions-for-railway/plug-play-hvac/plug-and-play-hvac-7174981)
  → publisher downloads → [MACS technical brochure](https://assets-cdn.liebherr.com/versions/de503e8d-bb31-4aa2-8e5c-b6717cb3a11c/original/)
  and equipment-test resources;
- [Roxtec rolling-stock sealing](https://www.roxtec.com/en-ca/knowledge-library/application-areas/cable-sealing-and-cable-clamping-for-rolling-stock/)
  → transit frames, plastic-conduit fire protection, clamping and installation;
- [Pandrol fastening overview](https://www.pandrol.com/products/fastening-systems/fasteners/fastclip)
  → baseplate and two-pad technical sheets;
- [Texas Instruments precharge reference](https://www.ti.com/tool/TIDA-050063)
  → its design guide; and
- [NIST digital-twin implementation scenarios](https://www.nist.gov/publications/use-case-scenarios-digital-twin-implementation-based-iso-23247)
  → the linked implementation report.

The broader search also reviewed bearing replacement, gangway route-motion
measurement, wheel-sensor installation, connector guidance, bonding processes,
precast tolerance responsibilities, tool setting records, grounding and
running-gear diagnostics. The expanded [source register](../../engineering/best_practice/data/sources.json)
and [handbook](handbook.md) retain publisher, date, findings and limitations.
Search recursion is bounded and reviewed; the tool does not ingest arbitrary
web pages into a design or silently refresh an accepted configuration.

## Design decisions and their implementation

| Change | Concrete geometry and twin behaviour | Remaining qualification |
|---|---|---|
| Modular HVAC with a one-module-out study margin | Four candidate module envelopes per car, original drained carrier, mounting feet and hole pattern; thermal cases and explicit mass addition | Actual supply voltage/conversion, ambient derating, airflow, ventilation, refrigerant, roof loads and installed comfort |
| Replaceable door installation | Paired cassette envelopes, folded steel channel carriers, surveyed header holes and threshold datums; isolated LV power and separate control ports | Supplier cassette, body portal, seals, sensitive edges, emergency release, retention loads and physical interlocks |
| HV service panel and isolated LV conversion | Removable cabinet, segregation wall, contactor/fuse/resistor reservations and separate converter envelope; original circuit topology and RC study | Creepage/clearance, switching/protection ratings, bleeder discharge, converter isolation, EMC and actual controller |
| Cable support and barrier penetrations | Separate HV/LV trays, replaceable open transit frames and sensor reservations; configuration-bound interfaces and inspection IDs | Actual cable/connector routes, strain relief, sealed insert build-up, fire tests and sensor implementation |
| Maintainable rail seats | Original perforated bolted baseplates, two pads, toe insulators, bushings, washers and anchors; per-seat stiffness converted into the distributed support model | Anchor embedment, pad curves, toe/longitudinal restraint, fatigue, electrical insulation and rail-structure interaction |
| Bearing replacement interfaces | Fixed/guided/free reservations, accessible cap seats and jacking pads, thermal-movement demand | Actual bearing capacity/travel, reinforcement, staged lifting loads, synchronized jacking and authority release |

The [component schedule](../../engineering/models/digital-twins/best-practice/component-schedule.csv)
records physical study quantities rather than treating a car kit as a fully
decomposed component. Catalogue allocation groups remain explicit. New mapped
groups are marked **partial original study decomposition**: the unmodelled
contents and supplier internals remain open.

The [input file](../../engineering/twin_design/data/design-inputs.json) distinguishes
public candidate information from OSR assumptions. The HVAC brochure provides a
1,000 × 1,600 × 220 mm single-module envelope and nominal 8 kW cooling; the
product page supplies the approximate 125 kg mass. These are external candidate
data, with actual purchase revision and environmental/electrical conditions open.
Door, cabinet, carrier, rail-seat and jacking geometry is original OSR design.
No supplier clip, patented sensor clamp, proprietary circuit board or normative
standard text is copied.

## A failed case led to a design change

The initial three-module arrangement has 24 kW nominal capacity. Under the OSR
study assumptions of 45°C ambient, 9.5 kW combined internal/solar gain,
500 W/K conductance and a 26°C setpoint, maintaining the setpoint requires
19 kW cooling. Losing one module leaves 16 kW; the lumped model reaches about
29.17°C after 30 minutes and fails the declared 27°C study limit.

The proposed four-module arrangement retains 24 kW nominal capacity after one
failure and holds 26°C in the same model. The original failed case is retained
beside the proposal. This is conditional sizing evidence: fresh-air and latent
loads, actual climate, supplier derating, air distribution and physical comfort
tests are still required. The 27°C limit is an OSR study policy, not an ISO
acceptance value.

The proposal adds one reference 125 kg module per car, or 750 kg across six
cars. That increment is explicit. Other newly decomposed equipment is extracted
once from the original synthetic residual-body allowance. Mass, CG, inertia,
static reactions and the spatial vehicle matrices are recalculated. The
three-module allowance inside that residual is a declared OSR assumption;
physical mass closure still requires actual supplier and measured values.

Rail pads similarly reach the numerical model: the two assumed 60 MN/m pads in
series produce 30 MN/m per rail seat. Two rails at 0.6 m spacing give a
100 MN/m² distributed foundation modulus. The historical adapter key ends in
`_n_m`, but its tributary-length operation uses N/m². The conversion and
dimensional meaning are recorded explicitly in the review.

## Executed checks and boundaries

The [native audit](../../engineering/models/digital-twins/best-practice/reference-twin.native.json)
records installed Assembly solving, saved/reopened geometry, joint datums,
actual occupied-volume checks, independent OCC primitive inertia, drawing edges
and STEP round-trip volume. It does not qualify the synthetic context body's
door openings, structural capacity or a fire barrier. An open frame is an
installation interface, not a certified seal.

The [original circuit](../../engineering/models/digital-twins/best-practice/precharge.svg)
and [netlist](../../engineering/models/digital-twins/best-practice/circuit.json)
include positive/return contactors, a separate resistive precharge path, bus
capacitance, an unresolved bleeder and load. The declared 150 Ω / 6 mF study
reaches 95% at about 2.70 s; its tolerance corner is about 3.11 s. Required pulse
energy with the stated margin is 4,009.5 J. No resistor or contactor rating is
accepted. Offline cases reject open HVIL, insulation fault, wrong feedback,
movement and timeout; the model controls no physical switch.
The closure decision helper is stateless. Persistent fault latching, switching
sequence, observation freshness, authorised recovery and target-controller
implementation remain required work.

The [coupled smoke check](../../engineering/models/digital-twins/best-practice/spatial-smoke.json)
retains four integration steps over 0.02 s with the new train masses, CG/inertia
and distributed rail-pad input. It is an integration check, with its initial
live-load transient and limitations retained. It does not establish time/mesh
convergence, ride comfort, structural serviceability or a complete passage. The
existing [six-car contact-domain issue](../civil/full-train-contact-domain.md)
remains open. Neither that issue nor physical acceptance is closed by these
design additions.

## Reproduce and extend

```bash
tools/automation/osr-python tools/automation/design-best-practice-twin.py \
  generate --output build/engineering/my-design-study
tools/automation/osr-python tools/automation/design-best-practice-twin.py \
  verify --output build/engineering/my-design-study
tools/automation/osr-python tools/automation/design-twin-freecad.py \
  --package build/engineering/my-design-study \
  --output build/engineering/my-design-study/reference-twin.FCStd
tools/automation/osr-python tools/automation/design-twin-smoke.py \
  --package build/engineering/my-design-study \
  --output build/engineering/my-design-study/spatial-smoke.json
tools/automation/osr-python -m pytest -q engineering/analysis/tests/test_design_twin.py
```

Use fresh output paths to retain earlier evidence. Only canonical input changes
are published with `--publish`; generated JSON, HTML, CSV and SVG are checked
against recompilation. CI verifies the published design, native artifact hashes
and meaningful software tests. Native execution is recorded separately; CI does
not claim to rerun FreeCAD or perform physical tests.

Next research branches are actual contact profiles, tunnel fire/ventilation,
stationary storage/PV protection, approved connector and refrigerant selections,
and route-specific gangway/crash endurance. Extend the existing standards thread
and [OSR-BP-001](../standards/OSR-BP-001.md) with project applicability, adopted
clauses, acceptance limits, procedures and independent decisions before release.
