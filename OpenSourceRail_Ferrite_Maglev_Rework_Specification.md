# OpenSourceRail ferrite permanent-magnet maglev redesign

## Rework input specification — revision A, 20 October 2026

**Purpose:** define a separately modelled, costed and tested maglev vehicle/guideway family for OpenSourceRail. This is an engineering development specification, with numerical targets and an auditable cost model. It is not a fabrication release or an assertion that the proposed magnetic circuit has already met its targets.

**Repository baseline:** `modernecotech/OpenSourceRail`, commit `50010ce56370cf6b22dc383c12eebbc224800007`, committed 20 October 2026. Existing repository values are planning/design values unless their source identifies measured hardware. All financial amounts are USD. Estimates preserve the repository's local-production pricing basis; they are not construction tenders or independently escalated October 2026 market quotations.

**Proposed family identifier:** `ferrite-pm-maglev-study`. Add an explicit architecture branch. Preserve the current wheel/rail family as the comparator until the new variant passes its own engineering gates. This handoff contains proposed input data; it does not modify the repository.

### Selected study baseline and revised construction estimate

The primary study combines a rigid 17 m car, onboard ferrite PM-biased attractive lift on broad horizontal faces, short active guidance stations, onboard linear propulsion, and a passive narrow guidebeam. The same ferrite budget must cover every permanent magnet used by lift, guidance and propulsion. Shaped-pole passive vertical restoring suspension remains an explicit alternative.

| Baseline input/result | Study value | Status |
|---|---:|---|
| Ferrite | 3 t/car; 4 t sensitivity | Material allocation, not proven lift capacity |
| Battery | 225 kWh/car; 150 kWh option | Matched-current comparison; smaller option needs route proof |
| Tare at 3 t ferrite / 225 kWh | 18.75 t/car | Aggressive complete-vehicle mass target |
| AW3 at same configuration | 30.75 t/car | Derived from 160 passengers at 75 kg |
| Maximum initial acceleration / DC draw cap | 1 m/s² / 600 kW per car | Acceleration tapers with speed |
| Narrow concrete section for comparison | 0.8 m × 1.6 m hollow box | Illustrative, pending structural/magnetic/egress design |
| Mature three-car train factory-gate cost | $0.764m / $0.872m / $1.130m | Low/base/high engineering allowances, matched 675 kWh |
| Elevated civil cost per dual-direction route-km | $7.048m / $8.346m / $10.529m | Revised narrow-beam scenarios; current reference $9.748m |
| First three-car pilot programme | $9.0m / $23.22m / $55.2m | Separate scope, including first article and test infrastructure |

The revised civil base case supersedes the earlier $9.038m/km generic screen. It holds passive rail supply at $600 per single-direction beam-m and explicitly adds long evacuation-walkway brackets. A separate $350/beam-m rail-manufacturing target reduces the same base geometry to about $7.846m/km; geometry alone does not establish that lower rail price. These are conditional planning scenarios, not statistical confidence intervals.

## 1. What is being designed

Develop a nominal 17 m long passenger car using inexpensive sintered hard-ferrite permanent magnets, integrated magnet carriers, onboard electromagnetic propulsion and stabilisation, and a passive elevated guidebeam. The vehicle has no rotating traction motor, gearbox, wheelset, axle bearing or conventional wheel bogie in normal running. Permanent magnets provide the steady suspension bias. Powered windings produce propulsion, guidance and the stabilising forces required by the chosen magnetic geometry.

The design objective is **no mechanically moving running gear**. Three-car couplings and gangways still articulate; doors, HVAC, optional cooling pumps, charging contacts and emergency hardware have their own moving functions. Every added mechanism must be visible in the mass, cost, maintenance and fault models. Do not claim that all motion or all maintenance has disappeared.

Use a single structural guidebeam per direction, with as many passive magnetic faces or reaction surfaces on that beam as the electromagnetic circuit requires. "One rail" defines the civil beam arrangement, not a requirement to make one undifferentiated steel surface perform every force function. Two directions normally require two beam alignments. No active route stator or route-length permanent-magnet array is assumed. Station/depot charging, signalling and communication equipment remain.

Mainline switch elimination is a user requirement. Route topology, terminal turnback and recovery must be redesigned around it; removing switches from a drawing does not preserve the former service plan. Depot switching is an explicit exception.

### Requirements inherited from the proposal

| ID | Requirement | Interpretation for rework |
|---|---|---|
| SYS-001 | Nominal car length 17 m | Define whether this includes end interfaces; check coupler pitch and the three-car overall envelope |
| SYS-002 | Ferrite permanent magnets | Sintered hard ferrite, grade and temperature-dependent properties to be qualified |
| SYS-003 | Onboard active equipment | All suspension/propulsion windings and power electronics on the car; guideway magnetic elements passive |
| SYS-004 | No rotating running gear | Preserve the functions of support, guidance, braking, parking, capture and recovery in the replacement architecture |
| SYS-005 | Stationary hover in normal service | Zero-speed lift AND stability must be demonstrated; protection power and controlled landing remain required |
| SYS-006 | Small load-dependent vertical movement | Initial target 5 mm AW0→AW2; define AW3 travel separately |
| SYS-007 | Integrated construction | Share qualified structural carriers and services; ferrite blocks do not replace the primary crash/bending load path |
| SYS-008 | No mainline switches | Rerun terminal, headway, failure recovery and depot access models |
| SYS-009 | Local fabrication and low repeat cost | Price manufactured assemblies, fixtures, yield, labour and inspection, not raw magnets alone |
| SYS-010 | Battery/station charging | Retain 225 kWh/car as the matched comparison; evaluate 150 kWh/car as a charging-dependent option |

Width 2.65 m, 80 km/h initial service target, 1 km station spacing, 60 s dwell and 45 s effective charging are study assumptions. They must be replaced by route requirements before design freeze. Retain a 90 km/h comparison case because the current LM3 specifies 90 km/h; cost and energy savings must not depend silently on reduced service performance.

## 2. Current design and comparison boundaries

The current detailed LM3 reference is a three-car, 49.5 m train with nominal 16.5 m modules, a controlled 78.75 t tare target, 360 AW2 passengers and 480 AW3 passengers. It uses 675 kWh gross / 540 kWh usable LFP. Its controlled mass contains 75.308 t of modeled items plus 3.442 t of reserve. The existing lightweight study is not the promoted product reference.

The current factory-gate estimate is $885,205.42 per three-car train: $682,431.18 of direct materials/supplier modules, $55,240 of labour and a 20% unexpected-cost premium. The rounded city planning allowance is $900,000. The comparison in this specification uses the precise build estimate for train deltas and the active $9.748 million per elevated dual-direction route-km for civil deltas.

Current OpenSourceRail already uses onboard batteries and station charging. There is no additional catenary-removal credit. The same applies to signalling, evacuation, stations and other functions that remain necessary.

Baghdad's active city model is a separate six-car, 111 m family with 720 AW2 / 960 AW3 passengers, 1,350 kWh gross batteries, and a $1.68 million planning allowance per set. Its 809 sets cannot be replaced by 809 three-car maglevs while preserving capacity. A preliminary equal-passenger-capacity extrapolation can use six proposed cars, but it still needs platform, loading, performance, fleet, reserve, coupling and cost redesign; multiplying the three-car price by two is only a screening calculation.

## 3. Vehicle geometry and mass allocation

### 3.1 Geometry and accommodation

Retain the LM3 passenger-function baseline: longitudinal seating, accessible boarding, wheelchair spaces, emergency access, door obstruction protection, saloon-isolated batteries, externally serviceable equipment and passenger information. Establish a new general arrangement showing the central beam intrusion, cabin floor, magnetic wrapping arms, evacuation walkway, equipment access and crash load paths. The old floor height and underfloor envelopes cannot be inherited without a section drawing.

Use three 17 m nominal cars for the initial engineering family, approximately 51 m before any unresolved interface-length adjustment. This is not automatically a platform-compatible substitution for 49.5 m LM3. Preserve AW2 = 120 and AW3 = 160 passengers per car for screening. The initial mass model uses 75 kg per passenger; luggage and the operator's approved loading standard must be reconciled before structural release.

### 3.2 Target mass ledger, per car

| Assembly | 3 t ferrite, 150 kWh case (t) | Basis and boundary |
|---|---:|---|
| Structural body, floor, doors, glazing and interior | 6.40 | Aggressive allocation; new load paths and 17 m geometry require CAD/FEA and a weighed BOM |
| Ferrite permanent magnets | 3.00 | Included in tare; four-tonne sensitivity adds exactly 1.00 t here |
| Combined magnetic/electrical running system | 2.70 | All soft-iron cores, windings, structural magnet carriers, retention/encapsulation, drives, gap sensors, module wiring and traction cooling; no double-counted integration credit |
| Fixed landing/capture and emergency support/braking | 0.60 | Provisional function allocation; mechanism and stopping concept not selected |
| Battery pack | 1.50 | 150 kWh at assumed installed 100 Wh/kg, including its own pack housing/BMS/thermal equipment |
| HVAC and ducts | 0.80 | Cabin HVAC only; battery and magnetic cooling already assigned above |
| Auxiliary electrical systems, controls and wiring | 0.60 | Train-level equipment; local magnetic controls are assigned to the 2.70 t package |
| Couplers, gangway interfaces and roof solar | 0.60 | Packaging allocation; mounting and actual solar area to be resolved |
| Unallocated growth reserve | 1.80 | Do not consume invisibly or reuse as a saving |
| **Target tare** | **18.00** | Development target, not a demonstrated mass closure |

The 6.40 t body allocation and 2.70 t combined magnetic system are the largest unresolved allocations. Do not infer their feasibility by subtracting the weight of a conventional motor/gearbox from the current train. Replace allocations by component quantities, density, CAD mass, supplier mass and measured first-article values as work progresses.

| Case | Ferrite/car | Gross battery/car | Tare/car | AW2/car | AW3/car | Three-car tare |
|---|---:|---:|---:|---:|---:|---:|
| Current LM3 | — | 225 kWh | 26.25 t | 35.25 t | 38.25 t | 78.75 t |
| M3-225, matched battery | 3.0 t | 225 kWh | 18.75 t | 27.75 t | 30.75 t | 56.25 t |
| M4-225, matched battery | 4.0 t | 225 kWh | 19.75 t | 28.75 t | 31.75 t | 59.25 t |
| M3-150, reduced battery | 3.0 t | 150 kWh | 18.00 t | 27.00 t | 30.00 t | 54.00 t |
| M4-150, reduced battery | 4.0 t | 150 kWh | 19.00 t | 28.00 t | 31.00 t | 57.00 t |

The matched-battery 3 t case reduces target tare by 28.6% and AW3 mass by 19.6%. Those are vehicle-load reductions, not whole-viaduct cost reductions. Every case retains the same passenger payload. The difference between 150 and 225 kWh is a modelled 0.75 t/car at the assumed pack density.

MASS-001: export mass, centre of gravity, inertia tensor, support positions, uncertainty and evidence for every assembly. Include magnet mass exactly once. Include all cold plates, cables, fasteners, covers, gap sensors and field shielding. Retain a separate growth reserve and produce a mass-closure ledger for each battery/magnet variant.

## 4. Magnetic architecture decision

Carry two alternatives into an initial field/geometry study; do not combine their equations as though they were the same circuit.

**Alternative A — PM-biased attractive suspension.** Onboard ferrite/Halbach arrays lift toward an appropriately located iron surface above the lifting poles, with active gap stabilisation. A variable equilibrium gap can minimise steady coil current as load or temperature changes. It is compatible with zero-speed lift, but magnetic attraction is vertically unstable without control. More load does not necessarily mean the car sinks; the lift gap may become smaller.

**Alternative B — PM-excited shaped poles and passive C-shaped rail.** Geometry provides a vertically restoring force as pole alignment changes. This is closer to the requested "sink a few millimetres under load" behaviour. Lateral unstable directions still require active control at rest and in motion. The optimal arrangement may use ferrite blocks feeding shaped poles instead of retaining the original flat Halbach pattern.

Use A with wide horizontal lifting faces and separate short guidance stations as the primary geometry to investigate for a rigid car without moving running gear. Keep B as the explicit alternative for the passive vertical load response. This is an initial engineering choice, not a qualified suspension selection. Select the released circuit only after field maps, curve geometry, manufactured rail costs and failure behaviour have been compared. The technical appendix provides published antecedents and their evidence limits.

Increasing magnet volume cannot make motion-induced electrodynamic lift persist at rest over an ordinary unpowered conductor. Likewise, permanent magnets and ordinary iron do not provide unconstrained stable suspension in all required directions by size alone. The design is PM-biased active maglev, with passive guideway hardware and active onboard control.

### 4.1 What 3 tonnes of ferrite establishes

At an assumed density of 5,000 kg/m³, 3,000 kg occupies 0.60 m³. A packaging seed is two strips, each 12 m × 0.5 m × 0.05 m, totaling 12 m² of face area. If built from 50 mm cubes, this is 4,800 blocks; a 24-module division contains 200 blocks and 125 kg of ferrite per module. These are arithmetic packaging equivalents, not a released Halbach orientation pattern or proof of lifting force.

At the user's $7,000 per 3 t assumption, ferrite costs $2.333/kg, $7,000/car or $21,000/three-car train. A fourth tonne adds approximately $2,333/car of raw material. Machining, magnetisation orientation, inspection, breakage, fixtures, carrier, retention, encapsulation, winding manufacture, cooling, sensors and drives are additional. The cost model prices these separately.

For M3-225 at AW3, static lift must equal 301.66 kN. Distributed over the seed 12 m² face area, that is 25.14 kPa of average vertical pressure. An ideal normal Maxwell-pressure analogy would require approximately 0.251 T at the working surface. With a preliminary 1.3× load screening multiplier this becomes 392.15 kN and approximately 0.287 T. This analogy indicates the scale of the field requirement; it does not predict the force of either proposed magnetic circuit. Use nonlinear, finite-length force maps and a measured rig to establish the actual required ferrite mass.

The 1.3 screening multiplier is a project assumption, not a regulatory load factor or a complete dynamic load combination. Fault redistribution, wind, cornering, body flexibility, uneven passenger loading and guideway motion must be sized independently.

### 4.2 Load movement and temperature

AW0→AW2 adds 9,000 kg or 88.29 kN per car. A 5 mm load-induced movement target requires average incremental vertical stiffness of 17.658 MN/m. AW3 adds 12,000 kg: the same linear stiffness would require 6.67 mm movement, or 23.544 MN/m to remain within 5 mm. This incremental requirement is identical for the 150/225 kWh and 3/4 t magnet cases because their passenger-load increments are the same.

For a shaped-pole circuit, distinguish vertical pole overlap from the physical lateral gap. For an attractive circuit, distinguish equilibrium lift gap from carbody motion. Keep the nominal 8 mm magnetic gap as a study point until a tolerance budget proves that normal motion, manufacturing errors and protection clearances fit within it.

Use grade-specific temperature curves. TDK documents a typical negative ferrite remanence coefficient near −0.18%/K; the earlier −0.20%/K is retained only as a conservative sensitivity. With that sensitivity, Br = 0.43 T at 20°C becomes 0.3784 T at 80°C, and an unsaturated B² force scaling is 77.44% of its 20°C value. Real force, active correction and demagnetisation margins require the actual circuit. Qualify cold reverse-field demagnetisation as well as hot operation.

## 5. Curves, structural integration and the air-gap budget

This is a design gate with direct implications for the user's low-part-count objective. A straight 12 m active assembly facing a curved rail has a chord-to-arc deviation approximately L²/(8R). At R = 100 m, this is 180 mm; at R = 300 m, 60 mm. These are horizontal deviations on a horizontal curve: they do not automatically consume an 8 mm VERTICAL lift gap. An 8 mm allowance in the direction of the deviation would imply approximately 2,250 m radius if the entire length had to follow the same narrow curved face. Splitting the magnets into 1 m blocks does not remove the global error when all blocks are fixed along a straight underframe.

The primary candidate uses broad horizontal lifting surfaces so horizontal sweep consumes overlap width. With endpoint-centred chord placement, a conservative surface width is magnet-strip width plus twice the maximum lateral offset plus separate edge/tolerance margins. Before those margins, a 0.5 m strip needs approximately 0.86 m of face at R100 or 0.62 m at R300. Short guidance poles must separately tolerate local heading mismatch. Broad lifting faces do not solve vertical crests/sags, guidebeam twist or magnetic edge-force changes. The geometry appendix quantifies the options.

Evaluate four concrete resolutions: a lifting face broad enough for the swept lateral offset with guidance allocated separately; short support clusters with geometry designed around their support stations; shorter articulated structural vehicle sections; or a much larger permitted route radius. Compact support clusters reduce available magnetic area and can increase required magnet/core mass. Broad pole faces increase guideway material. Articulation adds moving joints. Large radii change route fit. Cost and reliability comparisons must use the selected solution, not the best property of each incompatible option.

GEO-001: publish a three-dimensional swept-envelope analysis on tangent, minimum horizontal radius, vertical curves, cant transitions, beam ends and depot routing. Verify every active face, cover, capture rail, platform interface and evacuation path.

GEO-002: create a gap budget with independent terms for rail manufacturing, erection/shimming, beam bending/twist, bearing movement, thermal expansion, carbody bending/twist, load-induced movement, control tracking error, sensor bias/noise and wear/debris. Differentiate absolute structure deflection from relative magnet-to-rail displacement. No term may be silently set to zero because it is not present in the old wheel/rail model.

GEO-003: integrate magnet carriers into a continuous qualified frame, but retain positive block containment after cracking, bonding failure and crash loads. Ferrite is a ceramic material and is not the primary tensile, bending, impact or fatigue chassis structure. Use common brackets, crossmembers and service channels where the actual load path permits.

GEO-004: determine ride quality using a flexible vehicle/guidebeam model. The 5 mm load-movement stiffness alone produces a several-hertz heave mode in a single-body approximation. This is not proof of comfortable suspension. Evaluate whether electromagnetic control provides adequate disturbance isolation without a mechanical secondary suspension.

## 6. Propulsion, braking, battery and thermal requirements

### 6.1 Propulsion configuration

