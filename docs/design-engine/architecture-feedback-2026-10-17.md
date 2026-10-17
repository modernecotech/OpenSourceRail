# Provisional architecture feedback — 17 October 2026

This continuation follows the instruction to develop provisional designs while
keeping acceptance gates open. The [review packet](architecture-feedback/index.html)
propagates vehicle mass and spacing changes through **12 architecture cases** and
**193 beam geometries**, producing **2,316 beam response records**. A separate
lighter-frame search retains **192 alternatives**. Two selected beam definitions
passed native FCStd/STEP export and reopening. These are local research results;
no architecture, material, supplier configuration or manufacturing release is adopted.

The [whole report](architecture-feedback/report.json),
[mechanical study](architecture-feedback/mechanical.json),
[equipment investigation](architecture-feedback/equipment.json) and
[demand CSV](architecture-feedback/architecture-demands.csv) retain failed cases,
explicit assumptions and unresolved requirements.

## Vehicle changes remain separate from the six-car planning train

| Case family | Known model mass | Train length | Axles | Complete 6 m platform modules |
|---|---:|---:|---:|---:|
| Original LM3 reference | 105.750 t | 49.5 m | 12 | 9 = 54 m |
| LM3 with 1.8 / 2.0 m gaps | 105.750 t plus unclosed gap equipment | 53.1 / 53.5 m | 12 | 10 = 60 m |
| LM3 with gaps and previous deep box-frame proposal | 149.141 t plus unclosed gap equipment | 53.1 / 53.5 m | 12 | 10 = 60 m |
| LM3 with 1.8 m gaps and lighter built-up I proposal | 124.118 t plus unclosed gap equipment | 53.1 m | 12 | 10 = 60 m |
| Separate six-car planning control | 384.000 t | 111 m | 24 | 20 = 120 m |
| Separate six-car +20% mass sensitivity | 460.800 t | 111 m | 24 | 20 = 120 m |

The last two families each include longitudinal car CG offsets of −0.5, 0 and
+0.5 m. No LM3 steel increment or new gap is transferred into them. They retain
their separate assumed bogie geometry. The 460.8 t case is a sensitivity, not an
accepted supplier mass or a redesign with six LM3 cars.

The LM3 cases preserve all 12 original axle IDs and each car's actual source axle
offsets. Gaps translate complete cars and their axles. Added members use explicit
car CG/bogie equilibrium. Original source forces retain their 9.81 m/s² convention;
new steel additions use 9.80665 m/s², with force and first-moment checks against that
mixed convention. Equal axle sharing remains a hypothesis. Vertical/lateral CG,
new gangway/services mass and actual replacement-net steel mass remain unknown.

The [scaled diagram](architecture-feedback/architecture-layout.svg) centres each
train on its full-module platform reservation. A 2 m allowance is reserved at
each end before rounding up to complete modules. The earlier 116 m six-car branch
requires a partial closure module; it cannot be described as twenty unchanged
6 m modules. The new 120 m reservation does not establish site fit, egress,
station structure or route acceptance. Planning body cells in the diagram are
assumptions, not a supplier general arrangement.

## Lighter chassis branch and preliminary stock geometry

Fourteen of the 192 built-up I alternatives pass the declared local stiffness
screen; **none fit the existing 260 mm sill-height envelope**. The lowest added-mass
passing branch has 750 mm-deep side members, 40 mm flanges, 8 mm webs and an 8 mm
wall hypothesis for the 220 × 380 mm centre spine. Its gross new-member addition is
**6,122.648 kg/car**, compared with **14,463.625 kg/car** for the previous box branch.
Both conservatively retain the existing car mass rather than deducting unidentified
members. These figures are not an accepted vehicle mass saving.

| Preliminary stock item | Quantity/car | Research dimensions |
|---|---:|---|
| Side I-member flange | 4 | 16,000 × 180 × 40 mm |
| Side I-member web | 2 | 16,000 × 670 × 8 mm |
| Proposed hollow centre spine | 1 | 15,800 mm long, 220 × 380 mm outer section, 8 mm wall |

The lighter branch gives approximately **11.650 mm** deflection against the
12.3 mm research target under the assumed rigid transverse compatibility model.
Its clear-web depth/thickness ratio is 83.75. Plate buckling, lateral restraint,
crossmembers, weld fatigue, local attachments, crashworthiness and strength remain
unqualified. Material grade, stock supply, long-member cutting/handling, any splice
design, welding/straightening route and process qualification are unresolved.
The dimensions above are preliminary geometric definitions, not an issued cut list.

The 750 mm depth also requires coordinated floor, doors, batteries, lifting pads,
bogie/suspension and loading-gauge changes. Braking, traction, rescue and factory
handling/resource requirements reopen with the mass change. The impact ledger
retains the mandatory gates for all 63 potentially affected packages through
their dependencies; it does not claim that those packages have been redesigned.

## Beam and factory demand feedback

The 193-geometry family varies section depth, stem width, strand count, requested
strand packing ratio and lift station. It includes the original 48-strand seed
and failed shallow/high-strand geometries. Exact moving-load events feed sampled
transfer, service and handling fibre calculations for 20/25 m spans. The 1.25 force
multiplier is an explicit sensitivity, not an adopted railway dynamic factor.
Train-off stress extremes are included. Resistance, end zones, reinforcement,
losses, fatigue, dynamics and full material/process qualification remain open.

Representative local selections are:

