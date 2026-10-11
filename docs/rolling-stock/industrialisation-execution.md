# Executed trainset industrialisation expansion

[Implementation plan](industrialisation-expansion-plan.md)
· [generated review](../../engineering/industrialisation/modernisation/review.json)
· [execution evidence](../../engineering/industrialisation/modernisation/execution-evidence.json)
· [industry source register](../../engineering/industrialisation/modernisation/sources.json)
· [machine-readable programme](../../engineering/industrialisation/modernisation/programme.json)
· [OSR-MFG-001](../standards/OSR-MFG-001.md)
· [native battery datum fixture](../../design/component-catalogue/models/cad/battery-datum-fixture-reference.FCStd)
· [native fixture receipt](../../design/component-catalogue/models/cad/battery-datum-fixture-reference.native.json).

The six repository work packages in the plan are implemented. They expand the
existing shared train model and factory definitions with callable screening,
planning, trace-validation and offline commissioning tools. The current six-car
reference yields **117 material passports, 117 process routes and 756 assembly
operations**, linked to **16 existing factory packages, 10 manufacturing controls
and 416 first-article characteristics**. Physical qualification remains open.

## Delivered implementation

| Package | Implemented behaviour | Verification and physical boundary |
|---|---|---|
| IM-01 design | Eight source-backed improvements bind automation, redundancy, monitoring, traction, HVAC, doors, acoustics and modular materials to existing part IDs | Missing sensor/latency/common-cause evidence remains visible; CCTV is not reclassified as an obstacle safety sensor |
| IM-02 materials | Per-product passports preserve existing material/process candidates; coupon mass/stiffness, layered conduction and duty-energy tools compare explicit inputs | No grade/strength/fire/fatigue/EPD release is inferred from a lighter material or supplier envelope |
| IM-03 assembly | Six-restraint fixture, signed tolerance stacks, parent/child preparation and handback dependencies | Native locator positions/volumes and two drawing projections checked; clamp capacity, deflection, calibration and physical repeatability remain required |
| IM-04 production | Open travelers, CSV exports, offline work instructions and capacity/wait-aware scheduling | Actual operation times and qualified process windows remain null; synthetic scheduling demonstrations are not factory forecasts |
| IM-05 quality | Exact identity/revision/lot checks, calibrated range/expiry, environment, uncertainty decisions, torque/angle traces, process-window sampling and NCR blocking | Outputs only prepare independent review; they never approve physical work or change ERP status |
| IM-06 commissioning | Offline lifecycle and critical-fault contract, bounded auxiliary reset and movement inhibition | Computational fault cases pass; real TCMS/ATP/ATO, redundancy timing, sensor coverage and GoA4 evidence remain open |

The reference fixture now places all six locators on pads, supported brackets,
outriggers and base members. Its kinematic rank is six. These solids are an
inspectable datum study rather than released load-bearing shop drawings.

Materials examples are explicitly synthetic. For the same coupon geometry,
lower-density materials reduce mass while lower modulus increases deflection.
Changing thickness updates both mass and bending stiffness; an assumed strength
or carbon factor is not silently supplied. The duty comparison conserves energy
and exposes effects of declared mass, traction/regeneration efficiencies,
resistance and auxiliaries. It does not verify CRRC's energy-saving claim.

## Run and inspect

Use a fresh output folder for each controlled generation:

```sh
tools/automation/osr-python tools/automation/factory-modernisation.py generate \
  --output build/engineering/my-factory-programme

tools/automation/osr-python tools/automation/factory-modernisation.py verify \
  --output build/engineering/my-factory-programme

tools/automation/osr-python tools/automation/factory-fixture-freecad.py \
  --fixture build/engineering/my-factory-programme/assembly_package.json \
  --output build/engineering/my-battery-fixture.FCStd
```

Supply `--model` and `--battery` together to bind another compiled train variant.
The package retains those inputs, source hashes, JSON requirements/passports/
operations/protocols, the blank traveler, synthetic method demonstrations,
`assembly-operations.csv`, `material-passports.csv`, `work-instructions.md` and
an immutable receipt. Verification checks outputs and recompiles generated data.

For an actual work order, retain the generated blank template and create a
separate controlled execution package/record. Bind it to the identified as-built
configuration, issued family-specific drawings, complete part allocations,
released acceptance criteria and qualified process windows. Fill actual physical
serials/lots, operators, independent inspectors, timestamps, calibrated evidence
and NCR dispositions. Reconcile its revision/hash whenever the approved package
changes. Reference aggregate rows cannot substitute for resolved physical parts.

```sh
tools/automation/osr-python tools/automation/factory-modernisation.py assess \
  --output build/engineering/my-factory-programme --record path/to/actual-record.json
```

The default reference package remains blocked: it is as-designed, has no physical
asset identity and lacks complete production allocations, released criteria and
special-process data. Assessment of that template cannot become an approval.

## Design and factory handoff still required

The detailed LM3 manufacturing packages must undergo family-transfer review for
six-car geometry, loads, datums and supplier interfaces. The reference LTO battery
is also an alternative to the catalogue's LFP candidate, requiring an approved
substitution/design release. No selected adhesive, cure recipe, weld authority,
torque setting or fire-rated material is issued by this expansion.

Execute physical pilots in the plan's order: battery mounting, representative
bogie, carbody/door/HVAC bay, then full-train commissioning. Collect first-pass
yield, scrap, rework causes, actual cycles, repeatability and repair/removal time
before claiming factory improvements. The existing full-train contact-domain
rejection at 9.13 s remains a service gate. Supplier, process, physical and
independent railway/safety evidence cannot be closed by software demonstrations.

## Retained verification

**42 focused tests pass**, including 30 new tests for this expansion and the
existing fabrication-twin and production-schedule checks. They cover identity,
stale/tampered evidence, expired tools/materials, uncertainty margins, process
sampling, NCR/predecessor holds, fixture rank, resource limits, energy balance,
critical fault lockout and withdrawn movement qualification.

The generated package was verified by source/output hashes and recompilation.
Native FreeCAD 1.1.4 checked all 15 fixture solids and their positions/volumes,
and generated two nonempty projections with 49 plan and 36 elevation edges.
The independent six-restraint check passes. All 13 offline commissioning cases
pass their software contracts; physical commissioning and fixture qualification
remain unperformed.
