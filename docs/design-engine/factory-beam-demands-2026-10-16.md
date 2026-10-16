# Baghdad Pi-beam railway and handling demand development

The [source-bound review](factory-beam-demands/index.html) adds moving axle
demands and four-point handling geometry to the common `factory-precast`
problem. Both Pi20 and Pi25 fail the declared zero-tension diagnostic using the
retained **three-car** reference. The current six-car Baghdad axle allocation
remains unknown. No railway resistance or lifting arrangement is accepted.

The [six-case comparison](factory-beam-demand-comparison.json) retains verified
request/attempt hashes, variables, metrics, checks, handling demands and unknown
installed costs. A fresh native baseline confirms 376 bed objects and two
OpenSees spatial-frame cases; these confirm bed geometry and gross first-order
frame correspondence, not concrete beam qualification. All nine original factory
examples and the earlier handover and snapshots remain unchanged historical
evidence. The new snapshot is bound to this continuation's sources.

## Railway diagnostic

The retained [vehicle/civil trace](../../engineering/industrialisation/vehicle-civil-load-trace.json)
contains a three-car, twelve-axle AW2 planning reference, total mass 105,750 kg.
Its forces use 9.81 m/s²; those historical forces are preserved, with an explicit
mass-balance check. Beam gravity and handling retain the factory examples'
9.80665 m/s² convention. Neither reference establishes current six-car loading.
The multiplier is an OSR sensitivity, not an adopted code dynamic factor.

At a fixed section, the moving influence line is piecewise linear in train
origin. Entry, exit and axle-under-section events therefore give its maximum.
Each resulting branch is piecewise quadratic along the span when combined with
the retained uniform gravity and end patches. The solver checks interval ends
and interior stationary points, giving a continuous maximum sagging moment for
this one-dimensional, downward-load model. It also evaluates support-reaction
entry/exit events. This avoids treating a train-position grid as an exact peak.

The existing gross, prismatic, uncracked section, straight full-force tendons,
local elastic-shortening and additional-loss hypotheses remain in force.
Additional live bending is superposed without a new prestress-loss credit.
Fibre stresses are evaluated at 41 declared sections; no continuous stress or
deflection envelope is claimed. Top minimum compression occurs with the train
off the span; top maximum and soffit minimum use maximum sagging moment. The
[CSV](factory-beam-demands/beam-service-demands.csv) retains all three, with
compression positive and tension negative.

| Case | Diagnostic axle multiplier | Total peak moment, MNm | Minimum sampled compression, MPa | Most negative handling moment, MNm | Nominal lower-leg tension, kN |
| --- | ---: | ---: | ---: | ---: | ---: |
| Pi25, balanced 48 strands, lift at 0.2L, vertical lower legs | 1.0 | 4.145 | −8.121 | −0.636 | 250.530 |
| Pi20, otherwise same | 1.0 | 2.864 | −1.479 | −0.433 | 204.049 |
| Pi25, axle sensitivity | 1.5 | 5.053 | −13.045 | −0.636 | 250.530 |
| Pi25, lift at 0.25L | 1.0 | 4.145 | −8.121 | −0.943 | 250.530 |
| Pi25, lower legs 45° from vertical | 1.0 | 4.145 | −8.121 | −0.636 | 354.303 |
| Pi25, balanced 40 strands | 1.0 | 4.140 | −11.661 | −0.635 | 250.071 |