| Case | Section / strands | Minimum sampled service compression | Initial bed demand | Known hook equivalent |
|---|---|---:|---:|---:|
| LM3, 1.8 m gaps and heavy frame | 1.4 m depth, 0.30 m stems, 96 strands | +0.031 MPa | 14.784 MN | 119.233 t |
| LM3, 1.8 m gaps and lighter I frame | 1.155 m depth, 0.30 m stems, 112 strands | +0.231 MPa | 17.248 MN | 106.186 t |
| Six-car 384 t, ±0.5 m car CG | 1.4 m depth, 0.30 m stems, 112 strands | +0.057 MPa | 17.248 MN | 119.607 t |
| Six-car 460.8 t, ±0.5 m car CG | 1.4 m depth, 0.30 m stems, 144 strands | +0.993 MPa | 22.176 MN | 120.356 t |

These positive values establish sampled stress screens only. Small positive
values are not structural reserves. Maximum compression demands and failed
checks remain in every case report; no material resistance is accepted. Hook
figures exclude unresolved reinforcement, attachments and complete rigging.
The 22.176 MN bed demand exceeds the previous 17.248 MN hypothesis and requires
new head/seat, return system, supports and foundation qualification.

Requested packing ratios must not be confused with actual counts. The 112-strand
case with a requested 0.75 lower ratio packs **80/112 lower strands (71.43%)** after
row rounding. The 144-strand equivalent packs **112/144 (77.78%)**. Physics and
native geometry use the actual points; selected summaries expose actual counts.

Vehicle demand records include translational kinetic energy and braking force at
the inherited 80 km/h / 1 m/s² research condition, plus two/four-point lifting
sensitivities. These omit rotating mass, grade, resistance, brake/adhesion sharing,
regeneration, repeated-stop thermal duty and actual lift reactions. They do not
approve a brake, drive or lifting system.

## British equipment cases: useful limits, no automatic selection

**CCL Stressomatic MKII:** the manufacturer's flyer states UK design/manufacture.
The published maximum design load is 247 kN, with short-jack retracted length
833 mm, width 160 mm, height 234 mm, 110 mm main cylinder, 194 mm stroke and
9.6–15 mm strand range. The research force of 154 kN is below the published load,
but **15.2 mm exceeds that stated strand range**. The previous hypothetical
90 mm × 200 mm tool cannot inherit this unit's geometry. [CCL flyer](https://www.cclint.com/wp-content/uploads/2024/02/CCL-Stressomatic-MKII-250-kN_Flyer.pdf).

At 60 mm strand pitch, a 110 mm cylinder and adjacent 15.2 mm straight tail give
−2.6 mm clearance **if they occupy the assumed common axial plane**. This rejects
that envelope hypothesis; it is not proof of collision between actual supplier
shapes. The 833 mm length also fails the previous 250 mm tier reservation.
Actual nose/body positions, hoses, operator access, stroke/seating, tail cutting,
lock-off and detensioning sequence remain mandatory. A custom or alternative jack
requires its own evidence; this investigation qualifies none.

**Macalloy 1030:** a British manufacturing lead for an alternative tension-bar
return concept. The public product page states 26.5–75 mm carbon bars and lengths
up to 11.8 m, with couplers for longer assemblies. These published dimensions
support an enquiry concept only; they establish no system design load, bar count,
coupler/anchorage capacity or replacement for the existing compression rails.
The manufacturer's detailed downloads require login and were not accessed.
[Product](https://macalloy.com/products-services/post-tensioning/),
[Dinnington manufacturing history](https://macalloy.com/about/history/),
[download access](https://macalloy.com/downloads/brochures/).

**Mechan lifting jacks:** the Sheffield manufacturer publishes a 5–40 t family
and an actual historical supply of 30 t jacks. The new report compares the
49.714 t known loaded-car subtotal against elementary two/four-point demands.
A nominal 30 t unit is a configuration enquiry lead, not a selected or accepted
jack. Stroke, support geometry, stability, synchronisation, bogie-removal path,
floor foundations, exact offered origin and Baghdad support remain unknown.
The 10 t component crane receives no whole-car lifting credit.
[Lifting-jack family](https://www.mechan.co.uk/rail/lifting-jacks/),
[historical 30 t supply](https://www.mechan.co.uk/kiwirail-bears-fruit-for-mechan/),
[manufacturing facility](https://www.mechan.co.uk/about-mechan/).

British manufacture remains the priority. Manufacturer statements and published
families do not authenticate the origin of a future offered configuration.
No supplier was contacted and no equipment was ordered.

## Reproduction and acceptance

```sh
./osr design campaign architecture --output build/architecture-feedback/new-run --native
./osr design campaign verify-architecture --output build/architecture-feedback/new-run
./osr design campaign verify-architecture-snapshot \
  --destination docs/design-engine/architecture-feedback
```

The completed local run is `build/architecture-feedback/final-2`. Fresh output
directories preserve previous attempts. The published packet retains FCStd,
inputs, all response records, CSV and SVG. STEP and execution logs stay in the
sealed local run. Native geometry confirms the declared solids and reopened
exports; it does not qualify structural resistance or manufacture. Verification
checks hashes and explicit case/gate correspondence; it does not recompute the
studies. Historical verification uses frozen inputs without regenerating the
current planning train.

The existing 472 unissued production artifacts, 416 unperformed inspections and
unaccepted project/supplier inputs remain open. This continuation creates no
approvals or physical results and does not alter the earlier source baselines.

Validation passed 172 design/automation tests, including equilibrium, source-cache
invalidation, architecture separation, module rounding, diagram alignment and
artifact/gate checks. Both native geometry checks passed. Desktop (1,440 px) and
mobile (390 px) reviews checked all 20 links with no page overflow or browser errors.