The train still contains a motor in the functional sense: it is a linear electromagnetic machine with no rotating rotor or gearbox. Put its powered windings on the vehicle. Evaluate a short-primary linear induction motor against a flux-switching/flux-reversal permanent-magnet machine whose windings and magnets are both on the mover and whose long reaction rail is passive iron. The costed reference budgets passive ferromagnetic functional rail, so the second option is the initial cost-model topology. A linear-induction alternative must also price its conductive secondary. Shared magnetic cores are an optimisation subject to coupled lift/thrust maps, not an automatic removal of the propulsion system's mass.

Allocate the 3/4 t TOTAL permanent-magnet budget explicitly between lift, guidance and propulsion. The 12 m² packaging seed uses the entire 3 t as a flat lift array; it cannot simultaneously supply an additional separate PM motor without reallocation or added magnet mass. Start with shared mechanical carriers and separately controllable windings; claim shared magnetic volume only when the coupled model demonstrates it.

For every point in the service envelope, export thrust, lift, lateral force, cogging, force ripple, input power, copper/core losses, rail losses and thermal state. Include rail joints, end effects, reverse running, regeneration, shorted windings and supply-voltage limits. Propulsion acts against the external guideway; forces entirely between components fixed to the same chassis cannot propel the car.

### 6.2 Power envelope

Start with an 800 V nominal DC study bus, 600 kW total DC discharge cap per car, 1 m/s² maximum initial acceleration and 1 m/s² service deceleration. These are proposed inputs. Current LM3 motor shaft-power ratings are not directly comparable to this total DC input cap.

At M3-225 AW3, acceleration alone at 80 km/h requires 683.3 kW mechanical. With 1 kN assumed magnetic drag, CdA = 3 m², air density 1.2 kg/m³ and 70% drive efficiency, plus 40 kW onboard services, holding 1 m/s² to 80 km/h would require approximately 1.08 MW DC per car. A 600 kW cap requires acceleration tapering. Do not advertise both unrestricted 1 m/s² to top speed and a 600 kW cap.

At 800 V, 600 kW implies approximately 750 A total DC current; 450 kW station input implies 562.5 A before interface losses and auxiliary-load splitting. Phase current, back-EMF, busbar heating, interruption rating and cable mass require the actual motor and pack voltage range. An MCU does not switch these currents directly; isolated gate drives and power semiconductors do.

### 6.3 Duty cycle and capacity

The accompanying reproducible energy calculation integrates one 1 km level segment with acceleration tapering, 80 km/h limit, regeneration, aerodynamic and assumed magnetic drag, and 60 s station dwell. Normal services are allocated 40 kW/car: 10 kW suspension/control, 25 kW HVAC and 5 kW other auxiliaries. These are assumptions to replace with measured loads. A hotter/lower-efficiency sensitivity uses 60 kW services, 55% drive efficiency and 35% regeneration recovery.

Keep 225 kWh/car for the matched-current cost and reserve comparison. Evaluate 150 kWh/car only after a route energy and charger-availability simulation. Under a chosen 20–80% SOC operating window and 80% end-of-life capacity, these packs provide 108 and 72 kWh respectively before any separately reserved emergency energy. The current repository's 540 kWh usable per train is an 80% gross planning allowance; it is not the same definition as this conservative end-of-life 60%-window calculation.

Specify pack power and charge acceptance independently of capacity. At 150 kWh, 600 kW discharge is 4C and 450 kW external charging is a 3C charger-to-nameplate ratio; at 225 kWh they are 2.67C and 2C. Actual net battery charge is reduced by services and interface loss. End-of-life effective C-rates increase as capacity fades. Select cells and parallel strings for pulse duration, hot operation, SOC, cycle life and cooling rather than treating kWh alone as sufficient sizing.

PWR-001: validate normal, crush load, maximum grade, strong headwind, hot HVAC, weak magnet, reduced battery voltage, missed chargers, low SOC, full SOC/no-regeneration and one failed traction channel.

PWR-002: size station electrical service from simultaneous arrivals and actual dwell. A 450 kW/car candidate requires up to 1.35 MW DC per three-car berth, or 2.70 MW if two berths charge simultaneously, before charger/grid losses and other station loads. Recalculation finds that 450 kW/car does not balance several hot/low-efficiency cases even on level track; the heaviest case needs about 482 kW/car before pack/grid losses. Carry 500 and 600 kW/car charger sensitivities; 600 kW/car means 1.8 MW per three-car berth. The current repository's 500 kW-class $100,000 station charger allowance cannot be carried over without a scope check. Reduced-charge-power operation may be possible with the larger battery over selected intervals, but must close over the full duty cycle.

PWR-003: specify separate energy paths for regeneration, dynamic braking when the battery cannot absorb power, and holding at zero speed on grade. A magnetic brake that fades with speed cannot be the only parking function. A resistor, passive brake surface or capture system needs a defined thermal and structural energy path. A 31.75 t car stores 7.84 MJ of translational kinetic energy at 80 km/h, excluding downgrade energy and any other inertias.

PWR-004: keep support/protection power available during a traction fault for the period required to execute the safe-stop strategy. "Trip" must inhibit unsafe propulsion while preserving the control needed for stable support until capture/landing is safe. Determine independent power-domain and energy-reserve requirements from the hazard analysis. Permanent magnetisation does not establish stable contactless operation after complete control-power loss.

### 6.4 Cooling and solar

Close a heat budget for magnets, coils, motor cores, inverters, reaction rail, battery and cabin. Distinguish HVAC cooling capacity from its electrical input. The current 24 kW-class HVAC catalogue wording must be resolved against a supplier datasheet before using it as a continuous electric load. All continuous-current assumptions must include rejected heat at the declared maximum ambient.

At 17 × 2.65 m the geometric roof area is 45.05 m². With a 22% PV efficiency assumption, covering every square metre would imply 9.9 kWp at 1 kW/m² irradiance; HVAC, roof curvature, access and mounting reduce usable area. Study roughly 5–8 kWp/car with flush modules if that is the selected roof concept. This is an area-based target, not a solar yield prediction. Recompute hot-module output, dust, shading, mounting temperature and cleaning. Credit only route/weather-modelled solar energy; it is a small contribution relative to hundreds of kilowatts of traction and continuous hot-weather HVAC.

## 7. Civil works and guideway specification

The required redesign is a narrow structural beam per direction, removing the broad wheel/rail track flange and plinth layer. The current repository already uses one 2.9 m-wide decked π beam per direction on a shared pier. Its bare concrete area is 1.199 m². The illustrative 0.8 × 1.6 m hollow guidebox with 150 mm walls and 180 mm top/bottom slabs has area 0.660 m². It uses 45.0% less bare concrete and has 35.4% greater gross vertical bending I because it is deeper.

With current trackform removed and the same one-metre walkways retained, listed superstructure concrete falls from 3,097.2 to 1,560.0 m³ per dual-direction route-km, before local end details, reinforcement, prestress, magnetic rail and walkway brackets. A simple fully loaded span comparison gives approximately 38.8% less superstructure/train reaction at a shared pier and 30.5% less axial load above the foundation if the old column/cap is retained. That supports investigating smaller supports. It does not establish equivalent percentage foundation cost savings.

At unchanged 25 m spacing the reference remains about 40 shared piers/km. Longer spans need a new optimisation. Also, the illustrative box has much lower lateral bending I than the wide π section; wind, guidance, torsion and vehicle-to-guideway movement can require a wider/stiffer section or added bracing. The costed geometry is not accepted on vertical stiffness alone. The narrow-beam appendix supplies the dimensions, equations and explicit load omissions.

CIV-001: price and design a **dual-direction route-km**, equal to two single-direction beam-km, unless a result is explicitly labelled otherwise. Include beam structure, reaction surfaces, supports, foundations, bearings/joints, erection, transport, installation, survey/metrology, drainage, protection and continuous evacuation access. Keep station, depot, major bridge, utility, land and charging scopes separate and visible.

CIV-002: retain the current 25 m reference span and 8 m pier height as initial comparison geometry; explore 20/25/30 m spans with actual geotechnical zones and erection logistics. Do not assume a nominally narrower beam automatically permits longer spans or lighter foundations. Magnetic attraction can create large local opposing forces even when net vertical support equals train weight.

CIV-003: derive the passive rail's material, laminations if required, pole/tooth geometry, sectional kg/m, mounting pitch, adjustment range, corrosion protection, thermal gaps, magnetic continuity, capture faces and inspection access from the chosen circuit. Ordinary unqualified steel cannot be assumed to have negligible eddy-current/hysteresis loss at service speed. Reaction rails remain passive electrically while carrying induced or varying magnetic fields.

CIV-004: retain the one-metre clear evacuation walkway planning requirement until the deployment's approved egress design replaces it. Compare a common central walkway and separate walkways using actual access, door direction, vehicle-to-walkway height, disabled evacuation, smoke/fire and recovery cases. A narrow beam does not eliminate the width needed by passengers, maintenance or the vehicle swept envelope.

CIV-005: compute coupled guideway/vehicle dynamics, guidebeam bending/torsion, seismic/wind response, thermal gradients, settlement, joint steps and surface alignment. Publish both structural ultimate/serviceability results and the tighter local magnetic-gap results. The old wheel/rail allowable beam deflection is not a maglev tolerance.

CIV-006: use adjustable, replaceable reaction-rail cassettes only if their fasteners, tolerances, inspection and lifetime cost are included. Allocate correction between concrete casting, surveyed erection and precision magnetic surfaces. Do not demand machine-tool tolerances from the whole viaduct without pricing how they are achieved and maintained.

CIV-007: evaluate debris, ferrous-object attraction, sand, drainage, rail corrosion, damaged rail joints and contamination. Covers must be included in the field/loss and mechanical-clearance models. Allow full access for rail replacement and magnet module service without dismantling the civil beam.

## 8. Operations, stations, depot and rescue

OPS-001: select an explicit switch-free mainline topology. Options are continuous directional loops, terminal balloon loops, or independently reversible shuttle guideways/sections. A normal double-track terminal that swaps trains between tracks requires a crossover; it cannot retain that operation while claiming no mainline switches. Loop land/civil costs and shuttle capacity/dead-time belong in the model.

OPS-002: recalculate capacity, headway, commercial speed, platform occupancy, fleet, spares, timetable and depot dispatch. One-minute dwell can dominate travel time on one-kilometre stop spacing. Compare at equal passengers/hour/direction and service hours; longer travel time or lower capacity is a changed product requirement, not a cost saving.

OPS-003: define the failure-blocking consequence of each no-switch route. Demonstrate controlled stopping, evacuation, towing/recovery and reopening with a failed car on the most constrained elevated section. Access to a depot switch does not provide a mainline bypass. Use realistic recovery time in availability and spare-fleet calculations.

OPS-004: replace wheel-bogie maintenance facilities with magnetic module service, retained-magnet handling fixtures, safe support stands, field measurement, gap/current calibration, coil/inverter replacement and guideway metrology. Do not delete all inspection pits, cranes or rescue equipment merely because wheel turning is removed.

OPS-005: preserve level boarding and door-to-platform protection over AW0–AW3 motion, control tolerances and failures. A five-millimetre normal load shift is only one term. Define what happens to door enabling after contact/capture or loss of levitation.

## 9. Embedded control, sensing and protection

CTL-001: use local deterministic control at each magnetic module or module group, with train-level force allocation. STM32G4/H7-class controllers are plausible prototype processors; benchmark the exact implementation against the derived timing envelope. The selected MCU, its software and its power/sensor/output architecture require their own qualification evidence. Processor clock speed and two cores on one chip do not establish independent protection channels.

CTL-002: initial scheduling study points are 10–20 kHz PWM/current control and 1–2 kHz gap/force allocation sampling, subject to the chosen power stage, sensor bandwidth and unstable-mode dynamics. These are starting design targets, not prescribed stabilising bandwidths. Distinguish switching frequency, control sample rate and closed-loop bandwidth. Demonstrate worst-case execution time, latency, jitter, quantisation, saturation recovery and delay robustness on target hardware.

CTL-003: measure enough independent gaps and inertial/body motion to observe vertical/lateral motion and pitch, roll and yaw. Each channel carries calibration, temperature compensation, quality flags, timestamp, range and uncertainty. Treat sensor bias as well as loss. Define actuator limits from temperature, voltage and electromagnetic force maps.

CTL-004: isolate train/OCC supervision from the inner suspension loop. FUXA provides displays, alarms and maintenance information; it does not close the lift-control loop or grant movement authority. Loss of supervisory communications must lead to a bounded locally controlled state.

CTL-005: add an independent protection design that detects dangerous gap, overspeed, overcurrent, sensor disagreement and uncommanded thrust. The action sequence must be suspension-aware: restrict traction, preserve required support control, brake, then capture/secure as designed. Do not blindly reuse a conventional traction controller's "remove all power" action for a levitated body.

CTL-006: replace wheel-derived speed/distance and axle-health assumptions with a justified contactless odometry architecture. Candidates include guideway markers, radar/optical speed, motor electrical position and IMU fusion; quantify observability and low-speed errors. No single proposed sensing method is accepted without route/environment testing.

CTL-007: add machine-readable interfaces for gap, pole overlap, current, estimated force, force reserve, bus state, temperatures, capture contact, protection power, mode and sensor health. Include units, bounds, provenance and time validity. Extend formal invariants for permitted movement, force/thermal saturation, loss of control and switch-free occupancy. Formal state-machine checks do not establish electromagnetic force or physical stability.

## 10. Manufacturing and lifecycle

MFG-001: retain the existing modular body/door/glazing manufacturing concept where compatible with the new structure. Integrate cable channels, mounting datums and service access in CAD. Avoid hundreds of unique magnet carrier variants; use replaceable standard cartridges with controlled orientation variants.

MFG-002: specify ferrite by grade, magnetisation axis, remanence/coercivity over temperature, dimensions, permissible chips/cracks, coating if needed and batch traceability. Include controlled assembly fixtures, magnetic keepers/shields where appropriate and a verified field map of each completed module. Identify the installed location and orientation of every replaceable cartridge.

MFG-003: define winding conductor, insulation system, impregnation, electrical tests, cooling interface, current calibration and module end-of-line force/gap test. Include production yield, rework, scrap, supplier quality and labour. Price the actual manufacturing routing in ERP rather than using only material cost.

MFG-004: preserve positive retention after bonding failure and differential thermal expansion. Establish non-destructive inspections where feasible, periodic gap/field checks, crack/debond indicators and replacement limits. Ferrite's corrosion and high-temperature advantages do not remove the need to inspect mechanical supports, insulation, cooling and sensors.

MFG-005: issue EBOM/MBOM revisions, manufacturing drawings, travellers, fixture definitions, inspection plans, calibration certificates, installed serial records and spare-parts lists. Bind each to the same vehicle/rail configuration hash. Keep preliminary engineering items distinct from production-released ERP items.

## 11. Engineering assurance and decision gates

Apply the project's current RAMS/safety lifecycle and establish which rail, structural, electrical, battery, EMC, fire and automated-operation requirements apply to the new architecture with the responsible operator/assessor. Do not copy wheel/rail compliance claims unchanged or assume absent wheels make the omitted functions irrelevant. The companion repository map identifies the current standards and assurance registers to update. No new standard edition or operational approval is asserted here.

| Gate | Required evidence | Decision produced |
|---|---|---|
| G0: requirements and geometry | Load cases, capacity, selected topology alternatives, swept-envelope study and complete source-linked parameter register | Candidate geometries fit the intended service and route |
| G1: material and magnetic rig | Grade curves, accepted blocks, static force/moment maps over gap/offset/current/temperature, independent force-model correlation | Actual magnet/core/winding requirements and controllable envelope |
| G2: closed-loop multi-module rig | Restrained stationary levitation, disturbances, asymmetric load, sensor/power/coil faults, force redistribution and thermal steady state | Zero-speed support and stability with bounded failure behaviour |
| G3: moving sled/representative beam | Curve and joint passage, speed-dependent losses, lift/thrust coupling, reaction-rail heating, metrology and controllability | Moving guideway interface and energy/loss model validated |
| G4: loaded full car | Measured mass, CG, structural modes, ride, braking, capture, power loss, charging and hot-duty operation | Vehicle target closure or documented redesign |
| G5: train and route demonstrator | Multi-car interfaces, switch-free service, depot, evacuation, recovery, capacity and sustained availability | Evidence for deployment-specific acceptance work |

For each gate record quantitative acceptance limits before the test. Force-map residuals, current/thermal margins, minimum gap, failure response times, braking distances, ride limits and availability targets must be tied to the declared operating envelope. Values still awaiting hazard/route derivation must stay visibly open. Passing repository checks or rendering CAD does not close physical tests.

The design comparison should advance only if measured/qualified subsystem data allow the complete mass, cost, energy, tolerance and failure budgets to close together. A cheap magnet assembly that requires an expensive precision rail or unacceptable curve restriction has not met the system objective.

## 12. Required software and data deliverables

Add the new family/profile, suspension/propulsion architecture enums and conditional generators. Replace bogie/axle reactions with distributed magnetic force interfaces only in that branch. Create a reproducible electromagnetic model and a flexible vehicle/guideway model; link force/loss maps into energy, traffic and failure simulations.

The initial handoff includes a proposed TOML input scaffold, calculation source/results, an editable cost model and this specification. **The TOML is not directly accepted by the current repository schema.** First implement the schema/profile branch and validation rules, then import the values with their evidence status. Unknown field maps and unset operational acceptance limits must cause release validation to fail clearly rather than defaulting to a successful design.

Required generated outputs are: general arrangement and swept envelope; magnet/coil/rail CAD and drawings; force/loss maps; mass/CG/inertia and support-load ledgers; thermal/electrical load cases; route energy/charging simulation; protection fault matrix; guideway BoQ and gap/tolerance register; train MBOM and manufacturing routing; train/civil/station/depot/charger cost reconciliation; life-cycle inspection and replacement schedule; configuration-linked assurance evidence; IFC/ERP/supervision interface exports.

The appendices that follow contain the detailed magnetic requirement set, recalculated duty-cycle results, cost build and exact repository integration map. The cost workbook uses one active low/base/high selector and keeps the battery reduction as an explicit engineering choice.

---



# Appendix A. Detailed magnetic suspension and propulsion requirements

## Magnetic suspension and propulsion requirements for the ferrite maglev redesign

Status: proposed input specification for concept development. Numeric allocations are engineering targets and sensitivity cases unless explicitly identified as measured evidence. This section does not release hardware for fabrication or operation.