All cases retain adverse diagnostic checks. Passing the earlier dead-load screen
does not clear the railway diagnostic. The Pi25 baseline peaks at x = 12.935 m,
train origin −1.465 m; its maximum total support reaction is 777.081 kN.
Material compression/tension limits remain null. Transfer, transmission/end
zones, reinforcement, shear, torsion, fatigue, cracking and railway dynamics
remain unresolved. The [FHWA prestressed beam example](https://www.fhwa.dot.gov/bridge/lrfd/pscus056.cfm)
illustrates separate service stress evaluation; its US example properties and
allowables are not adopted as Baghdad requirements.

## Handling and British equipment enquiry

The calculation uses the same concrete/strand gravity and end patches as the
retained beam model. It finds lifting-station reactions and exact overhang
moment extrema for those distributed loads. A 1.25 research factor applies to
beam forces and moments; the existing 2,000 kg rigging assumption enters hook
demand only. Missing reinforcement, attachments and a supplier-defined complete
rig prevent a complete mass or crane-capacity check.

For Pi25 at 0.2L, the 81,750.175 kg known beam mass gives 501.060 kN at each
station, x = 5 and 20 m. The factored beam-only handling moments range from
−0.636 to +0.410 MNm. Nominal four-leg equalization gives 250.530 kN per vertical
leg; a two-effective-leg hypothesis gives 501.060 kN. At 45°, nominal tension
rises to 354.303 kN and each nominal insert receives 250.530 kN horizontal force.
These are hypotheses, not an approved load-sharing or insert design.

The enquiry concept has one longitudinal spreader and two transverse
distributors, with four lower lift points 1.435 m apart across the beam.
Its 15 m longitudinal span at 30° upper slings from vertical needs **12.990 m
above the longitudinal end units**, before hook block, rig hardware, lower
distributors and beam clearance. Pi20 needs 10.392 m above those units. Moving
Pi25 stations to 0.25L reduces that geometric requirement to 10.825 m but
increases hogging demand to −0.943 MNm. Actual crane hook height and usable site
headroom remain unknown.

The [interface supplier register](../../engineering/design_engine/data/factory-interface-suppliers.json)
adds a configuration-specific Modulift enquiry. Its
[manufacturing page](https://www.modulift.com/manufacturing/) describes UK
manufacture with European steel processed in the UK; its
[contact page](https://www.modulift.com/contact-us/) identifies the factory in
Poole, England. This supports priority investigation as British manufacture.
Origin of each offered beam component, sling and shackle still needs evidence.

The [MOD 110 page](https://www.modulift.com/mod-110-tonne-spreader-beams/) gives
a maximum model class of 110 t and individual component masses, including
178 kg end units, 45 kg drop links and 367 kg 4 m struts. The
[MOD 110H page](https://www.modulift.com/mod-110h-tonne-spreader-beams/) gives
a maximum model class of 170 t. These figures do not establish capacity at
15 m or a complete rig mass. The
[2024 catalogue](https://www.modulift.com/wp-content/uploads/2024/02/Modulift-UK-Product-Catalogue-2024-Lo-Res.pdf),
printed pages 6–7, provides load/span charts at 30° STV; no chart ordinate or
accepted configuration is adopted here.

The [unsent enquiry](factory-beam-demands/interface-rfq.csv) requests the exact
span/angle load chart, strut schedule, full three-member arrangement, complete
mass, component origin, equalization, insert side loads, applicable load-factor
and WLL basis, certification and Baghdad supply/service price. Accepted capacity,
complete rig mass and price remain null. Tilt, unequal sharing, local concrete
breakout, transverse torsion, suction, transport and wind need separate work.

## Reproduction and remaining design work

The native baseline charged four evaluations: compilation/screening, FreeCAD
and two OpenSees cases. The six scenarios charged six screening evaluations;
they do not inherit native confirmation from the baseline.

```sh
.venv/bin/python tools/automation/design-engine.py --store build/my-beam-study run --problem factory-precast --city baghdad --revision my-beam-study --refine --evaluations 4 --wall-seconds 180
.venv/bin/python tools/automation/publish-factory-review.py --check --current --output docs/design-engine/factory-beam-demands
.venv/bin/python tools/automation/factory-buildout.py --check --output docs/design-engine/factory-buildout
```

Use a fresh store/revision for new candidates and fresh export/publication
directories. Previous handover verification checks retained historical integrity;
it does not claim applicability to these changed sources. The local
`factory-native` gate now requires integrity of this new snapshot as well as the
three earlier snapshots and fresh execution of the nine original models and
both common factory adapters.

The next beam design iteration needs an accepted six-car axle layout and load
combinations, concrete/strand/transfer evidence and a declared service stress
basis before selecting a section, tendon layout and reinforcement. The handling
iteration needs lift-age material properties, insert and distribution design,
complete mass and an actual crane/headroom envelope. Numerical completion and
supplier research do not close those engineering inputs or stage 6 qualification.
