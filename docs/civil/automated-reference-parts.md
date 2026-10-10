# Automated reference parts and full-train variants

[Generated review](../../engineering/civil_exploration/examples/automated-parts-review.json)
· [native and operating evidence](../../engineering/civil_exploration/examples/automated-parts-evidence.json)
· [complete native assembly](../../design/component-catalogue/models/cad/reference-full-train.FCStd)
· [native CAD receipt](../../design/component-catalogue/models/cad/reference-full-train.native.json)
· [saved-file audit](../../design/component-catalogue/models/cad/reference-full-train.audit.json)
· [industry source register](../../engineering/reference-parts/industry-basis.json)
· [default choices](../../engineering/reference-parts/default-variant.json)
· [compiler](../../engineering/civil_exploration/variant_compiler.py)
· [OSR-ENG-002 generation requirements](../standards/OSR-ENG-002.md).

The compiler generates a complete planning train and regenerates its reference
part geometry, installed datums, mass/CG/inertia, spatial dynamics inputs,
mechanical/electrical/thermal/control interfaces, battery quantities, inspection
requirements and coverage register from one set of design choices. It uses the
existing catalogue part IDs and authoritative operational family definition.

The default six-car variant contains **192 instances, 191 joints, 12 bogies,
24 wheelsets and 48 wheel contacts**. Its computed planning mass is
**200,490.108 kg**. This is a reference design study with residual synthetic
mass allocations, rather than a released supplier train.

## Industry examples and their actual use