### 1. System definition and baseline quantities

MAG-001. Develop a 17 m by 2.65 m car supported and guided magnetically by a passive guidebeam, with permanent magnets and all powered propulsion/suspension windings on the car. Permanent magnets provide the steady suspension bias. Solid-state power electronics control the required forces. The normal running system shall target zero internally moving mechanical running gear; doors and HVAC remain conventional functional assemblies. Cooling pumps, charging mechanisms and emergency mechanisms must be disclosed if selected.

MAG-002. Carry both ferrite cases through every calculation. For the 150 kWh/car battery option these are (A) 18,000 kg empty including 3,000 kg ferrite and (B) 19,000 kg empty including 4,000 kg ferrite. The primary matched-capacity 225 kWh/car cases add 750 kg to each car, becoming 18,750/19,750 kg empty. Retain the current LM-3 load cases: AW2 is 120 passengers per car, initially 9,000 kg at 75 kg/person; AW3 is 160 passengers per car, initially 12,000 kg. Thus 150 kWh AW2 masses are 27,000/28,000 kg and AW3 masses are 30,000/31,000 kg; matched-capacity AW2 masses are 27,750/28,750 kg and AW3 masses are 30,750/31,750 kg. Do not silently reduce the repository's 480-person three-car AW3 requirement to the 360-person AW2 case. Tare masses are targets, and final occupancy/load definitions need the project's approved requirements. Magnet mass is included in empty mass, not added a second time.

MAG-003. Use the following derived force requirements at standard gravity for the 150 kWh/car Cases A and B. For the primary 225 kWh/car cases, add 7.3575 kN to each total weight, 0.75 kN to inertial thrust at 1 m/s², and 0.3065625 kN to each equal-share 24-module lift. Passenger-load increments are unchanged. All later references to Cases A/B in this appendix use the 150 kWh cases unless explicitly stated otherwise:

| Quantity | Case A | Case B |
|---|---:|---:|
| Empty-car weight | 176.58 kN | 186.39 kN |
| AW2 weight | 264.87 kN | 274.68 kN |
| AW3 weight | 294.30 kN | 304.11 kN |
| AW0-to-AW2 passenger weight increase | 88.29 kN | 88.29 kN |
| AW0-to-AW3 passenger weight increase | 117.72 kN | 117.72 kN |
| AW2 inertial thrust at 1 m/s² | 27 kN | 28 kN |
| AW3 inertial thrust at 1 m/s² | 30 kN | 31 kN |
| Ideal equal AW2 static lift per 24 modules | 11.04 kN | 11.45 kN |
| Ideal equal AW3 static lift per 24 modules | 12.26 kN | 12.67 kN |

Thrust requirements must add grade, aerodynamic drag, electromagnetic drag and other losses. Equal module loading is only a screening case; distributed loads, pitch, roll and local flexibility govern the real allocation.

MAG-004. Retain 24 modules as an initial packaging study, not a fixed architecture. The earlier two 12 m × 0.5 m × 0.05 m strips occupy 0.60 m³; at an assumed density of 5,000 kg/m³ this is 3,000 kg. This volume arithmetic establishes no levitation capacity. It also excludes cores, windings, brackets, encapsulation and covers.

### 2. Competing suspension architectures

MAG-010. Evaluate two explicitly separate magnetic circuits before fixing a beam cross-section.

Architecture A: transverse Halbach array attracting an iron lifting surface. The car's load path wraps beneath an appropriate guideway flange or equivalent upward-attracting surface. A flat iron surface below an ordinary magnet does not provide upward attraction. Orienting the array's spatial periodicity across the direction of travel is a candidate for reducing longitudinal field variation and parasitic guideway losses. The usual attractive vertical lifting gap is unstable and requires active vertical control. Permit the equilibrium gap to change with load and temperature to reduce steady coil demand. A zero-current operating point is not an open-loop stability guarantee. Zero-power control of a rigid multi-point vehicle is a published research direction, not an established performance result for this car. [S2]

Architecture B: permanent-magnet-excited shaped pole assemblies working inside or beside a matching passive C-shaped iron/steel rail. Pole alignment produces vertical restoring force over a defined displacement range, so gravity and passenger load can set the vertical offset. Lateral attraction remains unstable and requires active guidance at rest and while moving. The original flat Halbach block pattern need not be optimal for this circuit.

Richard Post's patent distinguishes these configurations: Figures 1–2 concern vertically restoring shaped poles with transverse instability; Figure 3 concerns a Halbach array attracting an overhead iron surface with vertical instability. The patent's motion-dependent stabilisation is not evidence that a stationary car is fully stabilised. Replacing it with onboard active guidance is an engineering proposal here. [S1]

MAG-011. Reject any model that credits sustained zero-speed lift to a plain permanent-magnet array inducing currents in a passive normal conductor. Enlarging that array does not remove the requirement for relative motion or powered time-varying excitation.

MAG-012. Rank A and B on complete installed system mass, force capability, power, guideway cost, gap tolerances, controllability, failure response, thermal performance and assembly requirements. A visually simpler cross-section or a lower raw magnet price is insufficient for selection. Record why a topology is selected and retain the losing topology as a comparison model until the choice is supported by hardware evidence.

### 3. Variable height, stability and ride

MAG-020. Set 5 mm AW0-to-AW2 vertical movement as the initial design target, with 3 mm and 10 mm sensitivity cases. The additional lift is 88.29 kN; therefore the required average restoring stiffness is 29.43, 17.658 and 8.829 MN/m for 3, 5 and 10 mm respectively. At 24 equal modules, the 5 mm case corresponds to 735.75 N/mm per module. AW3 adds 117.72 kN above empty: a linear extrapolation of the 5 mm/AW2 stiffness would require 6.67 mm travel, while restricting AW0-to-AW3 movement to 5 mm would require 23.544 MN/m. Select and verify the AW3 travel/active-force requirement explicitly; do not assume the usable force curve remains linear.

MAG-021. Distinguish carbody displacement, physical magnetic gaps and pole overlap in every model. In Architecture B, 5 mm vertical displacement can change pole overlap while the lateral clearance is nearly unchanged. In Architecture A, a smaller upward-attracting gap increases lift and may place a more heavily loaded car higher relative to its rail. Do not transplant the "heavier car sinks" assumption between topologies.

MAG-022. Treat the earlier 8 mm magnetic gap as a study point. Determine minimum permissible gap, normal equilibrium range, control travel and contact thresholds from a tolerance budget including manufacturing, rail installation, beam deflection, carbody bending, temperature, curves, sensor uncertainty, disturbances and control error. Passenger-load movement must not consume all available clearance.

MAG-023. Determine the complete force/moment stiffness matrix and controllable modes, not only vertical force. Include vertical and lateral translation, pitch, roll, yaw, longitudinal motion and the dominant elastic modes. Unstable directions must be stabilised at zero speed. Along-track translation can be intentionally free or driven; that does not establish lateral stability.

MAG-024. Simulate passenger movement, eccentric boarding, braking weight transfer, curve loads, wind loads, rail joints, beam deflection and differential module heights. A 5 mm load movement target alone does not establish passenger comfort. With approximately constant 17.658 MN/m total stiffness and the AW0-to-AW2 midpoint masses of 22.5/23.5 t, a single-body model has an undamped heave frequency of approximately 4.46/4.36 Hz. Use the actual multi-body model and route disturbance spectrum to determine ride quality and damping.

MAG-025. Investigate direct electromagnetic support of the carbody. If it fails ride or clearance requirements, identify the minimum necessary compliance and its mass rather than silently importing conventional bogies. Conversely, do not remove structural flexibility or suspension functions from the model merely because the preferred design contains no mechanical ride suspension. Verify horizontal and vertical swept geometry as well as forces. For a straight active length L following a horizontal rail curve of radius R, the chord-to-arc deviation scales approximately as L²/(8R); 12 m at R = 100 m gives 180 mm of horizontal offset. This exceeds an 8 mm lateral allowance at a narrow vertical face but does not directly consume an 8 mm vertical lift gap at a broad horizontal face. Shortening the individual modules does not automatically solve the global offset if they remain fixed along a straight rigid underframe. Resolve lifting-face overlap, separate guidance geometry, vehicle articulation/compliance or route curvature before claiming a bogie-free car can negotiate the existing alignment. Vertical curves and twist require their own clearance calculation.

### 4. Ferrite material, retention and thermal design

MAG-030. Use sintered hard permanent-magnet ferrite, distinguishing it from soft ferrite core materials. The initial Br = 0.43 T and density = 5,000 kg/m³ are calculation inputs pending a specific grade and procurement specification. TDK lists a hard-ferrite grade with Br 430 ± 10 mT; its ferrite guidance also identifies ceramic brittleness and a Br temperature coefficient near −0.18%/K. These data support a material study, not equivalence between every low-price ferrite block and that grade. [S5, S6]

MAG-031. Carry at least −20, 20, 50, 80 and 100°C magnet-temperature screening points until the operating and survival environment is agreed. These are analysis cases, not accepted operational ratings. Keep ambient, rail, magnet, winding, adhesive and battery temperatures separate. For sensitivity, the earlier −0.20%/K Br coefficient gives Br(80°C) ≈ 0.3784 T from 0.43 T at 20°C. In a simple unsaturated B-squared force estimate, this corresponds to 77.44% of the reference force. Recompute from the real magnetic circuit; do not assume this ratio transfers exactly under saturation or active compensation.

MAG-032. Check irreversible demagnetisation at the minimum material temperature as well as at maximum temperature, with the worst reverse coil field, opposing magnet assembly field, shorted winding and manufacturing tolerance. High temperature resistance is not constant magnetic output. Obtain full second-quadrant and recoil curves over temperature and a manufacturer-approved demagnetisation margin.

MAG-033. Do not credit ferrite ceramic as the primary crash, bending, tensile or fatigue load path of the chassis. Integrate magnets into the structural assembly through carriers, pockets, clamps, potting or bonded interfaces with positive retention. Design for differential thermal expansion, block cracking and local debonding. Structural integration means shared engineered support, not an assumption that brittle blocks replace a qualified underframe.

MAG-034. Each magnet module shall have polarity/orientation poka-yoke, a traceable material batch, dimensional inspection and a field-map acceptance record. Check every block or a justified manufacturing sampling plan for remanence, orientation and defects. Verify the complete assembled field, including weak-side leakage. Use assembly fixtures that control attractive forces without depending on manual alignment near an exposed gap. Make a damaged module replaceable without dismantling the whole underframe.

### 5. Onboard electromagnetic propulsion

MAG-040. Compare two onboard propulsion options:

P1: a short-primary linear induction motor acting on a passive conductive reaction rail, with suspension magnets nearby or sharing selected structural supports. Quantify slip-dependent efficiency, normal forces, end effects, power factor and reaction-rail heating.

P2: a linear flux-switching or flux-reversal permanent-magnet machine with magnets and powered windings on the moving car and a passive salient iron track. Cao et al. describe and experimentally test a motor with this arrangement; their prototype supports the topology, not our passenger-car force density or ferrite mass. [S3]

MAG-041. Evaluate shared suspension/propulsion cores and windings only after producing coupled force maps. Jastrzebski et al. model a linear permanent-magnet machine combining levitation and thrust with all active hardware on the mover, using winding arrangements that permit control of both functions. Their published evidence is modeling and control simulation. [S4]

MAG-042. The powered coils must exchange force with the external guideway. Forces between components fixed to the same car do not propel it. A uniform lossless iron rail and arbitrary pulsing of onboard magnets is not an acceptable thrust model; define induction currents or a position-dependent salient magnetic circuit.

MAG-043. Supply maps of thrust, lift, side force, cogging and force ripple against rail position, gap, lateral displacement, current and speed, including forward/reverse motoring and regeneration. Show how propulsion commands affect suspension authority. Size sensors and commutation from the selected pole/tooth combination; the previously discussed 200 mm array wavelength does not universally determine electrical frequency.

MAG-044. Report mechanical output, DC input, winding/core loss, rail loss and cooling demand separately. Do not apply a fixed 70% efficiency as a validated result. At 80 km/h and 1 m/s², even the inertial thrust alone requires approximately 600/622 kW mechanical in AW2 Cases A/B and 667/689 kW in AW3, before drag. Therefore a 600 kW total electrical cap cannot maintain that acceleration to 80 km/h; the controller must taper acceleration or the power system must be resized.

### 6. Model outputs and verification gates

MAG-050. Produce reproducible 2D screening models and 3D finite-element models with nonlinear steel, grade-specific magnet curves, finite array ends, module seams, winding slots, joints, conductive covers, mechanical tolerances and mesh convergence. Export SI-unit force and loss maps with geometry/material/model revision identifiers. Verify force by at least two independent methods where practical, such as Maxwell stress and virtual work.

MAG-051. Publish the usable operating envelope, including lift capacity at the weakest magnet state and maximum normal gap, lateral stability/control margin, continuous and transient current limits, saturation margin, demagnetisation margin, thermal limits and torque capacity for asymmetric loads. A suggested initial screening reserve of 1.3 times AW3 static weight gives 382.59/395.34 kN in Cases A/B. This is a project assumption, not a substitute for deriving dynamic design loads or a regulatory safety factor. The full AW3 body/rail load and asymmetric passenger distribution must be retained.

MAG-052. Couple these maps into a six-degree-of-freedom vehicle model and flexible guideway model. Include actuator delay, sensor noise and bias, bus-voltage sag, current saturation, force ripple and structural resonance. Determine control bandwidth from unstable mode growth and disturbance rejection; microcontroller clock speed is not a stability proof.

MAG-053. Verify failure cases individually and in credible combinations: a magnet block cracked or incorrectly oriented; a missing module; a coil open or short circuit; an inverter stuck on or off; failed gap sensor; stale communications; guideway joint offset; a blocked cooling path; and common DC-bus interruption. A failed coil does not automatically remove permanent-magnet attraction. A shorted coil may generate speed-dependent forces and heat. Capture these effects in the fault model.

MAG-054. Prove stationary support and guidance, controlled stopping, power-off support and recovery separately. Fixed skids or capture surfaces may avoid deployment mechanisms, but require load, friction, energy and stability analysis. An AW3 31 t car at 80 km/h contains approximately 7.65 MJ of translational kinetic energy; any emergency stopping system must account for its energy path. Permanent magnets remaining magnetised do not by themselves guarantee contactless stability after a control failure.

MAG-055. Use progressive evidence gates: material coupon and block acceptance; static instrumented module rig; force-versus-gap/offset and thermal correlation; restrained closed-loop levitation; moving sled with representative joints and speed-dependent rail losses; multiple-module rigid/flexible body; and a representative loaded car/beam demonstrator. Do not advance from bench levitation directly to passenger operation.

Acceptance must require force/moment map correlation, model error bounds adequate for control design, stable operation across the declared envelope, bounded failure behaviour, verified module mass and cooling demand, and a manufactured rail tolerance consistent with the civil design. The 2.7 t combined magnetic/electrical package remains an allocation until weighed or supported by component-level CAD and supplier data.

### Primary technical references

S1. Richard Freeman Post, Inductrack configuration, US7096794B2. Figures 1–3 and detailed description distinguish passive vertical support from the unstable directions and discuss onboard propulsion.
https://patents.google.com/patent/US7096794B2/en

S2. Morishita, Akashi and Azukizawa, Zero-power Control for Maglev System of A Rigid Body Vehicle with Multi-suspended Points, 2000. Supports the variable-equilibrium/current-minimisation research direction; does not establish our multi-module dimensions or performance.
https://www.jstage.jst.go.jp/article/ieejias1987/120/4/120_4_509/_article/-char/en

S3. Cao et al., Modeling of a Complementary and Modular Linear Flux-Switching Permanent Magnet Motor for Urban Rail Transit Applications, 2012, DOI 10.1109/TEC.2012.2190985. Prototype-tested propulsion topology.
https://chrismi.sdsu.edu/publications/2012_TEC_27_2_June_Ruiwu_Modeling.pdf

S4. Jastrzebski, Jaatinen and Pyrhönen, Modeling and control design simulations of a linear flux-switching permanent-magnet-levitated motor, 2017, DOI 10.1299/mej.17-00084. Coupled lift/thrust simulation methodology.
https://www.jstage.jst.go.jp/article/mej/4/5/4_17-00084/_article

S5. TDK, Ferrite Magnet FB Series summary. Mechanical properties, temperature behaviour and demagnetisation considerations.
https://product.tdk.com/info/en/catalog/datasheets/magnet_fb_summary_en.pdf

S6. TDK hard-ferrite product catalogue. Example FB9H Br 430 ± 10 mT; supplier grade selection remains open.
https://product.tdk.com/en/search/magnet/magnet/ferrite/catalog

Additional Halbach propulsion reference: Raihan et al., Linear consequent pole Halbach array flux reversal machine, 2019, DOI 10.1049/joe.2018.8110. Halbach magnets and windings share the active member; its small low-speed model does not establish train-scale performance.
https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/joe.2018.8110



# Appendix B. Curve geometry and switch-free operation

## Geometry review: 17 m rigid ferrite-maglev car without moving running gear

Engineering screening only; pure geometry plus read-only OpenSourceRail source inspection. Source commit: **50010ce56370cf6b22dc383c12eebbc224800007**. No mechanical or electromagnetic feasibility is claimed by a clearance calculation.

### Recommended candidate to investigate first

Keep the rigid 17 m safety frame and distributed magnets, but separate **vertical lift-gap control** from **horizontal curve accommodation**: use sufficiently wide, horizontal ferromagnetic attraction faces on the guidebeam, with short, separately controlled guidance stations near two longitudinal locations. Maintain the nominal 8 mm vertical lift gap while allowing roughly centimetres to decimetres of horizontal displacement across the face on curves. A horizontal 180 mm chord offset is not automatically a vertical 180 mm gap error.

This is a candidate geometry, not proof of passive static stability. It needs active heave, pitch, roll, lateral and yaw control/protection as required by the chosen magnetic topology; independently checked force maps must establish stability, saturation, failed-channel behavior and acceptable magnetic overlap. The fixed magnets, coils and chassis can have no internal mechanically moving running gear while the whole car follows the guideway.

### 1. Quantitative geometry limits

For a straight chord of length L on a circular guideway of radius R, with its ends centered on the guideway:

`s = R − sqrt(R² − (L/2)²) ≈ L²/(8R)`.

If the entire allowable deviation in that direction is δ, the exact limiting radius is `R = L²/(8δ) + δ/2`; the additional δ/2 is negligible in these examples. For δ = 8 mm:

| Straight constrained length | Minimum radius from approximate formula |
|---|---:|
| 12 m | **2,250 m** |
| 1 m | **15.625 m** |
| 17 m | **4,515.625 m** |

These values are clearance geometry, not allowable-speed or rail-vehicle safety ratings. Also, a nominal 8 mm operating gap is not an 8 mm available disturbance budget: manufacturing error, beam deflection, thermal displacement, sensing error, control error and minimum non-contact reserve consume part of it. With only 4 mm available for curve geometry, the 12 m result becomes 4,500 m.

| Radius | 12 m center-to-chord deviation | 1 m independently tangent/chord-aligned deviation |
|---|---:|---:|
| 90 m | 200.2 mm | 1.389 mm |
| 100 m | 180.2 mm | 1.250 mm |
| 200 m | 90.0 mm | 0.625 mm |
| 300 m | 60.0 mm | 0.417 mm |
| 1,000 m | 18.0 mm | 0.125 mm |

The endpoint-centered chord is an explicit placement assumption. A freely offset best-fit straight line can approximately halve maximum absolute deviation by distributing it to either side, but the actual guidance constraints, collision envelope and minimum gaps must allow that placement. Do not silently take this credit.

#### Why twelve 1 m modules do not solve a 12 m rigid-car problem

If all twelve module centers and faces remain attached along the same straight chassis datum, their global envelope is still a 12 m straight array. Independent current commands can change forces; they cannot move those module centers onto a curve or remove physical contact. The 1 m sagitta result applies only when each module actually has its own local tangent/chord alignment and location, or when a sufficiently broad reaction surface tolerates its global offset.

The same distinction applies to vertical curves. A constant 5% grade is handled by pitching the whole rigid car; a grade transition has curvature, so a long rigid array develops a vertical gap mismatch. Widening the face horizontally solves horizontal overlap, but not a vertical crest/sag or guidebeam twist. Those need an explicit vertical-radius/roll-transition limit, shorter longitudinal support zones, or a justified larger gap envelope.

### 2. Actionable alternatives

#### A. Distributed arrays with wide flat attraction faces and separate guidance

Retain the 12 m total longitudinal magnetic footprint. Arrange upward attraction to horizontal guidebeam faces so the operating gap is vertical. Provide adequate face width for lateral sweep, rather than forcing the chassis to track a narrow vertical face at 8 mm clearance over 12 m.

For a magnet strip of transverse width w, a conservative face-width requirement is `w + 2e_max + 2m`, where e_max is maximum lateral centerline offset and m is the separate edge/alignment margin. Under endpoint-centered chord geometry, the required extra face width before margins is approximately **400 mm at R90**, **360 mm at R100**, **180 mm at R200**, or **120 mm at R300**. These are per-face overlap allowances, not an extra distance between the two route directions.

Add short guidance pole stations and local lateral-position sensing near front/rear support locations. Use distributed longitudinal force maps that include x-position, lateral overlap, local heading mismatch, gap, current, temperature and curve direction. A broad fixed array with laterally tiled coils can select effective force regions electronically, but permanent magnets remain present: inactive coil commands do not make displaced ferrite disappear. Analyze unwanted fringe attraction, normal forces from the linear motor and the cost/mass of unused overlap width.

This preserves distributed load and magnetic area but widens magnetic/reaction surfaces and some guidebeam interfaces. It directly trades guideway cost and magnetic overlap margin against eliminated pivoting gear.

#### B. Compact fixed support clusters near two longitudinal points

Concentrate lift near, for example, x = ±6 m with 1 m long clusters. Put the rail centerline through the cluster centers. The car is aligned to the chord between those points. This avoids requiring a continuously close-fitting 12 m side channel; each small cluster and the body envelope still need checks.

There is a significant local yaw mismatch: `θ = asin(6/R)`. At R100, θ = 3.44°. A fixed 1 m cluster then has approximately **30 mm** of lateral deviation over its half-length from heading mismatch, in addition to local curvature effects. At R90/200/300, that term is about **33/15/10 mm**. Thus a 1 m cluster cannot simply claim the isolated 1.25 mm sagitta at R100.

Use wide horizontal lift faces at each cluster, with much shorter guidance pole faces close to its center. For an 8 mm lateral excursion allowance, the first-order guidance pole length limit is `ell ≤ 2δ/sinθ`: about **0.24 m at R90** and **0.27 m at R100**, before error/clearance reserves. If only 3 mm is available, these fall to about 0.09 and 0.10 m. Pole placement and reaction-face width must be designed together.

The main drawback is magnetic pressure and structural load concentration. Reducing total effective length from 12 m to two 1 m clusters at unchanged transverse width divides lift area by six. Supporting the same weight then requires **six times average pressure, or sqrt(6) ≈ 2.45 times effective field** under the ideal `p = B²/(2μ0)` scaling. It is not valid to keep the same ferrite mass/flux claim while silently discarding five-sixths of useful area. A larger transverse area, more poles or a different topology may be needed. Chassis bending and local guidebeam reactions also increase.

#### C. Genuinely shorter articulated body units

Shorten each independently orienting rigid body/support unit. With an 8 mm full geometric budget, `L ≤ sqrt(8Rδ)` gives approximately **2.4 m at R90**, **3.58 m at R200**, and **4.38 m at R300**. These are screening upper bounds before tolerance reserves.

Splitting a 17 m vehicle into roughly four shorter sections therefore approaches the R300 geometry case; seven approximately 2.4 m sections approach R90. Every section needs real independent yaw/pitch freedom or a contactless equivalent. Mechanical articulation reintroduces moving joints, bellows and trainlines, so this is an explicit relaxation of “only doors and HVAC move,” even if the running gear has no wheels or steering pivots. Merely panelizing a continuous rigid frame does not qualify.

#### D. Retain narrow gaps and impose generous route radii

Keep long rigid, close-fitting arrays and set a radius of at least 2,250 m for a full 8 mm chord budget over 12 m; a usable budget of 4 mm gives 4,500 m. Specify separate horizontal radius, vertical radius, twist/roll gradient and tolerance limits. This can preserve simple onboard geometry but requires substantial realignment and large terminal loops. It is poorly matched to the present 90/200 m urban presets. Curvature and acceptable speed must be recalculated together.

### 3. Body sweep, grade and repository comparison

With support points 12 m apart on a 17 m rigid body, the 2.5 m end overhang beyond each support sweeps outward by approximately `(8.5² − 6²)/(2R)`. It is about **202 mm at R90, 182 mm at R100, 91 mm at R200 and 60 mm at R300**, while the middle of the body cuts inward by the 12 m sagitta. Add this to half-width, roll/sway, construction tolerances and evacuation/structure clearance. A 2.65 m body alone does not define a sufficient tunnel, station or viaduct envelope.

Current source presets, **not surveyed actual route minima**:

| Existing profile | Minimum horizontal radius | Elevated preferred radius | Maximum grade | Compatible current families |
|---|---:|---:|---:|---|
| standard-urban | **90 m** | 300 m | **5%** | tram-2car, light-metro-3car |
| standard-metro | **200 m** | 300 m | **3.5%** | LM3, metro-4car, metro-6car |