| Primary source | Adopted input or practice | Remaining evidence |
|---|---|---|
| [Toshiba railway application](https://www.global.toshiba/jp/products-solutions/battery/scib/about-scib/application/railway.html) | Type3-23 nominal 27.6 V, 45 Ah, approximately 15 kg, 190 × 361 × 125 mm module envelope | Purchased-part revision, tolerances, impedance/OCV maps, current limits, installation, rail/fire/vibration release |
| [SKF axlebox architecture](https://evolution.skf.com/en/the-evolution-of-railway-axlebox-technology/) | Separate axlebox/bearing and wheelset responsibilities; provision for condition sensing | Bearing dimensions/fits/load ratings, supplier mass, speed/temperature sensor installation |
| [Continental secondary suspension](https://www.continental-industry.com/global/en/products-solutions/airsprings-suspension/railway/secondary-suspension) | Air-spring and auxiliary-support installation architecture | Force/displacement/damping curves, emergency operation, actual envelopes and life |
| [Pandrol Fastclip](https://www.pandrol.com/products/fastening-systems/fasteners/fastclip) | Captive fastenings and configurable replaceable pad stiffness inform infrastructure coverage requirements | Clip/pad/insulator geometry, tested properties, supplier loads and inspection data |
| [NASA systems engineering handbook](https://www.nasa.gov/reference/system-engineering-handbook-appendix/) | Units, coordinate systems, endpoint responsibilities and requirements-to-verification traceability | Project-owned interface approval and measured verification |

Only Toshiba's listed nominal module data supplies numerical supplier-reference
inputs. The other manufacturer sources guide architecture; their proprietary
part geometry or numerical load ratings have not been reconstructed. Reference
axleboxes, springs, motors and gearboxes use explicitly assumed mass and simplified
OSR envelopes. The existing wheelset, frame and body CAD remain reference models.

## Consistent battery generation

The default battery is a **28-series × 4-parallel** arrangement of 112 modules
per car: 772.8 V nominal, 180 Ah, 139.104 kWh nominal and 111.2832 kWh over the
declared 10–90% SOC window. It is an **LTO study alternative** to the existing
catalogue's LFP battery. Its part ID is an allocation link, not approval to
substitute chemistry or reuse the LFP supplier release.
Toshiba's [Type3 system-components description](https://www.global.toshiba/content/dam/toshiba/ww/products-solutions/battery/scib/pdf/BatterySystemComponents-en.pdf)
identifies the lithium-titanate cell architecture.

Each installation includes a generated base with eight clearance holes, lid,
four enclosure walls and eight reference fastener stacks. Every module and
enclosure/hardware feature has a cutlist identity. The compiler sums independently
declared module mass and assumed-density OSR enclosure/hardware mass, with analytic
primitive inertia and the parallel-axis theorem. It does not turn the enclosing
module volume into active-material mass.

Changing the parallel-string count regenerates width, installed mass/inertia,
Ah/kWh, pack resistance, current limits, heat capacity, cooling conductance,
SOC histories and conditional range/recharge estimates. The pack's DC model
solves `P = I (V - I R)` and retains electrical and thermal energy balances.
Discharge consumes chemical energy; regeneration increases it while generating
positive resistive heat. A lumped temperature uses exact constant-power Newton
cooling within each duty segment.

Resistance, current limits, cooling conductance, thermal capacity, SOC window
and temperature limit are **OSR research assumptions**, listed separately from
Toshiba's nominal data. This is a constant-OCV, equal-current-sharing screening
model. It does not resolve cell hot spots, protection logic, coolant hydraulics,
age-dependent impedance or SOC-dependent voltage. Conditional range uses an
explicit assumed 20 kWh/train-km; charging assumes 600 kW/train. These estimates
do not establish route autonomy, traction capability or station dwell feasibility.

## Expanded running gear and mass reconciliation

Each wheelset allocation expands into the wheelset and two separately identified
axleboxes. Each bogie expands primary and secondary suspension kits into four
primary spring/guide envelopes and two air/auxiliary spring envelopes. Powered
bogies additionally instantiate two motors and two gearboxes. Their masses are
deducted from the original wheelset/frame aggregates before dynamics assembly.
Axlebox mass stays unsprung; frame-mounted component mass stays in its bogie group.

The six-car total reconciles exactly to the frozen planning tare plus the change
from the old 2,500 kg/car battery allocation. Body/frame residual masses still
represent components that have not been individually resolved. Their inertia
remains a uniform research approximation, not an as-built tensor. The suspension
parts map to the existing reduced six-direction joint laws; generating envelopes
does not derive spring rates from geometry.

## Coverage and interfaces

The six-car catalogue produces **1,367 required allocation slots**. The compiler
maps 114 to explicit reference components and reports **1,253 unresolved slots**.
The earlier published 737-slot allocation belongs to the three-car catalogue;
these totals use different families. Coverage records every required slot,
representation, evidence state, joint/interface mappings, acceptance requirements
and model limitations. Unresolved kit/area/length allocations remain visible.
Planning mass closure is distinct from complete production component coverage.

All 191 physical joints have mechanical interface records that identify local
datums, units, signs and endpoint responsibilities. Battery interfaces add
electrical, thermal/fluid and control contracts. Unknown connector/protection,
hydraulic and latency capabilities remain open. Validation rejects stale model
identity, missing/unknown endpoints, mismatched joint mappings, wrong units and
invalid declared limit intervals. It cannot approve compatibility where supplier
port capabilities are absent.

Geometry validation rejects malformed primitives and invalid/overlapping holes.
Battery bay screening rejects overlap with the reference inner-wheel/bogie
envelopes and excess width/height. This is a specific installation check, not a
complete train clearance, cable-routing or removal-envelope certification.

## Generate, verify and run

Use fresh output folders to retain previous evidence:

```sh
tools/automation/osr-python tools/automation/compile-reference-parts.py generate \
  --output build/engineering/my-reference-parts

tools/automation/osr-python tools/automation/compile-reference-parts.py verify \
  --output build/engineering/my-reference-parts

tools/automation/shared-engineering-freecad.sh \
  --model build/engineering/my-reference-parts/model.json \
  --output build/engineering/my-reference-train.FCStd

tools/automation/osr-python tools/automation/verify-reference-parts-freecad.py \
  --model build/engineering/my-reference-parts/model.json \
  --cad build/engineering/my-reference-train.FCStd \
  --output build/engineering/my-reference-train.audit.json

tools/automation/osr-python tools/automation/shared-service-envelope.py run \
  --model build/engineering/my-reference-parts/model.json \
  --config build/engineering/my-reference-parts/spatial_configuration.json \
  --output build/engineering/my-reference-service --cases empty-15mps
```

Pass `--choices path/to/choices.json` to generate another architecture. For the
shorter three-car planning modules, reduce series modules to fit the bay; 20
series modules is a tested example across all five authoritative families.
Invalid variants fail before outputs or analysis can be accepted.

The package includes `model.json`, `spatial_configuration.json`, `battery.json`,
`interfaces.json`, `coverage.json`, `manufacturing.json`, `mass_properties.json`,
`joint_register.json`, `verification.json`, source inputs and a hash-bound receipt.
Verification checks retained output/source hashes and recompiles every result.
CAD uses the same embedded primitive definitions and actual installed datums;
the native solver and projected drawing edges are checked independently.
The elevation/plan scale adjusts to the complete family length.
The native audit reopens the saved file, solves the restored assembly, checks
all installed instance placements and tests generated reference solids against
independent OpenCASCADE volume/inertia integrals. Legacy body/frame/wheelset
geometry remains under its existing reference-model limitations.

Research packaging and mass checks, numerical completion, engineering constraint
approval and physical validation remain separate states. Inspection methods and
nominals are generated with acceptance limits open. The automated battery
retention pattern is ready for simultaneous six-resultant bolt-group screening;
preload, plate prying, fatigue and assembly-specific native submodels still require
actual materials, mounting geometry and loading evidence.

The full operating matrix, independent full-family time/mesh convergence,
geometry-specific local strength/fatigue, traction/brake maps, coolant/controller
coupling and physical asset measurements remain required. Historical two-car
proofs retain their original producing commit and are not relabelled as tests of
this new full-train variant.

## Retained verification outcome

The focused suite passed **108 tests**, including 24 new reference-part tests.
Native FreeCAD 1.1.4 generated and reopened the 192-instance assembly, solved all
191 joints and produced four nonempty drawing projections. The saved-file audit
checked 164 distinct reference primitives against independent analytic volume
and inertia calculations. The drawing remains unissued.

FreeCAD emits subshape-reference restoration diagnostics for the detached
whole-feature joints. The audit checks the restored solver and actual installed
placements independently; these pass. This does not establish supplier fits or
physical attachment capacity.

The fresh complete six-car passage attempt used `dt=0.005 s`, two deck elements
per span and 2 m rail spacing. It failed nonlinear convergence at **9.775 s**,
with a reported trial residual of approximately **2.0493e7 N**. The campaign
retains all converged history through 9.770 s and its failed-case receipt.
No full-train passage or time/mesh convergence is accepted from that attempt.
The other 21 planned cases remain unexecuted. Resolving this coarse-run failure
and independently refining the full-train operating cases is the next numerical
qualification task, separate from the completed part-generation and CAD checks.