Source: [`lib/templates/track-geometry.toml` lines 12–34](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/lib/templates/track-geometry.toml#L12-L34). These presets require realignment or a special structure for tight elevated curves; they do not guarantee that maximum speed is permitted on minimum radius. The file does not specify a vertical-curve radius. Existing cant in millimetres is a two-rail measure and must be converted into a new guidebeam banking/roll specification.

The controlled Baghdad alignment concept has `preferred_fillet_radius_m = 1000.0`, but is marked as requiring survey/property/utility/crossing/independent review; it is not a guarantee of every curve. Even R1000 gives 18 mm deviation over 12 m, exceeding an 8 mm full chord budget. Source: [`lib/templates/baghdad-alignment.toml`](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/lib/templates/baghdad-alignment.toml).

The existing LM3 and M6 operating caps are 25 and 28 m/s respectively; their wheel-bogie compatibility must not transfer to this maglev. For a 27 t loaded car, the 5% urban grade alone requires about **13.23 kN**, or **331 kW mechanical power at 90 km/h**, before acceleration and drag. Source for current vehicle caps: [`rolling-stock.toml` lines 100–120 and 147–165](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/lib/templates/rolling-stock.toml#L100-L165); grade force is calculated as `mg sin(atan(0.05))`.

### 4. Turnbacks with no mainline switches

**Independent bidirectional tracks:** A train can stop and reverse propulsion on its own fixed track. This works well for independent shuttles. It does not produce normal high-frequency two-track urban operation automatically: two trains travelling in opposite directions on the same connected track cannot pass. A simple through-service with one train per independent track has per-direction headway approximately `H = (2T_run + 2T_turn)/2` for two evenly phased tracks. With T_run = 30 min and T_turn = 2 min, that is **32 minutes**, despite two tracks. Multiple trains on each track require directional convoy operation, isolated shuttle sections or passing infrastructure; reversal alone does not remove the constraint.

**Fixed terminal loops:** Join outbound and inbound tracks by continuous fixed curves at both ends, or operate a full ring. Multiple trains can circulate under normal separation without moving mainline points, making high frequency possible. The two end connections form one continuous circuit. Both directions still need appropriate station faces and passenger information; a through failure eventually blocks circulation unless recovery or another independent route is available. Depot access can retain the switches explicitly allowed by the user.

A 180° turning curve needs at least **2R centerline extent across its turn**: roughly 180 m at R90, 400 m at R200, or 600 m at R300, before structures and property margins. Close-spaced parallel guideways cannot be joined by a semicircle of that radius without flaring into a bulb or another surveyed connecting alignment. A 2,250 m radius narrow-gap design would need kilometre-scale terminal-turn land, which is a major reason to solve curve accommodation on the vehicle/guideface rather than only by route radius.

### Input-spec decision

Make **wide horizontal lift faces plus separately located short guidance poles** the primary no-moving-running-gear study, and keep **compact fixed lift clusters** as a quantified alternative whose required field/area must be demonstrated. Freeze horizontal/vertical/twist geometry and no-switch operating topology before promoting the ferrite mass, vehicle tare or viaduct cost estimate. A “1 m module” label alone must not be accepted as evidence of curve compatibility.



# Appendix C. Duty-cycle calculation and reserves

## Duty-cycle calculation and reserve results

All values in this appendix are calculated from explicit concept assumptions. They are not measured train performance. Each cycle includes one kilometre of motion and the complete 60-second dwell; charging must replace that energy during 45 effective seconds. Motoring is capped at 600 kW total DC per car, including services. Maximum initial acceleration and service deceleration are 1 m/s². Air density is 1.2 kg/m³, CdA is 3 m²/car, and constant moving magnetic drag is assumed to be 1 kN/car. Level track only.

Normal: 40 kW/car services, 70% drive efficiency, 55% regeneration recovery. Hot/low-efficiency: 60 kW services, 55% drive efficiency, 35% regeneration. Neither efficiency map nor the static-control/drag demand has been measured for the proposed machine. Battery internal loss, grid/charger loss, charge taper, jerk limiting and extra emergency reserve are excluded. Regeneration is assumed available; a no-regeneration case is a required next scenario.

| Battery/car | Ferrite/car | Load | Gross mass/car | Normal cycle | Hot cycle | Normal DC charger/car | Hot DC charger/car |
|---|---|---|---:|---:|---:|---:|---:|
| 225 kWh | 3 t | AW2 | 27.75 t | 3.661 kWh | 5.618 kWh | 292.9 kW | 449.4 kW |
| 225 kWh | 3 t | AW3 | 30.75 t | 3.842 kWh | 5.923 kWh | 307.4 kW | 473.8 kW |
| 225 kWh | 4 t | AW2 | 28.75 t | 3.721 kWh | 5.719 kWh | 297.7 kW | 457.6 kW |
| 225 kWh | 4 t | AW3 | 31.75 t | 3.902 kWh | 6.025 kWh | 312.2 kW | 482.0 kW |
| 150 kWh | 3 t | AW2 | 27.00 t | 3.616 kWh | 5.542 kWh | 289.3 kW | 443.3 kW |
| 150 kWh | 3 t | AW3 | 30.00 t | 3.797 kWh | 5.847 kWh | 303.7 kW | 467.7 kW |
| 150 kWh | 4 t | AW2 | 28.00 t | 3.676 kWh | 5.643 kWh | 294.1 kW | 451.5 kW |
| 150 kWh | 4 t | AW3 | 31.00 t | 3.857 kWh | 5.948 kWh | 308.6 kW | 475.9 kW |

All sixteen simulated cases reach 80 km/h before service braking. The 225 kWh/4 t ferrite/AW3 case runs the kilometre in 67.993 s normally and 69.338 s in the hot sensitivity; including dwell gives 127.993/129.338 s. Commercial speed on this repeating ideal segment is approximately 28 km/h. Actual timetable, jerk, grade, station approach and protection margins remain to be included.

At the heaviest normal case, the acceleration taper starts at 42.76 km/h and acceleration at 80 km/h is 0.496 m/s². In the hot case these become 32.50 km/h and 0.361 m/s². Holding 1 m/s² all the way to 80 km/h would instead require 1.108/1.419 MW DC per car under these two sets of assumptions.

For the heaviest hot case, the calculated balanced charger output is 482.0 kW/car, or 1.446 MW for three cars. A 450 kW charger loses approximately 0.400 kWh each repeating cycle. A 500 kW charger supplies 6.25 kWh in 45 seconds, only 0.225 kWh above the calculated 6.025 kWh demand. A 600 kW/car charger supplies 7.5 kWh and is a candidate for the full route/thermal/charging study. Two simultaneously charging three-car trains at that rating demand 3.6 MW DC before station and grid-conversion losses.

Charger DC output includes the services operating during charging. In the heaviest hot case, approximately 422 kW of the balanced 482 kW reaches the battery after 60 kW of services. It is incorrect either to subtract these services from the whole cycle twice or to omit their charging-interval consumption entirely.

### Battery power and reserve

| Pack/car | Installed target mass | BOL 20–80% window | Window at 80% EOL capacity | 600 kW/nameplate | 600 kW/EOL capacity |
|---|---:|---:|---:|---:|---:|
| 150 kWh | 1.50 t | 90 kWh | 72 kWh | 4.00C | 5.00C |
| 225 kWh | 2.25 t | 135 kWh | 108 kWh | 2.67C | 3.33C |

These are energy-equivalent power/capacity ratios, not accepted cell current ratings. Ageing, voltage, cooling, chemistry, SOC and duty duration determine allowed current. A larger pack has more reserve and lower effective C-rate; it does not fix a repeated charging energy deficit indefinitely.

One missed intermediate charging stop means two uncharged cycles before the next successful charge. Under the worst hot case plus a 30-minute 60 kW stationary hold, the 150 kWh variant consumes about 41.90 kWh and the 225 kWh variant about 42.05 kWh. Their respective EOL windows then have 30.10 and 65.95 kWh remaining, assuming departure at 80% SOC and permission to use energy down to 20%. This is not a guaranteed reserve at another dispatch SOC and does not include a separately protected safety reserve.

### Grades and adverse scenarios

The simple extra DC energy for one uphill kilometre at 1% grade is m g × 10 m / (3.6 million × drive efficiency). For the matched 225 kWh cases it is about 1.080–1.236 kWh at 70% efficiency and 1.375–1.573 kWh at 55%. A 5% climb magnifies that potential-energy term fivefold, but a real route calculation must also recompute speed, acceleration, time and regeneration. Downhill energy is recovered only to the extent the motor, inverter and battery can accept it.

Next calculations required: approved jerk-limited speed profile; 90 km/h capability comparison; full grade/curve alignment; wind and hot HVAC; weak magnets; measured motor/rail losses; low-voltage and failed-drive modes; regeneration unavailable/full SOC; battery charge taper and internal losses; multiple missed chargers; prolonged station hold; simultaneous charging; and weather-specific solar generation.

The source script uses adaptive velocity-domain quadrature and an independent 1 ms time-domain integration for representative normal and adverse cases. They agree within 0.001 kWh and 0.001 s. This verifies numerical consistency of the assumed model, not the physical inputs. The provided JSON retains all sixteen cases and energy-flow details.



# Appendix D. Construction and development cost model

## Ferrite maglev cost input for OpenSourceRail rework

**Status: conditional engineering screening, not quotations or a released cost estimate.** The proposed magnetic suspension, guidance and propulsion must first meet the mechanical, electromagnetic, thermal, control and fail-safe requirements. Prices below make the proposed architecture costable without treating unproved engineering as free.

This note uses the current OpenSourceRail checkout at commit `50010ce56370cf6b22dc383c12eebbc224800007`. All figures use the repository's nominal USD local-owner manufacturing basis for comparison. New unit costs and production hours are explicit author assumptions. Low/base/high are three scenarios, not confidence intervals, market quotations or forecasts.

The main result is that mature repeat production of a three-car train falls in the same broad range as the current train target. The matched 675 kWh battery base case is **$872,197 per three-car train versus $885,205 currently**. A small central saving is plausible within the model, but it is far smaller than the uncertainty. Elevated guideway using the dimensioned narrow-box concept is provisionally **$7.048m–$10.529m per dual-direction route-km, central $8.346m**, versus the current **$9.748m** target. A separate first three-car pilot programme is budgeted at **$9m–$55.2m, central $23.22m**, under the stated scope.

### 1. Use an equivalent train comparison

| Parameter | Current LM3 | Proposed base | Proposed smaller-battery sensitivity |
|---|---:|---:|---:|
| Cars | 3 | 3 | 3 |
| Nominal length | 49.5 m | About 51 m; couplings to be resolved | Same |
| AW2 passengers | 360 | 360 | 360 |
| AW3 passengers | 480 | 480 | 480 |
| Gross battery/train | 675 kWh | 675 kWh | 450 kWh |
| Gross battery/car | 225 kWh | 225 kWh | 150 kWh |
| Ferrite/car | None | 3 t | 3 t |
| Tare/car | 26.25 t planning | 18.75 t provisional | 18 t provisional |
| AW3 gross/car, 75 kg/passenger | 38.25 t | 30.75 t | 30 t |

The proposed tare targets have not been structurally or electromagnetically validated. They assume 100 Wh/kg at battery-system level. The matched 225 kWh case therefore adds 0.75 t/car to the 150 kWh case. Four tonnes of ferrite/car adds another tonne/car before any secondary design changes. Use AW3 and the appropriate dynamic, lateral, thermal, emergency and exceptional load cases for civil work, not empty vehicle mass. Preserve the present 90 km/h capability check even if normal operation is at 80 km/h.

The current Baghdad network uses a separate six-car M6 planning family: 111 m, 720 AW2 and 960 AW3 passengers, and 1,350 kWh gross battery. Its 809 six-car trains cannot be replaced by 809 three-car trains in a fair capital comparison. Rebuild the capacity, timetable, platform, charging and fleet model before calculating a city-wide saving.

### 2. Current factory-gate baseline and exact removal scope

The promoted build-cost file reports:

- Direct materials/supplier modules: **$682,431.18**.
- Final fabrication/integration labour: **5,524 hours at $10/hour = $55,240**.
- Subtotal: **$737,671.18**.
- Unexpected fabrication/rework/logistics/consumables/shop-learning premium: **20%**.
- Factory-gate total: **$885,205.42**; city planning rounds this to **$900,000**.

The older BOM skeleton totals $662,590 direct, $19,841.18 below the promoted candidate. This model retains that entire difference as an unchanged candidate adjustment. Before release, reconcile the component-specific removals against the promoted costing rather than silently mixing revisions.

| Deleted conventional supplier/BOM scope | Per three-car train |
|---|---:|
| Complete bogie group G1–G21 | $125,600 |
| T1 rotary traction motors | $36,000 |
| T2 reduction gearboxes | $15,000 |
| T3 conventional motor controllers | $24,000 |
| T4 conventional traction cooling | $6,000 |
| **Total direct removal** | **$206,600** |

The bogie group does **not** contain T1–T4, so these removals do not overlap. It does contain wheelsets, bearings, primary/secondary suspension, wheel brakes, parking brakes, suspension air supply, motor cradles, flexible couplings, harnesses and related hardware. Deleting the group requires a priced replacement for capture, landing/support, parking and emergency stopping functions.

Common vehicle scope remains costed: body, passenger fit-out, doors, glazing, HVAC, TCMS, train communications, couplers/trainline, battery auxiliaries, charge interfaces, BMS, enclosures, cooling and fire-management provisions. There is no released 17 m carbody BOM justifying a lower body price. The 20% premium is retained on both alternatives.

### 3. Replacement magnetic equipment

Raw ferrite uses the user's assumption, **3,000 kg = $7,000**. At three tonnes/car, a three-car train needs **9 tonnes and $21,000 of raw magnets**. At four tonnes/car it needs 12 tonnes and $28,000. This is not the cost of a finished, retained, inspected array.

All values below are **per three-car train**, not per module. They are supplier/manufacturing budget allocations to be replaced by released quantities and RFQs.

| New magnetic supplier scope | Low | Base | High |
|---|---:|---:|---:|
| Magnetic iron, pole pieces and structural module carriers | $20,000 | $35,000 | $70,000 |
| Lift, guidance and propulsion windings, insulation and potting | $15,000 | $30,000 | $65,000 |
| Magnetic-module inverters/current drivers and local power distribution | $20,000 | $30,000 | $60,000 |
| Gap/current/temperature sensing and local control electronics | $8,000 | $15,000 | $35,000 |
| Magnetic-module coolant circuit, heat exchangers and protection | $5,000 | $10,000 | $20,000 |
| Finished ferrite array assembly, mechanical retention, encapsulation and production QA; excludes raw ferrite | $7,000 | $15,000 | $35,000 |
| **Magnetic hardware subtotal, excluding raw ferrite** | **$75,000** | **$135,000** | **$285,000** |
| Raw ferrite, 3 t/car | $21,000 | $21,000 | $21,000 |
| Fixed capture, landing/support and independent emergency/parking brake hardware | $15,000 | $30,000 | $60,000 |
| Final vehicle integration labour | $50,000 | $65,000 | $100,000 |
| Integration hours at current $10/hour basis | 5,000 | 6,500 | 10,000 |

Supplier fabrication labour inside the magnetic assemblies is separate from final train integration hours; do not count coil fabrication labour twice. A bare STM32 price is not the subsystem price. Sensing, isolation, current control, switching devices, gate drives, wiring, protection, thermal design, redundancy, software, validation and rail-compatible enclosures still have costs.

At 24 modules/car, the central $135,000 train allocation is equivalent to **$1,875 per complete module**, averaged across the 72 modules and shared equipment. This is a procurement target to test, not a verified unit price.

### 4. Train results, battery credit and break-even

The model is:

`Factory = 1.20 × [682,431.18 − 206,600 − battery_credit + raw_ferrite + magnetic_hardware + capture/brakes + (integration_hours × $10)]`

The current BOM allows $75,000 for 675 kWh of battery packs, before separately listed BMS, enclosure, cooling and fire-management scope. Reducing gross storage to 450 kWh at the same pack rate gives a **$25,000 direct credit**, or **$30,000 after the common 20% premium**. The ancillary battery provisions are retained. The 450 kWh duty cycle and charger requirements still require an energy proof.

| Ferrite | Gross battery | Low factory/train | Base factory/train | High factory/train |
|---|---|---:|---:|---:|
| 3 t/car | 225 kWh/car | $764,197 | $872,197 | $1,130,197 |
| 3 t/car | 150 kWh/car | $734,197 | $842,197 | $1,100,197 |
| 4 t/car | 225 kWh/car | $772,597 | $880,597 | $1,138,597 |
| 4 t/car | 150 kWh/car | $742,597 | $850,597 | $1,108,597 |
| Current LM3 | 225 kWh/car | — | **$885,205** | — |

The primary like-for-like result is the first row: **$0.764m–$1.130m/train, central $0.872m**. Per car that is approximately **$255k–$377k, central $291k**, compared with approximately **$295k/car currently**. The smaller-battery three-tonne case is approximately **$245k–$367k/car, central $281k**.

At central assumptions and matched 675 kWh, the magnetic hardware bundle must remain below:

`$206,600 − $21,000 raw ferrite − $30,000 capture/brakes − ($65,000 − $55,240) additional integration labour = $145,840/train`

That is **$48,613/car** for cores, windings, drives, local sensing/control, cooling and finished-array assembly. The central bundle uses $135,000/train and leaves only **$13,008 factory-gate saving, 1.47% of the existing target**. With 450 kWh the break-even bundle rises to $170,840/train, but the additional headroom comes from battery downsizing.

Moving from three to four tonnes of ferrite/car adds **$7,000 direct or $8,400 factory-gate per train**. That arithmetic prices extra raw ferrite only; stronger carriers, altered iron/coils, energy consumption and civil loads must be separately closed. Cheap ferrite makes the concept worth examining, but it does not establish low-cost completed suspension or propulsion.

The current train price itself is a rough-order local manufacturing target, not an established delivered rail-vehicle market price. Compare both alternatives on that common basis.

### 5. Dimensioned narrow-beam elevated civil comparison

The user's proposed change is a substantial structural opportunity: a magnetic guideway can replace the existing wide track deck with a much narrower, deeper beam. Current OpenSourceRail already uses one 2.9 m-wide decked Pi-beam per direction on shared piers. The relevant change is its cross-section and trackform, rather than deleting a second set of piers that the reference does not have.

A provisional **0.8 m-wide × 1.6 m-deep hollow box**, with 0.15 m webs and 0.18 m flanges, has a 0.50 × 1.24 m internal void:

`A = 0.8×1.6 − 0.5×1.24 = 0.660 m²`

| Physical quantity | Current decked Pi | Narrow hollow box |
|---|---:|---:|
| Bare beam area | 1.199 m² | 0.660 m² |
| Bare beam concrete per dual route-km | 2,398 m³ | 1,320 m³ |
| Conventional alignment/plinth concrete | 459.2 m³ | 0 m³ |
| Two retained outside walkway cassettes | 240 m³ | 240 m³ |
| **Total listed superstructure concrete** | **3,097.2 m³/km** | **1,560 m³/km** |
| Bare concrete mass per 25 m beam, 2,500 kg/m³ | 74.94 t | 41.25 t |
| Gross strong-axis second moment of area | 0.1430 m⁴ | 0.1936 m⁴ |
| Shared pier locations at 25 m spans | 40/km | 40/km |

That is **49.6% less listed superstructure concrete** and **35.4% greater gross vertical bending stiffness at equal material modulus**. It is not a validated beam design: lateral bending stiffness is much lower, and torsion, curves, wind, seismic, local magnetic loads, capture loads, prestress, fatigue, deflection and vehicle/guideway control interaction require release calculations. Retaining the same clearance may require a higher support or changed vehicle envelope because the box is deeper.

The reference has one shared column per 25 m support location. Keeping that span retains **40 pier/foundation locations per route-km**. The smaller beam reduces lifted mass and can permit smaller caps or foundations; fewer support locations require a separately qualified longer span.

An unfactored static average-load comparison, with matched LM3 AW3 and 100 kg/m of assumed new reaction hardware, reduces foundation-top vertical load from approximately **3.943 MN to 2.741 MN**, even retaining the current column/cap: **30.5% lower**. This does not mean foundation price falls 30.5%, because lateral loads, soil depth, settlement and minimum construction geometry can govern.

The former $9.038m central cost was a broad scope screen. The revised table below ties supplied beam cost to the new concrete quantity, removes conventional plinths, retains bearings/joints and walkway panels, adds real outside-walkway brackets, and assumes lower handling/installation costs. It holds the earlier magnetic-rail supply price constant so the improvement reflects the new geometry and construction assumptions.

| Nonoverlapping installed-cost scope | Current | Low redesign | Base redesign | High redesign |
|---|---:|---:|---:|---:|
| Dimensioned narrow-box supplied structural components, excluding conventional rail and new walkway brackets | $3,594,160 | $2,333,535 | $2,395,410 | $2,642,910 |
| Conventional steel rail and fastening supplier allowance; provisional allocation, not a separately quoted repo price | $500,000 | $0 | $0 | $0 |
| New passive ferromagnetic functional rail, fabricated profiles/laminations and mounting/adjustment hardware; supply only, installation and QA below | $0 | $850,000 | $1,200,000 | $1,700,000 |
| Additional long cantilever walkway brackets for narrow guidebeams;800/km at$200/$400/$750 supply each | $0 | $160,000 | $320,000 | $600,000 |
| Erection equipment and normal guideway lifts | $779,840 | $428,912 | $545,888 | $740,848 |
| Transport | $584,880 | $292,440 | $380,172 | $526,392 |
| Temporary works | $487,400 | $316,810 | $389,920 | $487,400 |
| Installation labour and supervision, including passive rail installation | $1,169,760 | $701,856 | $818,832 | $1,111,272 |
| Night shift allowance | $194,960 | $116,976 | $146,220 | $194,960 |
| Testing, inspection and magnetic rail metrology/alignment | $292,440 | $292,440 | $336,306 | $380,172 |
| Maintenance equipment relocations; excludes utility relocation | $292,440 | $292,440 | $292,440 | $292,440 |
| Traffic management | $389,920 | $311,936 | $350,928 | $389,920 |
| Supports and foundations; reduced only after structural/geotechnical release | $1,462,200 | $950,430 | $1,169,760 | $1,462,200 |
| **Total per dual-direction route-km** | **$9,748,000** | **$7,047,775** | **$8,345,876** | **$10,528,514** |
| **Difference from current** | — | **−$2,700,225** | **−$1,402,124** | **+$780,514** |
| **Percentage difference** | — | **−27.7%** | **−14.4%** | **+8.0%** |

The central supplied-structure allocation is **$2.395m**, down from $3.594m after conventional rail supply is separately isolated. Bare girder allowance follows the 0.55046 volume ratio with a 5% fabrication allowance. Installation and ordinary erection use 0.70 of their existing budgets, transport 0.65, and supports/foundations 0.80; these are explicit budget assumptions requiring production and site verification. Magnetic alignment QA increases 15%.

The price model explicitly retains two 1 m outside walkways. A 0.8 m spine cannot directly support their previous position beside the 2.65 m vehicle without cantilevers. It allows **800 additional brackets/km**, at **$200/$400/$750 each** in the three scenarios, or **$160k/$320k/$600k supply/km**. Installation remains in the labour row. Walkway live load, bracket fatigue and torsion of the guidebeam remain design requirements.

The new passive rail supply remains **$425/$600/$850 per one-way beam-m**, or **$0.85m/$1.20m/$1.70m per dual route-km**. It includes all ferromagnetic functional faces and mounting/adjustment hardware; installation and QA are separate. Every additional $100 per beam-m adds $200,000 per dual route-km.

A separate successful **$350/beam-m rail supply target**, keeping the central geometry and construction assumptions unchanged, lowers the central total to **$7,845,876/km**. This is a procurement sensitivity, not a rail price proved by the narrow concrete section. Approximately **$7–8m/km can therefore be a conditional optimization target**, while the matched rail-price working case is approximately **$8.35m/km**. A $6m/km outcome is not established by this calculation.

Functional rail kg/m remains an optimizer output; the 100 kg/m mass is only a screening parameter. Solid-versus-laminated steel, saliency, corrosion protection, covers and mounting tolerances must be priced. If linear induction propulsion is selected, price its aluminium/copper secondary explicitly rather than treating an iron lift rail as the complete propulsion secondary.

#### Civil inclusions and exclusions

These rates include two directions of normal guideway, supports/foundations, passive rail supply/mounts, installation, ordinary erection, inspection and metrology. They exclude stations, depots, rolling stock, charging/grid/solar, active signalling/communications, production plant, land, utility relocation, tax/duty, escalation, financing and special sites outside the reference allowance. Add the repository's separate **7% EPC** once at programme level where applicable.

The current rail train already uses batteries/station charging, so the redesign receives no catenary-deletion credit. At-grade and bridge current targets remain **$2.584m** and **$18.0m per dual route-km**; do not apply the elevated saving percentage to these classes.

The repository baseline itself is an unquoted CAD-indexed planning target. Its structural-continuity/bearing and foundation releases remain open. The old broad scenario is preserved under `initial_scope_screen` in the revised JSON: $7.856m/$9.038m/$10.939m. Neither that high case nor the revised high case is a certified upper bound if magnetic or structural feasibility forces a different beam.

See Appendix D3 of this specification for the detailed quantity and cost derivation.

### 6. First three-car pilot and engineering programme

The repeat-production vehicle result does not fund creating or validating a new magnetic railway. The following is a transparent author budget envelope for a first three-car pilot and its development infrastructure. It is not a contractor quote or an incremental cost relative to an already completed conventional programme.

| Pilot programme item | Low | Base | High |
|---|---:|---:|---:|
| Magnetics, structures, embedded controls and systems engineering: assumed 20/60/120 FTE-years at $90,000 per FTE-year | $1.800m | $5.400m | $10.800m |
| Independent review, safety analysis, EMC/environmental/vehicle/guideway testing campaign for a pilot | $0.800m | $2.500m | $6.000m |
| Module magnetic, power, thermal, retention and fault test rigs | $0.500m | $1.000m | $2.500m |
| Prototype winding, ferrite assembly and body/guideway fixtures plus metrology tooling | $0.500m | $1.500m | $4.000m |
| One complete three-car first article, including low-volume fabrication and rework | $1.200m | $1.800m | $3.500m |
| Approximately 1 km single-direction low-height pilot guideway with functional rail, foundations, civil works and instrumentation installation | $2.000m | $4.000m | $8.000m |
| Pilot charging, power supply, modest workshop/test-site adaptation and recovery equipment | $0.400m | $1.000m | $2.000m |
| **Subtotal** | **$7.200m** | **$17.200m** | **$36.800m** |
| Reserve | $1.800m (25%) | $6.020m (35%) | $18.400m (50%) |
| **First pilot programme total** | **$9.000m** | **$23.220m** | **$55.200m** |

The physical first-article train and test guideway are already included; do not add either twice. The engineering rate and FTE-years are editable planning assumptions. The pilot track is approximately 1 km in one direction and at low height, with controlled test-site access, rather than a full passenger railway. Its final layout must provide the actual required acceleration/braking distance, overspeed protection and recovery clearance.

Commercial type approval, line safety authorization, extended reliability demonstration, revenue-service stations and a complete production factory need their own remaining-work scope. The conventional project also requires engineering, tooling and qualification; do not assign it zero remaining NRE while assigning all new development to maglev.

Factory saving cannot be obtained by simply deleting the existing bogie and motor plants. The redesign needs ferrite sourcing/quality control, module core and winding manufacture, encapsulation, power-electronics test, precision-guideway fabrication, metrology and spare-module overhaul/replacement processes. Rebuild the factory make/buy and utilization model, and avoid counting a factory deletion a second time through already discounted local per-train prices.

### 7. Scaling without a false whole-project total

For **100 elevated dual-direction route-km of guideway only**, current cost is **$974.8m** and the three dimensioned redesign scenarios are **$704.778m / $834.588m / $1,052.851m**. The central guideway delta is a potential **$140.212m reduction**. It is not a validated construction saving.

Stations, fleet, depot, charging, signalling and other common assets remain to be added equally. A 100 km simple line with roughly 1 km stop spacing has roughly 101 stations; an example containing only ten stations would not match the stated operating concept. New stations can require different platform/support arrangements, so equality itself must be checked. Fleet count must be derived from the service cycle and reserve policy.

Current Baghdad's $8.666552bn `local_positive` total includes civil, stations/access, six-car rolling stock, final assembly/component plants, line depots, solar/charging, signalling and programme overhead. It cannot be compared with a guideway-only subtotal or an LM3 fleet. Keep the present city as a reference and create a separate maglev scenario with matched passengers/hour/direction, dwell, reliability/reserve, route coverage, energy autonomy and charging limits.

### 8. Cost outputs required from the redesign

Before claiming a cost reduction, the rework should produce:

1. A released magnetic force/thermal/failure model, manufacturing drawings and actual kg/module of ferrite, iron, copper and structural retention.
2. RFQs against the magnetic bundle ceiling, with supplied hardware, final integration labour, test effort and NRE separated.
3. A route passive-rail BOM in kg and finished cost per one-way beam-m, including every lift/guidance/propulsion face and all mounting/tolerance hardware.
4. Civil quantities at AW3 and the governing fault/lateral/thermal loads, including supports, foundations, walkways, bearings, joints, temporary works and alignment QA.
5. A matched 675 kWh base and a separately verified 450 kWh energy/charging sensitivity.
6. An equal-capacity formation/timetable/fleet result before applying the model to Baghdad.
7. A manufacturing and development programme that prices replaced processes and new processes once each.

The corresponding editable numerical input is `maglev_cost_model.json`; the earlier broad civil screen is retained within it.

### Primary current-design sources

All repository links are pinned to the same commit.

- [design/component-catalogue/catalog/buildable-trainset/trainset-build-cost.json](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/design/component-catalogue/catalog/buildable-trainset/trainset-build-cost.json)
- [docs/rolling-stock/light-metro-3car/bom-skeleton.md](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/docs/rolling-stock/light-metro-3car/bom-skeleton.md)
- [lib/templates/civil-cost-model.toml](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/lib/templates/civil-cost-model.toml)
- [lib/templates/civil-cost-calibration.toml](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/lib/templates/civil-cost-calibration.toml)
- [lib/templates/capex-costs.toml](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/lib/templates/capex-costs.toml)
- [lib/templates/rolling-stock.toml](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/lib/templates/rolling-stock.toml)
- [cities/catalogue/west-asia/Iraq/Baghdad/README.md](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/cities/catalogue/west-asia/Iraq/Baghdad/README.md)

The raw ferrite price comes from the user. New magnetic, civil-delta and pilot values are clearly labelled engineering assumptions rather than sourced price claims. Existing repository prices remain planning-grade and require procurement validation.




# Appendix D2. Narrow guidebeam structural comparison

## Narrow guidebeam review: quantities, stiffness and support loads

Read-only source baseline: OpenSourceRail commit **50010ce56370cf6b22dc383c12eebbc224800007**. Geometry below is either current repository planning geometry or an explicitly illustrative candidate. **The candidate dimensions are not a released beam design.** No reinforcement/prestress, local magnetic load, bearing, wind, seismic, geotechnical, fatigue or vehicle–guideway dynamic acceptance is established here.

### 1. The user's structural point is valid, with a revised comparator

A narrow, deeper guidebeam can use substantially less concrete while maintaining or improving vertical bending stiffness. The comparison should therefore model a new cross-section, not merely reduce the train load on the existing section.

However, current OpenSourceRail already uses **one separate beam per direction on a shared double-track pier**. It is not a solid full-width flat bridge. Each existing beam has a 2.9 m track flange and two narrower stems below it. Maglev can remove much of that track flange/trackform and adopt a deeper narrow section, but it does not remove an additional bridge deck that the present model never contained.

Source: [`decked_pi.py` lines 1–48](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/design/component-catalogue/src/osr_mech/civil/decked_pi.py#L1-L48); [`substructure.py` lines 1–28](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/design/component-catalogue/src/osr_mech/civil/substructure.py#L1-L28).

### 2. Actual current cross-section versus illustrative narrow box

#### Current OSR-Pi25, one direction

- Span: 25 m; 20 m is the other catalogue length.
- Flange: **2.900 m wide × 0.220 m thick**, area 0.638 m².
- Two stems: each **0.300 m wide × 0.935 m deep**, combined area 0.561 m².
- Overall depth: **1.155 m**.
- Stem centres: ±0.7175 m from track centre, beneath the standard-gauge rail lines.
- Bare area: **1.199 m²**; concrete density 2,500 kg/m³.
- Derived centroid: **0.774794 m above stem bottom**.
- Derived gross vertical-bending second moment: **I = 0.1429995 m⁴**.

The second moment is calculated from the source rectangles and parallel-axis theorem, not taken from a structural release:

`I = Σ(b h³/12 + A(z_i − z_bar)²)`.

#### Illustrative hollow guidebox, one direction

- Outer width × depth: **0.800 m × 1.600 m**.
- Side walls: 0.150 m; top and bottom slabs: 0.180 m.
- Inner void: **0.500 m × 1.240 m**.
- Area: `0.8×1.6 − 0.5×1.24 =` **0.660 m²**.
- Gross vertical-bending second moment: `(0.8×1.6³ − 0.5×1.24³)/12 =` **0.193624 m⁴**.

| Bare beam quantity | Current Pi | Illustrative guidebox | Change |
|---|---:|---:|---:|
| Width | 2.900 m | 0.800 m | −72.4% |
| Depth | 1.155 m | 1.600 m | +38.5% |
| Concrete area | 1.199 m² | 0.660 m² | **−45.0%** |
| Concrete per 25 m beam | 29.975 m³ | 16.500 m³ | −45.0% |
| Bare concrete mass per beam | 74.94 t | 41.25 t | −45.0% |
| Gross vertical I | 0.143000 m⁴ | 0.193624 m⁴ | **+35.4%** |

The depth change, rather than simply calling it a monorail beam, produces this result. A same-depth narrow rectangle would not necessarily retain stiffness.

**Other structural directions remain important.** Gross lateral-bending I falls from approximately 0.740145 m⁴ for the wide Pi to 0.055350 m⁴ for this narrow box, a reduction of about 92.5%. A closed box has different torsional behavior from an open Pi, which must be calculated with its diaphragms and restraints. Vertical I alone cannot qualify wind response, lateral guidance loads, cant/twist, eccentric walkway loads or transverse stability.

#### Existing prestress and handling information

Current `decked_pi.py` describes a manufacturing envelope, explicitly not an accepted prestress/reinforcement/dynamic design. Its manufacturing study adds 2.36555 m³ of local end-diaphragm concrete to a 25 m Pi, then assumes 120 kg reinforcement/m³, 25 kg prestressing steel/m and 150 kg inserts. This produces **85.51 t manufactured study mass**, compared with 74.94 t bare concrete. Bearing lands, lifting arrangements, concrete strengths and tolerances are still unreleased. Do not price or lift the completed current beam as only 74.94 t, or assume the new box needs no equivalent end details. Source: [`decked_pi.py` lines 156–190](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/design/component-catalogue/src/osr_mech/civil/decked_pi.py#L156-L190).

### 3. Trackform and walkway must be counted consistently

Current elevated trackform is a **40 mm alignment layer over 2.7 m**, plus two **0.38 m × 0.16 m rail plinths**. Its equivalent concrete area is:

`2.7×0.04 + 2×0.38×0.16 = 0.2296 m²/direction`.

It is not a second full structural deck. The **1.0 m × 0.12 m evacuation walkway** is a separate outer cassette, area 0.12 m² per direction. Source: [`slab.py` lines 39–49 and 153–164](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/design/component-catalogue/src/osr_mech/civil/slab.py#L39-L164); [`quantity_model.py` lines 21–45 and 73–94](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/design/component-catalogue/src/osr_mech/civil/quantity_model.py#L21-L94).

| Two-direction route-km quantity | Current | Illustrative guidebox |
|---|---:|---:|
| Bare main beam concrete | 2,398.0 m³ | 1,320.0 m³ |
| Alignment layer and rail plinths | 459.2 m³ | Removed; replacement magnetic interfaces separately priced |
| Retained concrete walkway panels | 240.0 m³ | 240.0 m³ |
| Listed superstructure concrete subtotal | **3,097.2 m³** | **1,560.0 m³** |

The listed concrete subtotal falls **49.6%**, before end diaphragms, reinforcement/prestress, magnetic reaction hardware, walkway brackets/barriers, connections, drainage and ancillary works. The new walkway's support arrangement is deliberately unresolved: an 0.8 m beam under a 2.65 m car needs cantilever/bracket or independent access support to place a usable path beside the vehicle. This support is not free and must not invade the moving vehicle envelope.

Current canonical running-rail quantity is **240,000 kg per dual-route-km**, or approximately **120 kg/m per direction**. It excludes fixation/other hardware. The illustrative maglev load calculation below assumes **100 kg/m per direction** of magnetic/reaction hardware, purely as a sensitivity input; the electromagnetic design must determine the real quantity and cost. It is not an allowance for an already designed rail. Source: `quantity_model.py` lines 59–61.

The 0.8 m concrete box must also be reconciled with the earlier curve-compatible wide magnetic faces. Mounting lips, reaction plates or brackets that provide the required magnetic area/lateral overlap add loads and fabrication. No contradiction should be hidden by comparing bare concrete geometry while omitting the working magnetic interface.

### 4. Transparent simple-beam load and deflection comparison

Use parent-requested gross passenger-load cases: **38.25 t over 16.5 m** for current LM3 and **30.75 t over 17 m** for the maglev candidate. These are converted to continuously distributed vehicle weight for a coarse comparison, not an actual moving wheel/magnet footprint. A full 25 m span is assumed occupied at that average density, which corresponds to an extended consist rather than one isolated 17 m car.

Take L = 25 m, gravity 9.81 m/s² and **gross uncracked E = 30 GPa**, matching the repository's unmeasured reference-concrete elasticity. Ignore prestress camber, continuity, cracking, creep/shrinkage, shear deformation, discrete axle/module footprints and dynamic amplification. Source for E and current explicit study limits: [`engineering/civil_exploration/config/reference.json`](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/engineering/civil_exploration/config/reference.json). Its own superimposed-dead allowance is 1,500 kg/m per track; the comparison below instead uses an explicitly itemized subset so quantities and omissions remain visible.

Dead line masses:

- Current: `1.199×2500 + 0.2296×2500 + 0.12×2500 + 120 =` **3,991.5 kg/m**.
- Maglev: `0.660×2500 + 0.12×2500 + 100 =` **2,050.0 kg/m**.

These omit rebar/tendons, local end diaphragms, detailed brackets/rails fixings, barriers and other ancillaries on both sides; do not call them final installed dead loads.

For a simply supported uniformly loaded beam:

`M_max = wL²/8`; `R_end = wL/2`; `deflection_max = 5wL⁴/(384EI)`.

| Result, one direction | Current Pi | Illustrative guidebox |
|---|---:|---:|
| Dead load | 39.157 kN/m | 20.111 kN/m |
| Gross train load | 22.741 kN/m | 17.745 kN/m |
| Combined load | **61.898 kN/m** | **37.855 kN/m** |
| Maximum total bending moment | **4.836 MN·m** | **2.957 MN·m** |
| One beam-end reaction | 773.7 kN | 473.2 kN |
| Dead-load elastic deflection | 46.4 mm | 17.6 mm |
| Train-load elastic deflection | **27.0 mm** | **15.5 mm** |
| Total elastic deflection, before camber | 73.4 mm | 33.1 mm |

This is evidence for investigating a lighter section with improved vertical response. It is not a capacity or ride acceptance check. Prestress and continuity can change static shape and response; moving load resonance, foundation motion and control interaction can worsen dynamic behavior.

#### Why 33 mm absolute deflection is not directly compared with an 8 mm magnetic gap

The suspension follows the local guideway: clearance depends on **relative vehicle-to-guideway position**, not absolute beam displacement from an unloaded datum. Camber and constructed alignment also affect the permanent dead-load shape.

For illustration only, in the uniformly loaded 25 m case above, the new box's **15.5 mm global live-load deflection** produces approximately **4.13 mm deviation across a centered 12 m chord** after rigid-body height/pitch following is removed. That is obtained from the simple-beam deflection curve at x = 12.5 m versus x = 6.5/18.5 m. It is only one static load case; real module forces, rail joints, tolerances, speed, heave/pitch/roll response and controller dynamics determine the actual relative gap. Neither the global 15.5 mm nor the local 4.13 mm is a pass/fail substitute for coupled analysis.

### 5. Piers and foundations: real axial benefit, no automatic count reduction

The existing layout uses two beam centres **3.5 m apart**, one **1.5 m × 2.0 m** column, and a hollow cap. At the default 8 m pier height:

- Column concrete: `1.5×2.0×8 =` **24.0 m³**.
- Cap concrete: `2.5×7.0×1.2 − 2.0×6.5×0.8 =` **10.6 m³**.
- Total column/cap concrete: **34.6 m³**, or **86.5 t** before reinforcement/inserts.

Source: [`substructure.py` dimensions and hollow-cap constructor](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/design/component-catalogue/src/osr_mech/civil/substructure.py#L17-L102). Current planning has about **40 shared pier tributaries/route-km at 25 m spacing**; detailed endpoint counting is route-dependent.

An interior shared pier receives half the load from each adjacent span in each direction, equivalent to `2wL` under the same full-loading simplification:

| Axial load screen | Current | Guidebox with unchanged column/cap |
|---|---:|---:|
| Superstructure + trains to shared pier | **3.095 MN** | **1.893 MN** |
| Column/cap self-weight | 0.849 MN | 0.849 MN |
| Load above foundation, excluding foundation self-weight | **3.943 MN** | **2.741 MN** |

The superstructure/train reaction falls **38.8%**; retaining current column/cap reduces the illustrated axial load above the foundation by **30.5%**. This gives a concrete basis for studying smaller supports or foundation groups. It does not prove a 30.5% foundation cost reduction.

At unchanged 25 m spans, the support count remains approximately 40/km. Reducing count requires longer spans and new checks; simply narrowing the beam does not remove alternate piers. Smaller bearing transverse spacing and a narrower cap may be possible, but the two train centres and vehicle envelope still govern important load arms. The source currently allows four bearings at a shared internal line and eight at expansion/double-end lines; its 200/km continuity option itself requires structural release. A narrow box needs its own bearing/torsional-restraint layout. Source: [`continuity.py`](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/design/component-catalogue/src/osr_mech/civil/continuity.py).

For example, shrinking column dimensions to 1.2 m × 1.6 m reduces area by 36%, but reduces both gross bending inertias by about **59%**; at equal height and wind force the isolated-column lateral elastic displacement would increase about **2.44 times**. This illustrative size is therefore not adopted by the axial-load arithmetic alone. Wind, seismic displacement, braking/traction, collision, eccentric loading, soil lateral stiffness, overturning, uplift and settlement may govern. Lighter dead weight also supplies less stabilizing resistance to uplift/overturning.

Foundations require actual ground data, pile/shaft capacity, group effects and settlement constraints. Fixed survey/mobilization/test costs and minimum practical pile numbers do not scale smoothly with vertical reaction. The civil estimate can show conditional support/foundation sensitivities, but not a release or supplier saving claim.

### Cost-model implication

Use the **49.6% listed superstructure concrete reduction**, the new magnetic/evacuation interface quantities, actual fabrication/erection methods and conditional substructure scenarios as explicit BoQ inputs. Retain stations, access, property/utility constraints, drainage, special crossings and route interfaces. The user's narrower structural concept has a stronger quantitative basis than a calculation that only subtracts a few tonnes of vehicle mass from the existing pi-beam; its full benefit depends on completing the guidebeam and support design.



# Appendix D3. Narrow guidebeam quantity-led cost revision

## Dimensioned narrow-guidebeam civil cost revision

**Purpose:** quantify the user's proposal to replace a broad rail deck with one narrow magnetic guidebeam in each direction. This supersedes the generic primary civil screen while preserving its record. All dimensions and new costs below are preliminary, and no structural, geotechnical or magnetic design is certified.

The selected cost case retains the earlier magnetic-rail supply prices. It gives **$7.048m / $8.346m / $10.529m per dual route-km**, compared with **$9.748m** currently. The new central saving is **$1.402m/km, or 14.4%**. A separately achieved $350 per one-way beam-m passive rail target gives **$7.846m/km** at the same central civil geometry.

### Geometry and quantities

Current code defines a Pi flange 2.9 m × 0.22 m, plus two 0.30 m × 0.935 m stems. Thus A=0.638+0.561=1.199 m² and overall depth=1.155 m. The proposed box has outer0.8×1.6m, inner0.5×1.24m, giving0.66m².

At 25 m spans there are 80 one-direction beams and 40 shared support locations per dual route-km. Bare beam concrete falls2,398→1,320m³. Removing459.2m³ of conventional plinth/alignment concrete but retaining240m³ of outside walkway concrete gives **3,097.2→1,560m³/km**, a **49.6% reduction** in this subtotal. End diaphragms, reinforcement, prestress, barriers and local mounting details are not released in this quantity comparison.

Bare lifting mass at2,500kg/m³ falls74.94→41.25t for a25m beam, before release-dependent diaphragms/steel/inserts. The existing manufacturing study can exceed the bare mass; compare complete shipping weights before choosing a crane, transporter or launching system.

Gross vertical I increases0.14299949→0.193624m⁴, approximately35.4%. Gross lateral I decreases0.740145→0.05535m⁴. A closed box also changes torsion behavior substantially, but no global stiffness claim follows from one strong-axis number. The design must close lateral sway, wind, curvature, restraint, torsion, temperature, fatigue, prestress and magnetic gap-control response.

The unchanged outer1m walkways require cantilever support outside the vehicle clearance envelope. At2.5m bracket spacing,2,000one-waym/km require800brackets. Central supply allowance is800×$400=$320,000/km; low/high use$200/$750 per bracket. Bracket steel, anchors, torsional loading and installation access remain design inputs. Do not use the narrow beam as a reason to drop egress scope.

### Vertical load and foundations

Use AW3, not empty vehicle mass: old38.25t/16.5m=2,318.18kg/m; new30.75t/17m=1,808.82kg/m for the matched225kWh/car,3t-ferrite case.

The current screening dead mass is3,991.5kg/one-waym: beam+plinths+walkway+120kg/m rails. New dead mass is2,050kg/m: box+walkway+assumed100kg/m functional rail/hardware. That new rail mass is an editable placeholder; magnetic design must supply the real cross-section.

Unfactored average static line loading is61.898 versus37.855kN/m. One shared25m tributary pier carries two directions:3,094.9 versus1,892.8kN superstructure. Retaining the current1.5×2.0×8m column and10.6m³ cap adds848.565kN in each case, giving **3,943.5 versus2,741.3kN**, approximately**30.5% lower axial load** before foundation self-weight. This is not a load combination, peak moving-load result, seismic check, or geotechnical design.

The current cap is7m wide with10.6m³ net concrete. A geometrically possible4.8m cap with6.36m³ net concrete can be screened while retaining the original column, but its bearing spread and bending/temporary/egress load paths need checking. Reducing the column to1.2×1.6m would reduce its bending inertias to0.4096 of current values at equal height; roughly2.44times lateral drift at equal force is a reason not to claim that smaller column is already justified.

The central cost model assumes20% less support/foundation cost, conditional on a released cap/ground design. At25m spans it does **not** reduce the40pier/foundation locations. Pile counts, lengths and diameters must respond to actual soil, lateral and settlement requirements. Extending spans to reduce pier count is a separate design iteration with fourth-power deflection sensitivity.

### Reconcile the supplied-structure budget

The current installed total is$9.748m. Its unquoted42% supplied-components allocation is$4.094160m. Isolate$0.500m conventional rail/fastener supply, leaving$3.594160m to decompose as follows.

| Structural supplier allowance | Current | Low narrow box | Base narrow box | High narrow box |
|---|---:|---:|---:|---:|
| Fabricated prestressed girder budget indexed to actual bare volume | $2,248,125 | $1,237,500 | $1,299,375 | $1,546,875 |
| Deleted conventional alignment layer/direct-fixation plinth supplier scope | $250,000 | $0 | $0 | $0 |
| Retained bearing/expansion-joint supplier scope | $900,000 | $900,000 | $900,000 | $900,000 |
| Retained two outside1m concrete walkway panel supplier scope | $120,000 | $120,000 | $120,000 | $120,000 |
| Retained miscellaneous structural supplier allowance | $76,035 | $76,035 | $76,035 | $76,035 |
| **Subtotal** | **$3,594,160** | **$2,333,535** | **$2,395,410** | **$2,642,910** |

The current girder allocation uses the magnitude implied by the repository calibration,12m×0.30×2398/3840=$2.248125m. This is equivalent to$937.50/m³ of bare-beam quantity for the index; it is **not a concrete purchase price or a quotation for finished prestressed beams**. Applying the same index to1,320m³ gives$1.2375m. Low/base/high fabrication allowances are1.00/1.05/1.25 times that sum for the new form, processing and release-dependent details.

The plinth, walkway and residual allocations are explicit author budgeting assumptions within the fixed baseline total. Bearing/joint allowance is retained. They are not separately verified existing purchase orders.

### Complete installed-scope model

| Cost scope | Current | Low | Base | High |
|---|---:|---:|---:|---:|
| Dimensioned narrow-box supplied structural components, excluding conventional rail and new walkway brackets | $3,594,160 | $2,333,535 | $2,395,410 | $2,642,910 |
| Conventional steel rail and fastening supplier allowance; provisional allocation, not a separately quoted repo price | $500,000 | $0 | $0 | $0 |
| New passive ferromagnetic functional rail, fabricated profiles/laminations and mounting/adjustment hardware; supply only, installation and QA below | $0 | $850,000 | $1,200,000 | $1,700,000 |
| Additional long cantilever walkway brackets for narrow guidebeams;800/km at$200/$400/$750 supply each | $0 | $160,000 | $320,000 | $600,000 |
| Erection equipment and normal guideway lifts | $779,840 | $428,912 | $545,888 | $740,848 |
| Transport | $584,880 | $292,440 | $380,172 | $526,392 |
| Temporary works | $487,400 | $316,810 | $389,920 | $487,400 |
| Installation labour and supervision, including passive rail installation | $1,169,760 | $701,856 | $818,832 | $1,111,272 |
| Night shift allowance | $194,960 | $116,976 | $146,220 | $194,960 |
| Testing, inspection and magnetic rail metrology/alignment | $292,440 | $292,440 | $336,306 | $380,172 |
| Maintenance equipment relocations; excludes utility relocation | $292,440 | $292,440 | $292,440 | $292,440 |
| Traffic management | $389,920 | $311,936 | $350,928 | $389,920 |
| Supports and foundations; reduced only after structural/geotechnical release | $1,462,200 | $950,430 | $1,169,760 | $1,462,200 |
| **Total/dual route-km** | **$9,748,000** | **$7,047,775** | **$8,345,876** | **$10,528,514** |

Base erection factor0.70 can be viewed as roughlyone-third fixed work plus two-thirds scaling with bare lifting mass ratio0.55. Base transport0.65 likewise reflects a retained handling floor plus lower load. They require actual equipment/permit/logistics pricing. A narrow shipment helps width constraints, but25m length still imposes route/handling restrictions.

Base installation factor0.70 retains40% fixed work and allows the balance to broadly follow the0.504 superstructure-concrete/trackform ratio. New precision QA is increased15%. Temporary works, night shifts and traffic management receive smaller savings; maintenance relocations are unchanged. These factors are editable construction assumptions, not automatic consequences of cutting concrete.

The new magnetic rail supply stays at$425/$600/$850 per one-waym, identical to the earlier screen. Every$100/m change moves the dual-route-km total by$200,000 before EPC. A standalone$350/m base rail target changes only that row and gives **$7,845,876/km**. The geometry study has not proved that rail price.

Low/high are scenarios, not confidence bounds. The previous broad screen's$10.939m high case is retained for context, and a failed magnetic/lateral design can force costs beyond either shown high value. Do not treat the favorable geometry as a construction release.

### Scope, source and handoff controls

Stations, depot/factory, rolling stock, charging/grid/solar, active signalling, land, utility relocation, duty/tax, escalation, financing and exceptional local works remain outside these guideway rates. Add the separate7%EPC at programme level once where applicable. Train and pilot/NRE costs are unchanged from the existing note.

Primary numerical handoff: `maglev_cost_model.json`. Its `civil.rows` preserves the original workbook-compatible shape and adds `additional_walkway_brackets`; `civil.narrow_beam` contains geometry and decomposed budget; `initial_scope_screen` retains the original civil result; `civil.lower_rail_supply_target_sensitivity` isolates the cheaper rail target.

Current-design sources, all pinned to the same commit:

- [decked_pi.py](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/design/component-catalogue/src/osr_mech/civil/decked_pi.py)
- [viaduct-quantity-cost-model.toml](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/docs/civil/viaduct-quantity-cost-model.toml)
- [viaduct-load-model.toml](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/docs/civil/viaduct-load-model.toml)
- [viaduct-design-basis.md](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/docs/civil/viaduct-design-basis.md)
- [viaduct-substructure-kit.md](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/docs/civil/viaduct-substructure-kit.md)
- [civil-cost-model.toml](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/lib/templates/civil-cost-model.toml)
- [civil-cost-calibration.toml](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/lib/templates/civil-cost-calibration.toml)

Detailed independent source/geometry review: Appendix D2 of this specification.




# Appendix E. Manufacturing independence and make/buy strategy

## Industrial strategy: what ferrite maglev could change in OpenSourceRail's make/buy model

Read-only inspection of OpenSourceRail commit **50010ce56370cf6b22dc383c12eebbc224800007**. Current source statements are planning intentions, not evidence of completed procurement or qualified manufacturing. Proposed maglev manufacturing choices below are engineering recommendations, not existing supplier commitments.

### Main finding

**The stronger potential benefit is ownership of the running-gear product and its repair supply chain, even if total initial CAPEX savings are modest.** A successful fixed-array maglev could eliminate purchases of wheelsets, axle bearings, rotary traction machines and reduction gears, together with many associated wear and overhaul tasks. Locally fabricated magnet cartridges, coils and guideway components could replace those specialized assemblies.

That does not remove propulsion, electronics, material suppliers or product qualification. It changes the purchase boundary: the railway buys specified materials and electrical components and takes responsibility for designing, manufacturing, validating and supporting the magnetic suspension/linear drive. The result can improve supplier choice if interfaces and acceptance tests are open and multiple sources are qualified. Until those replacements are demonstrated, lower dependence on established rail-running-gear vendors and lower whole-life cost remain separate claims.

### 1. What the current design actually intends to buy and make

The [LM3 localization plan](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/docs/rolling-stock/light-metro-3car/localization-plan.md#L3-L26) explicitly phases localization:

| Current system | Initial production intention | Local scope and later purchase boundary |
|---|---|---|
| Bogies | **Buy complete qualified bogies for prototype and approximately the first 20–30 trainsets** | Initially inspection, wheel reprofiling, brake service, harnesses and installation. Later local frame welding and final assembly after process/dimensional/NDT/fatigue capability and supplier audit. Continue buying qualified wheels, axles, bearings, suspension, brakes, motors and gearboxes. |
| Rotary traction | Buy matched motor/controller sets | Local mounts, coolant manifolds, cables and harnesses. Motor/controller localization follows dynamometer, insulation, EMC, vibration and safety evidence. |
| Body | Local from first article where capability exists | Welded S355 structure, modular GFRP panels, nose, interiors and final assembly, subject to manufacturing and material release. |
| Doors | Buy drive, lock, sensors, emergency-release and controller kits | Local leaves, frames, rails, housings, thresholds, adapters and harnesses; mechanisms/controllers require further qualification. |
| Articulation | Buy bearings/joints, anti-lift elements, elastomers and bellows | Local steel adapters, support frames, floor bridge, covers and service guides. |
| Windows | Buy complete safety-glazing cassettes | Local aperture frames, drains and installation; local glazing requires its own material/system qualification. |
| Batteries | Buy qualified cells/modules and BMS/protection/detection components | Local enclosures, vents, cooling manifolds, harnesses and pack integration. No cell factory is assumed. |

There is a source-scope distinction to retain in the final comparison: the [BOM skeleton](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/docs/rolling-stock/light-metro-3car/bom-skeleton.md#L128-L157) labels bogie frames MAKE, while the localization plan buys complete early-production bogies. These describe different production stages. Neither proves that early purchased qualified bogies will cost the same as the later frame-and-component BOM estimate.

The frame itself is a conventional welded steel design. The [bogie description](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/docs/rolling-stock/light-metro-3car/bogie.md) specifies new fabricated frames rather than recovered freight-frame splices, with separate supplier-component interfaces and common powered/trailer spares. Thus “eliminate buying a complete bogie” is meaningful for the initial fleet; “eliminate all bogie manufacture and all associated material cost” is a different and larger claim.

The [supplier-anchor source](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/lib/templates/trainset-supplier-anchors.toml#L1-L16) already calls for supplier-neutral interfaces and qualified local equivalents. Named motor, gearbox, wheelset, bearing, suspension and brake families establish interfaces and evidence targets; they are not binding brand choices or accepted quotations. A maglev benefit should therefore be measured against this open, gradually localized wheel-rail baseline, not only against buying a closed turnkey train.

### 2. Baghdad already contains a local manufacturing alternative

The current programme's four positive-margin manufacturing options are **bogies, motor/inverter sets, battery packs and door cassettes**. Window-cassette manufacture is negative in that particular unquoted whole-order model, so it is excluded from the positive-margin selection. Source: [programme review](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/cities/catalogue/west-asia/Iraq/Baghdad/engineering/programme-recalculation/README.md#L44-L56), [component make/buy rows](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/cities/catalogue/west-asia/Iraq/Baghdad/engineering/programme-recalculation/component-make-buy.csv).

Its production boundaries are precise:

- **Bogie:** local frames, welding, machining, assembly and rig tests; wheels, axles, bearings and selected suspension/brake parts remain imported until qualified.
- **Motor set:** local housing, winding, rotor assembly and testing; inverter, magnets and selected laminations remain imported.
- **Battery pack:** local casing, busbars, cooling, integration and test; LFP cells and BMS remain imported.
- **Door:** local panels, mechanisms, machining, assembly and fixtures; safety controllers and selected actuators remain imported.

These boundaries are controlled in [`baghdad-programme-recalculation.toml` lines 92–150](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/lib/templates/baghdad-programme-recalculation.toml#L92-L150). The programme includes process machinery, facilities, qualification and residual imported input costs; it does not treat a locally assembled product as entirely domestic. Its [industry record](https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/cities/catalogue/west-asia/Iraq/Baghdad/engineering/programme-recalculation/industry.json) records missing supplier quotes/technology-license records, unaccepted first articles and unmeasured annual production cycles. The economics are planning sensitivities, not achieved savings or a ready factory.

### 3. What would shift in a locally made maglev

| Scope | Potential local manufacture/integration | Remaining specified inputs or services |
|---|---|---|
| Ferrite array | Cartridge metalwork, mechanical retention, polarity-controlled assembly, sealing, dimensional checks, force/gap bench testing and replacement kits | Grade-controlled ferrite blocks with magnetic properties versus temperature, geometry/polarity consistency and batch traceability. Buying $7,000 of raw magnets does not buy an assembled, tested running-gear system. |
| Linear propulsion | Motor frames, winding, insulation/impregnation, cooling, assembly and test | Copper conductor, insulation/resins, electrical steel/laminations if required by the chosen topology, connectors and qualified power electronics. A linear motor is still a motor. |
| Static lift and active stabilization | Mechanical pole structures, winding, harnesses, controller boards/firmware and system integration where capable | Power semiconductors, gate drivers, DC-link capacitors, isolation, current/gap sensors, microcontrollers and other electronic components. STM32 availability does not establish the complete channel's timing or failure behavior. |
| Passive guideway | Concrete/structural steel fabrication, reaction-surface mounting, adjustment, survey and installation | Material with specified magnetic/structural properties; conductive reaction plate if the chosen LIM requires it; precision metrology and qualification equipment. Laminated electrical steel is topology-dependent, not assumed for every metre of passive rail. |
| Vehicle shell and interiors | Similar local manufacture to the present reference, with redesigned load paths and cartridge access | Existing glazing, door safety, HVAC, fire/protection and other supplier inputs remain unless separately localized. |
| Battery system | Local pack integration and enclosures, potentially a different capacity after energy analysis | Cells, BMS/protection parts and evidence remain required; magnetic suspension does not create a local cell supply chain. |

The raw-input route can remove the need for precision wheel/axle manufacture, bearing manufacture and gearbox tooth/heat-treatment capability from the railway's own industrial programme. However, its new magnetic material, coil-insulation, control/protection, guideway-geometry and system-test requirements must be budgeted explicitly. No local-content percentage is justified without a priced, origin-traced MBOM and supplier-capability audit.

### 4. Maintenance and spare-parts implications

The **credible mechanism for savings** is removing wheel reprofiling, axle-bearing service, gearbox lubrication/overhaul, rotary-motor bearing work, and ordinary wheel/rail contact wear where those parts and contact functions are actually absent. It also removes the need to stock those specific assemblies. A successful repeatable open magnet/coil cartridge could be fabricated or repaired by more than one qualified workshop using the same drawings and acceptance test.

Replacement work includes magnet retention and fracture checks, force/gap verification, sensor calibration, power-electronics and insulation diagnosis, cooling maintenance, reaction-surface/guideway alignment and corrosion inspection, and protection/recovery hardware maintenance. Mechanical stopping/parking/capture devices, if the final safety design needs them, retain their own moving/wear parts. Emergency contact and recovery surfaces must be included rather than counted as nonexistent.

Fewer moving parts gives a reason to investigate reduced maintenance; it does not quantify fleet availability. Compare measured **failure rate, repair time, diagnostic coverage, module replacement time, spare availability, energy use and service disruption**. A failed inexpensive gap sensor or unrepairable custom power board can immobilize a car; a guideway alignment fault can block every following car. Sensor/electronic common causes and no-mainline-switch recovery must be included in availability estimates.

### 5. Input specification additions for industrial independence

1. **Own the product definition:** release native drawings, material/grade limits, winding/polarity maps, firmware/build instructions, interface control documents, calibration procedures and pass/fail test fixtures. Open shape files alone do not enable equivalent manufacture.
2. **Specify substitutability by evidence:** define magnetic force/stiffness/temperature acceptance envelopes, electrical/thermal limits, geometry and communications behavior. Qualify alternative components against the same tests instead of relying on a brand or a marketplace material name.
3. **Separate bought inputs from local value added:** give every MBOM row its supplier/material source, local operation, process cost, yield, inspection/test time and qualification status. Do not count imported cells, magnets or semiconductors as locally made because they are assembled locally.
4. **Price the owner-as-integrator role:** include electromagnetic design, control/protection engineering, structural/thermal/EMC tests, winding/assembly tooling, field/gap rigs, supplier qualification, first articles and test-guideway work as explicit non-recurring investment.
5. **Prove repairability:** demonstrate replacement and recalibration of a failed cartridge/power module at depot level, traceability of repaired units, stock requirements and controlled firmware/component substitution. Use observed durations and failures for maintenance/fleet economics.

A fair comparison should report **initial programme CAPEX**, **foreign-exchange exposure**, **qualified supplier alternatives**, **local repair capability** and **whole-life service cost** separately. An industrial-independence gain can be worthwhile even when civil CAPEX barely changes. It becomes a demonstrated advantage only when the local magnetic product and its repair chain are qualified and economically reproducible.



# Appendix F. Repository integration map

## OpenSourceRail ferrite maglev rework map and current baseline

Read-only source inspection. Source baseline: `modernecotech/OpenSourceRail` commit **50010ce56370cf6b22dc383c12eebbc224800007**, committed 2026-10-20 09:51:26 UTC, message “Refresh Baghdad archives and book with qualified connection evidence”. Files were fetched through GitHub at that commit. No repository changes, generator runs, tests, physical checks, or releases were performed.

Pinned source URL prefix: `https://github.com/modernecotech/OpenSourceRail/blob/50010ce56370cf6b22dc383c12eebbc224800007/`.

### 1. The current comparator must be named precisely

| Item | LM3 detailed reference | Baghdad active city family |
|---|---:|---:|
| Profile | `light-metro-3car` | `metro-6car` |
| Cars | 3 | 6 |
| Length | 49.5 m, nominal 16.5 m modules | 111 m |
| Planning tare | 78.75 t | 204 t |
| Tare per car, arithmetic | 26.25 t | 34 t |
| AW2 passengers | 360 | 720 |
| AW3 crush passengers | 480 | 960 |
| Gross / usable LFP | 675 / 540 kWh | 1,350 / 1,080 kWh |
| Maximum speed | 25 m/s (90 km/h) | 28 m/s (~100 km/h) |
| Active planning unit CAPEX | $900,000 | $1,680,000 |

Sources: `lib/templates/rolling-stock.toml` lines 100–120 and 147–165; `lib/templates/capex-costs.toml` lines 79–84. The LM3 mass is a controlled planning target, not measured prototype mass: detailed README lines 341–355 identifies **75.308 t modeled subtotal + 3.442 t reserve = 78.75 t**. An unpromoted lightweight study has 73.376 t subtotal and 76.818 t with reserve (same README near line 318). Neither number should be described as a weighed vehicle.

The current design already has onboard LFP and station charging, with no continuous catenary. The maglev comparison gets **no new catenary removal credit**. `docs/ARCHITECTURE.md` lines 215–228 and 241–256; `lib/templates/rolling-stock.toml` lines 7–18.

User's 17 m car should be introduced as a distinct module and checked for consist length, platform fit and coupling gaps. Changing from LM3's 16.5 m reference is a real interface change, although it is modest. A three-car 51 m maglev is not interchangeable with Baghdad's 111 m six-car set at the same train count.

#### Current LM3 factory-gate build record

Authoritative generated record: `design/component-catalogue/catalog/buildable-trainset/trainset-build-cost.json`.

| Component of estimate | USD/trainset |
|---|---:|
| Direct materials and supplier modules | 682,431.18 |
| Labour: 5,524 h at $10/h | 55,240.00 |
| Subtotal | 737,671.18 |
| Unexpected local fabrication/rework/logistics/shop-learning premium, 20% | 147,534.24 |
| Total | **885,205.42** |
| Rounded active planning unit | **900,000** |

The record calls itself rough-order planning, not a supplier quote or signed production budget. It excludes route/platform compatibility changes, supplier certification and homologation campaigns, warranty and initial spares, and production-plant fixtures/tooling (in a separate allowance). Do not label $885k an assured turnkey delivered price.

Its included fitout base subtotal is $146,750: $17,500 floors/seats/rails/lighting, $17,250 three HVAC units, and $112,000 windows/doors/sills/end glass. These survive the drivetrain redesign unless individually redesigned.

The older BOM skeleton remains useful for estimating component deltas, but its **$662,590 direct total is not the promoted $682,431.18 actual candidate subtotal**. It also contains stale $1.0M prose near line 244 while the active controlled unit is $900k. `docs/cost-model.md` is generated by `tools/automation/generate-cost-model.py`; hand editing it would create another conflict.

#### Older skeleton component cost anchors useful for delta estimates

Source: `docs/rolling-stock/light-metro-3car/bom-skeleton.md` lines 93–177. These are planning/RFQ anchors, not qualified vendor prices.

| Scope | Three-car subtotal | Treatment in maglev estimate |
|---|---:|---|
| Body and interior B1–B29 | $233,200 | Retain most; redesign safety frame and magnet attachments |
| Bogies G1–G21 | $125,600 | Conventional running gear removed, but braking/recovery/containment functions need replacements |
| Rotary PMSMs T1 | $36,000 | Remove rotary machines; replace by linear propulsion |
| Reduction gears T2 | $15,000 | Remove |
| Traction inverters T3 | $24,000 | Reuse cost concept only; linear motor control/hardware changes |
| Three 225 kWh battery packs T5 | $75,000 | Resize only against route/charging/degraded operation model |
| BMS T6 | $4,500 | Retain/resize |
| Battery enclosures T8 | $6,000 | Retain/resize |
| Battery thermal/offgas T9 | $10,800 | Retain/resize |
| Battery water mist T10 | $9,000 | Retain subject to fire concept |
| Three 24 kW HVAC units T14 | $17,250 | Retain/thermal duty check |
| Power/traction/thermal subtotal T1–T23 | $266,450 | Do not delete as a group |
| Electronics subtotal | $34,340 | New safety channels and gap sensors may increase cost |
| Other safety subtotal | $3,000 | Retain/rework |

The $125,600 bogie group includes frames $24k, wheelsets $18k, bearings $12k, springs $10.8k, dampers $3k, brake discs $12k, calipers $12k, parking brakes $2.4k, and other pivots/guides/sensors/harness/mounts/compressor. Treating this whole group as savings without replacement brake/park/recovery/support provisions overstates the net benefit. Body group already includes $30k articulations, $90k powered doors, couplers and crash absorbers; the design still has mechanical movement outside doors/HVAC unless these interfaces change.

### 2. Current civil cost basis

Source: generated `lib/templates/civil-cost-model.toml` lines 15–23, 55–89; input `lib/templates/civil-cost-calibration.toml`; canonical quantities `design/component-catalogue/src/osr_mech/civil/quantity_model.py`.

| Civil class | Current USD/dual-route-km |
|---|---:|
| At grade | 2,584,000 |
| Elevated | **9,748,000** |
| Bridge | 18,000,000 |

These are reference planning costs excluding land, tax/duty, utility relocation, escalation and financing. The current elevated value is already reduced from the retained $12M/km benchmark by quantity indexing: 30% cost share follows beam concrete (2,398 vs 3,840 m³/km), 10% bearings (200 vs 320/km), 5% deck gaps (10 vs 40/km), and 55% remains unscaled. Reduced bearing/joint counts depend on an open structural-continuity/connection design. Do not claim that reducing car live load proportionally reduces the whole $9.748M/km.

The current quantity model has two tracks, 25 m primary spans, reference 8 m pier height, 1 m × 0.12 m walkways per track, **240 t of running rails/route-km**, approximately 6,156 direct-fixation seats/km, and zone-specific foundations (source lines 21–27, 59–94). A monorail-maglev branch must replace trackform/rail quantities with actual guidebeam, reaction surface, magnetic gap adjustment and protection quantities; keep evacuation access, drainage, substructure and special structures.

The cost calibration offers an unquoted low-confidence allocation of the elevated rate: components 42% ($4.09416M), erection 8% ($0.77984M), transport 6% ($0.58488M), temporary works 5% ($0.4874M), labour 12% ($1.16976M), night possessions 2% ($0.19496M), QA 3% ($0.29244M), relocation 3% ($0.29244M), traffic management 4% ($0.38992M), supports/foundations 15% ($1.4622M). This is a scope allocation, **not an independent quoted bill of quantities**. “Relocation” in this allocation must not be confused with excluded citywide utility relocation.

The cited whole-beam launcher procurement assumption is 18 at $9M central unit, explicitly unquoted and excluding transporters/shipping/crews/maintenance and other scope. Existing local factory capacity is not free or automatically qualified.

#### Baghdad scale

Current generated sources `cities/catalogue/west-asia/Iraq/Baghdad/README.md`, `.../engineering/programme-recalculation/README.md`, and input `lib/templates/baghdad-programme-recalculation.toml` report 513.336 route-km, 56.73% elevated, 159 stations, 14 line depots and 809 six-car sets. Current local-production programme CAPEX is about $8.667bn versus matched bought-components programme $8.795bn. These totals include much more than running viaduct and trains.

Compare at equal AW2/AW3 capacity, passengers per hour per direction, route, speeds, station interfaces, operating hours and recovery assumptions. A 360-passenger three-car replacement would require a service/fleet recalculation to preserve a 720-passenger reference duty. Do not reuse 809 as the number of three-car replacements.

### 3. Actual integration map

The following paths exist in the inspected source baseline. Suggested new files/modules are explicitly suggestions rather than claims of current implementation.

| Rework area | Existing source paths | Required change for a controlled maglev variant |
|---|---|---|
| Architecture and requirements | `docs/ARCHITECTURE.md`; `docs/rfcs/`; `lib/templates/rolling-stock.toml` | Add explicit separate architecture identifier (suggested `ferrite-pm-maglev-study`), freeze static lift topology, passive guideway interface, onboard propulsion, protection and acceptance limits. Retain wheel-rail reference. Existing profile comments require powered/trailer bogies and common PMSM architecture. |
| Family geometry | `design/component-catalogue/src/osr_mech/family_definition.py`; `common.py`; `rolling_stock/trainset.py` | Replace hardcoded bogie placement only in a new branch. Family definition validates bogie geometry; trainset lines 74–87 repeats one powered/trailer pair per car. New magnet/support module IDs and 17 m geometry need separate rules. |
| Product/CAD build | `.../osr_mech/buildable_trainset.py`; `freecad_trainset.py`; `freecad_product_library.py`; `engineering_definition.py`; `freecad_engineering_definition.py`; `neutral_manufacturing_exports.py` | Add body load paths, mechanically retained ferrite cartridges, onboard motor/gap-control assemblies, rail capture, service access, brake/park/recovery and cooling. Generate FreeCAD/IFC, drawings, manifests and neutral manufacturing outputs from the same inputs. Ferrite must not silently become load-bearing safety structure. |
| Mass and dynamics | `.../osr_mech/vehicle_mass_properties.py`; `engineering/analysis/analysis-register.toml` | Reuse mass provenance, uncertainty, CG and inertia logic, but replace axle reaction output with distributed magnetic support forces and fault redistribution. Existing function assumes static two-support bodies and rectangular four-wheel bogies (lines 139–218). Uncertainty and growth reserve must be retained. |
| Civil geometry and quantities | `.../osr_mech/civil/`; `buildable_civil.py`; `civil_systems_integration.py`; `civil/quantity_model.py`; `lib/templates/structures.toml`; `lib/templates/track-geometry.toml` | Add guidebeam section/reaction surfaces/tolerances, magnets-to-guidebeam cross section, safe maintenance/evacuation clearances, foundations, joints and thermal alignment. Avoid treating conventional rail beam deflection tolerance as magnetic-gap tolerance. |
| Structural study engine | `engineering/civil_exploration/config/reference.json`; `config/system-options.json`; `schemas/`; `engineering/design_engine/` | Add maglev load-footprint schema and electromagnetic/vehicle/beam coupled dynamics. Current civil reference uses moving axles and 2 m triangular rail-load distribution, while current integration is one-way mass-to-axle sensitivity. Qualify magnetic solver and independent benchmarks before using it as evidence. |
| Material/supplier inputs | `lib/templates/trainset-supplier-anchors.toml`; `trainset-cots-candidates.toml`; `.../osr_mech/trainset_supplier_anchors.py`; `trainset_cots_candidates.py` | Add supplier evidence for ferrite grade, Br/Hc versus temperature, tolerances/coating, mechanical retention, batch traceability, laminations/reaction rail, coils, sensors and power stages. Keep user's $7k/3t ferrite as an unquoted raw-material assumption. |
| Manufacturability | `lib/templates/trainset-manufacturing-methods.toml`; `.../osr_mech/trainset_manufacturing_methods.py`; `industrialisation.py`; `fabrication_assembly_twin.py`; `engineering/industrialisation/` | Add magnet handling/assembly forces, polarity checks, segment replacement, inspection, motor/gap calibration, gauges, fixtures, yield/scrap, labour and first-article plan. Large arrays are not just magnet raw material. |
| Energy and thermal | `lib/templates/battery-profiles.json`; `.../osr_mech/battery_profiles.py`; `pack_thermal.py`; `network_energy_duty.py`; `network_energy_control.py`; `crates/osr-sim/src/battery.rs`, `energy.rs` | Include continuous static control loads, motor efficiency map, magnetic/reaction-rail losses, propulsion and regeneration limits, HVAC high-ambient duty, charger dwell/power, degraded charging, battery end-of-life and cooling. The 150 kWh/car concept must pass the actual service simulation. |
| Simulation and operations | `crates/osr-sim/src/physics.rs`; `train.rs`; `vehicle_systems.rs`; `scenario_file.rs`; `fault.rs`; `crates/osr-design`; `osr-alignment`; `osr-routing` | Add explicit maglev physics/parameter serialization, force maps, gap saturation/fault modes, braking to zero and safe stop, speed/curve/grade limits, fleet/energy consequences, depot and route topology. Current simple kinematic power calculations are not an electromagnetic acceptance model. |
| Runtime control | `crates/osr-traction`; `osr-brake`; `osr-bms`; `osr-tcms`; `osr-atp`; `osr-odometry`; `osr-derailment`; `control-electronics/safety-controller-selection.md` | Add separately justified gap/stability protection and actuator safety. STM32 class is an implementation candidate, not an accepted safety channel. Existing architecture says safety channel not yet selected (lines 354–367). Wheel-derived odometry/hot-axle monitoring must be reassessed. |
| Interface safety | `docs/ARCHITECTURE.md` interfaces I1–I11; `crates/osr-core`; `osr-proto`; `osr-supervision-contract` | New lift/gap/propulsion data and safety interfaces require hazard allocation. Current “only I1–I3 safety critical” text cannot automatically apply to new active support stabilization. Keep local stabilization independent of OCC/FUXA/network availability. |
| FMEA and standards | `lib/templates/system-fmea.toml`; `component-assurance.toml`; `subsystem-qualification.json`; `engineering/assurance/subsystem-control-register.json`; `docs/certification/` | Add magnetic lift loss/overforce, pull-in/contact, sensor bias/common cause, ferrite fracture/demagnetization, guidebeam deviation, protection power, regenerative limits, field exposure/EMC, emergency evacuation and recovery. Applicability must be reallocated for maglev; do not inherit steel-wheel requirements or presume they disappear without substitutes. |
| Formal assurance | `engineering/assurance/formal/tla/`; `topology-adapters.md`; `docs/safety-case/`; `crates/osr-safety-case` | Extend bounded control and interlocking properties for static support, actuator limits, fault shutdown and no-mainline-switch topology. Formal state-machine proof does not establish real force/stability margins; existing open obligations remain open. |
| Design closure and orchestration | `engineering/assembly_design/data/closure-plan.json`; `closure-evidence.json`; `closure-trust.json`; `equipment-layout.json`; `engineering/continuous_design/` | New source-bound variant tasks and evidence records; preserve existing traditional-rail evidence history. Do not mark existing tasks passed by substitution. Native structural pipeline and new electromagnetic capability need independent qualified benchmarks. |
| Cost and finance | `lib/templates/capex-costs.toml`; `civil-cost-calibration.toml`; `design/city-generation/src/osr_scenario/capital.py`; `iraq_finance.py`; `tools/automation/generate-cost-model.py`; `generate-civil-cost-model.py` | Add explicit low/base/high raw input cost basis and priced MBOM/BoQ. Regenerate all derivative city/factory/funding results. Keep recurring unit cost separate from NRE, prototype, test line, qualification and launch tooling. |
| City/service/depot integration | `lib/templates/fleet-sizing.toml`; `city-operating-scope.toml`; `switches.toml`; `depots.toml`; `corridor-resilience.toml`; `.../osr_mech/depot_dispatch.py`; `recovery_interface.py`; `maintenance_interface.py`; `design/city-generation/src/osr_scenario/` | Explicit no-mainline-switch operating model, turnback method, failure blocking/recovery time, evacuation, depot switches and service reduction scenarios. Rerun capacity, fleet, reserve, storage/workshop bays, charging and accessibility. |
| ERP/lifecycle | `deployment/erpnext/apps/osr_erpnext/`; `services/integration/osr_integration/manufacturing.py`; `engineering.py`; `store.py` | New Item/BOM revisions, manufacturing routings, installed serials, supplier evidence, inspections and maintenance tasks. ERP README requires released priced family MBOM with actual company/warehouse/operator/supplier inputs before production import; an engineering study is not a submitted production BOM. |
| Supervision/FUXA | `deployment/supervision/config/generic.json`; `services/integration/osr_integration/fuxa.py`; `embedded.py`; `crates/osr-supervision-contract` | New sensor tags, units/ranges, timestamps, alarms and physical bindings for gap/current/temperature/force reserve. FUXA displays equipment; it must not close the stabilization loop or grant movement authority. New bindings require controlled commissioning. |
| IFC/Bonsai integration | `engineering/interchange/`; `engineering/models/digital-twins/`; `.../osr_mech/freecad_product_library.py`; `neutral_manufacturing_exports.py` | Preserve stable component/assembly identity, IFC GlobalIds, source hashes and revised placement/clearance/maintenance envelopes across FreeCAD, IFC4.3/Bonsai, commercial quantities and operations. |

### 4. Rework/validation sequencing

1. Freeze variant architecture and quantitative acceptance criteria; keep wheel-rail baseline pinned. Record assumption vs calculation vs vendor data for every mass, force and price.
2. Establish magnetic coupon force/gap/temperature measurements and independently checked field model; add six-degree-of-freedom force/stiffness maps and passive/active stability proof. The Halbach-array mass alone cannot establish hover capability.
3. Create body/guidebeam/array CAD, mechanical retention, finite element loads, vehicle mass closure, guideway tolerance budget, thermal limits and fail-safe stop/recovery concepts.
4. Integrate physics, energy, protection/controller and route/fleet simulations with adverse cases; verify conservation, stiffness signs, saturation, current/thermal limits, sensing failure and structural motion.
5. Derive priced MBOM/BoQ and manufacturing sequence, then recalculate train, viaduct, station, depot, charger, tooling, programme and operating costs at matched transport capacity.
6. Release source-bound engineering study with open gates and explicit test programme; physical supplier/first-article/target-hardware/route trials and independent acceptance remain separate.

Existing deterministic checks can be reused where applicable: `./osr validate run --profile quick`; native toolchain acceptance `./osr validate run --profile native-design`; `cargo test --workspace`; `tools/automation/design-benchmark.py`; `tools/automation/osr-python tools/automation/civil-study.py`; `tools/automation/osr-python tools/automation/design-assemblies.py qualify`. These are commands discovered in current documentation, **not checks executed during this task**. Existing `design-continuous.py verify` checks source-bound evidence without rerunning physics (`physics_rerun:false`).

Current assurance documentation states item-specific G1–G4 remain open and no components have received operational authorization merely from repository checks (`docs/certification/README.md` lines 31–45 and 151–160). New maglev design, controller and structural evidence must be configuration-specific; no existing wheel-rail gate automatically transfers.



# Handoff acceptance and remaining decisions

The prepared files contain a specification and numerical study, not repository implementation. No OpenSourceRail code, generated city result, physical qualification gate or remote branch was changed. Baseline source was read at the pinned commit. Calculation checks establish arithmetic consistency; cost allowances, magnetic field performance, rail tolerances and structural design require the evidence described above.

Prioritise these linked decisions: (1) select a curve-compatible zero-speed magnetic circuit; (2) prove complete force, thermal and fault envelopes with the total magnet/core/coil budget; (3) qualify the narrow beam, rail interfaces and evacuation structure; (4) close the mass and hot-duty charging budget; (5) obtain priced manufactured modules/rail and compare at matched capacity; (6) release the new source-model branch and staged demonstrator programme.

The goal is a locally manufacturable railway with controlled running-gear interfaces and reduced wheel/gear/bearing maintenance. Track achieved capital cost, energy use, repair time, replacement cost, supply alternatives and operational availability separately. Industrial independence and construction savings are both useful outcomes, but one is not evidence of the other.
