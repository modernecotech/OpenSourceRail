# Station regenerative capture, mechanical launch and compact booster: design plan

**Status:** proposed architecture family and implementation plan; no selected or safety-qualified design.  
**Prepared:** 2026-11-05.  
**Purpose:** investigate a station-mounted mechanism that recovers some approach energy from a passive train, stores it between arrival and departure, launches the train *forward*, and uses the minimum economically justified wayside propulsion farther along the departure path.

## 1. The passenger outcome, not a fixed motor, is the requirement

Start with passenger demand, station spacing, journey time, dwell, wait, accessibility, operating hours and reliability. Treat vehicle mass, target speed, acceleration, jerk, launch hardware, recovery system, headway and energy supply as design variables. Compare candidates at the **same passenger-service requirement and scope**. A two-minute departure interval, a particular 72 km/h top speed, a 200 m booster, and the inherited 900 m shared LIM-winding allowance are **not mandates**.

The active [propulsion policy](../../../engineering/development_baseline/propulsion_policy.py), migrated in [commit 211925cf](https://github.com/modernecotech/OpenSourceRail/commit/211925cf37136b401394c76a66d313f1a4804a2d), selects no installed architecture, powered length, acceleration, braking or headway. **Do not use 900 m as a default or price this concept by scaling that former allowance.** Neither the five 20 m LIM-bank experiment nor a 200 m booster is an approved replacement.

**The train does not have to reach 72 km/h.** Target speed is a design variable, including different limits between station pairs. At the same ideal acceleration, 60 km/h requires 30.6% less kinetic energy and acceleration distance than 72 km/h; 50 km/h requires 51.8% less. These are kinematic comparisons, not net electricity savings. The selected service must also account for journey time, waiting, fleet requirement, dwell, stopping and reliability. The first executable screen includes 40, 50, 60 and 72 km/h cases without selecting a preferred speed. A whole-route service and lifecycle calculation must decide which speeds are worthwhile.

The optimistic outline can be accepted as an **outline** with calculated costs and recorded assumptions, even if suppliers, detailed CAD or physical data are unavailable. Missing credible evidence for launch force, controlled coupling, independent stopping, thermal performance or passenger protection must still prevent an engineering, prototype or operating release.

## 2. Important physics: a simple spring does not propel a through train forward

A spring compressed directly by a train moving towards a through-station would push the train back towards its approach. Continuing in the same direction requires a **controlled energy-transfer and direction-routing device**: for example, rollers and a one-way or reversible transmission driving a flywheel; a hydraulic pump/accumulator and motor driving a forward launch device; or a translating capture carriage with a separately controlled release path. A static end-of-track buffer is not an appropriate normal-service capture device.

A mechanical contact made only during the final small amount of braking can recover only the kinetic energy still present then. Capturing braking energy earlier requires controlled contact over an approach distance, such as trackside drive rollers acting on a passive engagement strip, a guided catch carriage/cable, or an electrical regenerative wayside machine. There is no energy creation when a spring is released: the recoverable launch work cannot exceed captured train energy after all coupling, conversion, standing and release losses.

**Illustrative, unqualified sizing** at an assumed **160,000 kg train mass** (the inherited mass accounts do not establish final installed mass). The distance column uses *constant net deceleration of 0.8 m/s²*; it is not the stroke required by a particular spring.

| Capture from speed | Kinetic energy | Constant-force capture distance at 0.8 m/s² | Share of kinetic energy at 20 m/s |
|---|---:|---:|---:|
| 2 m/s | 0.32 MJ | 2.50 m | 1% |
| 5 m/s | 2.00 MJ | 15.625 m | 6.25% |
| 10 m/s | 8.00 MJ | 62.50 m | 25% |
| 20 m/s | 32.00 MJ | 250.00 m | 100% |

At a peak **rather than average** deceleration limit of 0.8 m/s², an *unpreloaded linear spring* exerting zero-to-peak force would require at least **twice** the listed stroke to recover the same energy. Real engagements require jerk shaping, resistance, available stroke and failed-capture margins.

If a 5 m/s capture stores 2 MJ and the **assumed complete capture-to-relaunch round-trip efficiency is 70%**, the train receives 1.4 MJ: **4.18 m/s equivalent departure speed**, assuming no other losses. A 200 m booster from 4.18 to 20 m/s would need, before resistance, approximately **0.956 m/s²**, **153 kN**, **3.06 MW peak mechanical power**, and **16.5 s** in that powered region. Its installed hardware length additionally depends on how the train's multiple passive engagement elements overlap each motor bank.

**Ambiguity to resolve in a user brief:** “a booster 200 m from the station” (its *location*) is not the same as “a 200 m booster” (its *powered length*). At 5 m/s, traversing an unpowered 200 m after the platform takes about **40 seconds** before any further acceleration; this may make the timetable unacceptable. Position and length must be separately optimised.

Basic equations to encode with units and tests:

- `E_kinetic = 0.5 * m_effective * v^2`, with rotating-equivalent inertia added once and any gradient/work losses separately.
- `E_delivered <= E_captured * eta_capture * eta_store * eta_release`; storage state and energy transfers shall balance at each step.
- `s = (v_out^2 - v_in^2) / (2 * a_net)` only for a constant-acceleration first screen; apply jerk-limited time histories before selecting hardware.
- `F_net = m_effective * a`, `F_drive = F_net + resistance + grade_force`; `P_drive = F_drive * v / eta_drive` (define whether each result is mechanical or electrical).
- For real springs, evaluate `E = integral F(x) dx`, peak force, pre-load, fatigue, temperature and uncontrolled release; do not substitute average force for peak force.
- For hydraulic accumulators, derive usable work from the pressure/volume curve with pre-charge and thermal behavior; `p * delta_V` is only a rough bound for constant pressure.

## 3. Breadth-first candidate matrix

These are **competing hypotheses**, not successive features required on one design. Include no-regeneration benchmarks and reject redundant combinations before expensive analysis.

| Candidate | Energy capture | Station energy store | Controlled forward departure | Remaining drive | Key uncertainty |
|---|---|---|---|---|---|
| A. Spring contact and transfer | Compliant collector over last low-speed approach | Mechanical spring bank | Separate ratchet/transmission-driven trolley or rollers | Compact LIM or rollers | Stroke, shock, energy direction, release fault |
| B. Hydraulic-regenerative rollers | Rollers engage passive strip on approach | Gas-charged hydraulic accumulator | Reversible hydraulic motor driving rollers or trolley | LIM or roller bank | Grip, hydraulic efficiency, seals, noise, oil temperature |
| C. Flywheel-regenerative rollers | Rollers engage passive strip on approach | Contained flywheel | Clutched forward roller drive or catch carriage | LIM or rollers | Slip, transmission losses, containment, faulted clutch |
| D. Regenerative electromagnetic wayside | Reversible LIM or other generator interacting with passive element | Station flywheel/supercapacitor | Compact electromagnetic drive | Multiple shorter banks if needed | Air-gap, force map, power electronics, cooling |
| E. Capture-carriage cable | Mechanical carriage/cable couples during controlled braking | Accumulator or flywheel | Mechanically powered launch carriage | Optional compact booster | Safe capture/release, rope fatigue, reset time |
| F. No-capture comparator | Independent friction braking | None | Compact standalone rollers, cable or LIM | Candidate-specific | Required purchased energy and full installed cost |

For each: also explore **no booster** if mechanically achievable, **booster at station exit**, and **booster some distance downstream** as distinct combinations. Retain onboard traction as an equal-service architecture comparator, without implying onboard motors are required.

**Possible component creativity:** retracting sprung guide rollers, elastomer/composite engagement strips, distributed low-force contact banks, guided catch trolleys, overrunning clutches, hydro-pneumatic accumulators, serial or parallel springs, differential gears, flywheel shaft power buffers, replaceable clip-in mechanical cartridges and fail-open engagement jaws. These ideas need proof of forces, passenger jerk, wear and failure behavior; a creative shape is not a safety result.

## 4. Internet precedents and what they actually establish

| Primary source or research | What is demonstrated or described | Permitted inference / explicit limitation |
|---|---|---|
| [Turner Engineering / Vycon–LA Metro wayside flywheel project](https://turner-engineering.com/projects/la-metro-subway-energy-storage/) | Stationary flywheel recovering electrical braking energy in rail service | **Direct storage precedent**, not direct mechanical contact with an unpowered OSR train |
| [Stornetic EnWheel manufacturer](https://www.stornetic.com/) | High-cycle, high-power flywheel modules and modular power storage | Supplier technology lead; performance, pricing and sizing need an OSR duty enquiry |
| [University of Twente, station-level recovery research (2022)](https://research.utwente.nl/en/publications/recuperation-of-railcar-braking-energy-using-energy-storage-at-st/) | Railway-station power profiles and flywheel/ideal storage simulations for regenerative braking | Demonstrates a modelling method; **not** validation of mechanical capture or proof that every OSR braking event is recoverable |
| [Liu, Jiang & Li, Energy 187 (2019), hydraulic rail hybrid study](https://doi.org/10.1016/j.energy.2019.115957) | Rail-vehicle electric/hydrostatic concept with pumps, valves, accumulators and laboratory energy-recovery investigation | Adjacent hydraulics precedent; on-vehicle and downhill research, **not** an approved station mechanism |
| [Bosch Rexroth accumulator concept](https://www.boschrexroth.com/ics/Projects/GenericSelector/?ProductArea=HAD&c=tr&language=en) | Gas-precharged accumulator storage, vibration and shock-absorption applications | Component design starting point; no suitable railway package or pressure vessel established |
| [Intamin friction-wheel launch](https://www.intamin.com/project/quantum-accelerator/) | Powered friction-wheel launch in an amusement ride | Shows a contact mechanism class, **not** heavy rail repeated-load, safe separation or passenger comfort equivalence |
| [Bane NOR buffer-stop technical specification](https://tekniskregelverk.banenor.no/tekniske-spesifikasjoner/overbygning/buffer-stops/) | Impact-energy absorption, passenger deceleration, coupling and track-interface criteria | **Safety comparator only**: buffer stops intentionally dissipate energy and are not routine reversible launchers |
| [Rail longitudinal coupler-force research](https://link.springer.com/article/10.1007/s40534-021-00239-w) | Coupling force and jerk consequences in multi-unit trains | Requires whole-train multibody dynamics before assessing collector loads |

Tools to evaluate these hypotheses: [OpenModelica](https://openmodelica.org/) and [OpenHydraulics](https://git.openmodelica.org/Documentation/) for 1D power/accumulator/spring duty; [Project Chrono](https://www.projectchrono.org/) for coupling, multi-body contact and jerk; [FreeCAD](https://www.freecad.org/) plus [CalculiX](https://www.calculix.de/) for geometry and structural loads. Reuse the repository's Rust/Python design-search, CAD and reporting interfaces rather than inventing a separate dashboard.

These links are **concept/evidence sources, not reproduction licences**. Reverse Engineer Anything may inspect lawfully accessible documentation and authorised exemplar hardware; it must record licences, provenance and uncertain inferred dimensions without copying restricted drawings or implying supplier endorsement.

## 5. Integration into OpenSourceRail

The plan should be executed as a **new approach adapter** in the existing breadth-first design loop, not as a replacement assumption hard-coded into `engineering/development-baseline.toml`.

1. **Requirement and candidate declaration.** Register `station-regenerative-mechanical-launch` as an approach in [`engineering/outline/transport-goal.toml`](../../../engineering/outline/transport-goal.toml), initially `requires-approach-specific-adapter`, with this plan as its design reference. Keep route length, 120/150/180/200/240/300 s example headways, passenger demand, dwell, 1.0/1.5/2.0 km station spacings, grade and climate as **scenario inputs**, not universal defaults.
2. **Energy and motion model.** Add a deterministic, unit-tested candidate evaluator that accepts effective train mass, approach/capture speeds, engagement mode, force/jerk limits, storage capacity/SOC, efficiency factors, drag, grade, source availability, launch velocity and booster position/length. Its outputs are time history, energy flow, coupling force, motion envelope, headway resource reset and hard/unknown constraints. Prefer a small Rust core after profiling; Python may orchestrate initial generation and differential reference tests.
3. **Morphological enumeration.** Generate feasible combinations of capture, store, forward transfer and booster. Reject physically inconsistent combinations early (e.g. spring pushes backward with no transfer, recovery energy greater than input, insufficient stroke, impossible reset time). Keep physically *unknown* ideas as `outline` with required next analyses. Rank by cost, installation length, risk, maintainability, low local-content burden, energy, service quality and demonstrated evidence—not a single weighted score that hides trade-offs.
4. **Detailed models.** Use OpenModelica for `F(x,t)`, pressure, flywheel speed, round-trip losses and high-cycle thermal effects. Use Project Chrono for moving contact, multi-car coupler and jerk histories; CalculiX for anchor, foundation, carriage, collector and fatigue stresses. For LIM boosters, run the existing force/current/thermal adapter; never infer available force from occupied winding length alone.
5. **Engineering integration.** Bind the chosen revision to vehicle interfaces (passive contact strip, mounting and installed mass), station geometry, civil loads, power electronics or hydraulic enclosures, wiring/piping, access/maintenance, fire, noise, BIM and the same city-level service/delivery model. Compare equal-service end-to-end versions before any baseline promotion.
6. **Parametric costing.** Generate component EBOM/MBOM, source or make/buy, material quantity, yield/scrap, fabrication and installation labour, machinery time, QA, tooling, foundations, replacement cartridges, fluids/seals, energy consumption and lifetime overhaul. Where unknown, use labelled assumptions with low/base/high ranges (for example direct material + labour/process + declared 20% allowance), *never a fabricated supplier quotation*.
7. **Workbench output.** Let an end user enter `recover arrival energy`, choose `mechanical launch optional`, vary maximum waiting time/acceleration, and see concepts side by side: speed trace, powered footprint, capture/reuse energy, installed cost, 30-year lifecycle cost, reset throughput, leading uncertainties and next test. The current v0.6 rail system remains an explicit comparator, not a mandated winner.
8. **Evidence and approval.** Store each prediction with assumed parameters, model version, source URLs, exact candidate ID and validation maturity. A costed outline can be `outline complete`; physical engineering and safety approval remain separately held until proven.

### Minimum machine-readable candidate fields

```toml
[station_regenerative_launch]
stage = "outline"
selected_for_development = false
capture_interface = "roller"             # roller | trolley | sprung_contact | electromagnetic
storage = "hydraulic_accumulator"         # spring_bank | hydraulic_accumulator | flywheel | supercapacitor
forward_release = "reversible_rollers"    # rollers | trolley | electromagnetic
booster = "compact_lim"                    # none | compact_lim | rollers | cable
# All the following are per scenario, not hard-coded to the reference:
# train_effective_mass_kg, capture_entry_speed_m_s, efficiency_capture,
# efficiency_store, efficiency_release, coupling_force_limit_N,
# jerk_limit_m_s3, launch_exit_speed_m_s, booster_start_m,
# booster_active_length_m, max_headway_s, storage_reset_time_s,
# measured_source_id, qualification_state
```

This schema is an **interface proposal**, not an executable configuration or a replacement for existing selected vehicle IDs. Use one shared quantity/units library and reject untagged power or energy values.

## 6. Safety and operational non-negotiables

- **Independently safe stopping** must remain available on every train, including when coupling fails, a store is empty, supply is lost or a booster trips; brake operation must never rely on the capture mechanism.
- **No uncontrolled launch:** the stored-energy state shall remain latched/isolated when doors are open, route authority is missing, a platform obstruction is detected, a train is incorrectly positioned or control power is lost. This is a proposed protective requirement, not a certified implementation.
- **Unexpected contact and release:** examine collector misalignment, stuck engagement, partial strip attachment, tyre-slip, broken cable, over-pressure, flywheel failure and unintended backward thrust. Define safe mechanical escape/reset routes and inspection controls.
- **Passenger comfort and couplers:** report peak and RMS acceleration, jerk, longitudinal force through all six cars, wheelchair restraint implications, secondary vibration and repeated fatigue—not only average train acceleration.
- **Platform and civil integration:** compute foundation and anchor reaction, hydraulic/fluid fire risk, guarding, public proximity, maintenance access, acoustic impacts, drainage/contamination and elevated-beam deformation.
- **Service throughput:** model simultaneous arriving/departing trains, two berths if required, energy-sharing between movements, store replenishment, mechanical rearm, degraded dispatch and variable headway. A launcher that cannot reset before the next train is not an acceptable capacity solution.

## 7. Concrete tests and gates

| Work package | First output | Exit criterion for advancing **this candidate** |
|---|---|---|
| P0: cross-reference and reference removal | This document + approach entry; baseline migration already on main | New candidate never inherits fixed powered length, speed or headway; original comparisons retain their own source identities |
| P1: quick Rust/Python mechanics | Reproducible energy/motion simulator; 2/5/10 m/s capture and 100/200/300 m booster cases | Energy conservation and units proven; no unsupported force or energy credited |
| P2: breadth-first comparison | At least A–F and scenarios with variable service | Equal-service comparison with Pareto set, uncertainty and preserved discarded-candidate reasons |
| P3: dynamic feasibility | OpenModelica + Chrono reports for shortlisted concepts | Full-train force/jerk, positive forward release, contact/reset and low/high mass scenarios bounded |
| P4: physical/mechanical CAD | FreeCAD + FEA, station layout and counted part mass | Anchor/structure/guard/maintenance envelopes internally consistent and independently reviewed |
| P5: economics and delivery | 14-scope installed cost, local/China sourcing, 30-year maintenance, station rollout | No missing quantity silently priced as zero; uncertainties and low/base/high remain visible |
| P6: controlled benchtop | Instrumented low-energy collector/store/forward-launch rig, then scaled moving-carriage tests | Measured force, energy, jerk, release and failures match declared tolerances, with safety case for each test |
| P7: selected prototype | Protected representative vehicle/guideway test; independent safety review | No operating or passenger release from simulation or benchtop evidence alone |

Unit/regression cases: zero captured energy; empty/fully charged/overcharged store; `eta` outside 0–1 rejected; spring release direction wrong; blocked collector; train mass sensitivity; 2% uphill; a failed capture that still stops; missing/misaligned strip; a 200 m **offset** versus 200 m **motor length**; storage rearm exceeding headway; and multiple trains sharing one station store. CI should run the inexpensive deterministic screens, with native simulation results versioned as optional evidence.

## 8. Decision and delivery sequence

1. **Now:** publish the concept and mark it `outline`, while explicitly retaining no mandatory 900 m motor and no fixed headway. No physical design is selected.
2. **Next development slice:** implement energy-conserving envelopes and side-by-side comparison with standalone station rollers, compact LIM, capstan and onboard wheel drive; expose the principal result as launch speed, powered metres, peak MW, total USD/km and passenger minutes.
3. **Then:** use a 1D model and a contact-dynamics model to decide whether the sprung catcher, hydraulic roller or flywheel roller actually improves whole-system cost and service over a no-capture equivalent.
4. **Only then:** detailed geometry, parametric manufacturing/BOM, safety FMEA and small-scale proof. Select or reject each branch with its complete evidence and measured costs. At no point should unknown supplier pricing alone block an outline.

**Recommended first experiment:** compare a controlled 5 m/s last-approach capture with a 10 m/s roller-engaged capture, each at 50/70/85% *assumed combined* recovery efficiency, against zero-capture boosters. Sweep 100–300 m booster length, booster placement and passenger demand, then inspect peak force, time to cruise and 30-year cost before choosing a prototype. The present numbers are sensitivity cases, not guaranteed attainable performance.

## 9. Executable first screen

The [Rust kernel](../../../crates/osr-station-energy/README.md) and [Python batch runner](../../../engineering/station_energy/runner.py) implement a bounded, deterministic energy and motion envelope. Run from the repository root using its Python environment:

```sh
python -m engineering.station_energy build
python -m engineering.station_energy examples > build/station-energy-examples.json
python -m engineering.station_energy run --request build/station-energy-examples.json --output build/station-energy-study
python -m engineering.station_energy verify --output build/station-energy-study
```

The explicit example request contains 120 speed/capture/efficiency/booster cases plus three deliberately unsuccessful controls. Its 160 t mass, recovery efficiencies, 200 s headway and resource times are synthetic scenario assumptions. Efficiencies are not attributed to any particular storage technology. Required mechanical power and required source power are separate outputs. Booster active acceleration distance is **not** automatically installed hardware length.

The envelope accounts for initial stored energy, reserve, overflow, losses and delivered energy. It reports necessary-bound failures separately from unknown hardware capacity. The ideal release-speed bound does not establish finite passenger jerk, launch contact forces, actual propulsion capability or independently qualified brakes. Unsupported spring/grade combinations require a better model. Replaying a package does not release a physical design.

P1 has an executable first screen; P2–P7 remain staged work. Mechanism-specific storage, contact dynamics, repeated shared-store scheduling, geometry, manufacturing, installed costs and whole-life service optimisation are still required before this research family can produce a complete priced outline. The three existing priced no-capture station-launch outlines remain separate comparisons.

The first local reference execution completed all 123 cases: 20 violated a declared bound and 103 retained unknown engineering capability. The illustrative 160 t, 5 m/s capture, assumed 70% recovery and 200 m active booster gives:

| Target speed | Required peak mechanical power |
| --- | --- |
| 40 km/h | 0.471 MW |
| 50 km/h | 0.974 MW |
| 60 km/h | 1.735 MW |
| 72 km/h | 3.060 MW |

These calculations use level track, no running resistance and an ideal release-energy bound. Lower power is not sufficient to select a speed: complete journey time, fleet, installed equipment and lifecycle costs must also be compared. The sweep does not choose a preferred speed or storage mechanism.

A separate replay of the existing **no-capture** 30 km corridor, retaining its 45-minute one-way planning limit and reference auxiliary-energy assumptions, cost-admitted 72 km/h cases but not the tested 50 or 60 km/h cases: their screens reported journey-time and auxiliary-energy failures. The 40 km/h cases retained unresolved journey/berth/energy results or other failed bounds. This is a result for that bounded launch-and-coast configuration, not a minimum speed for urban transport. Slower alternatives need joint exploration of propulsion distribution, station spacing, journey requirements, charging and service storage; those inputs must be revised explicitly rather than relaxing an evidenced energy obligation. The stored control is `build/station-energy-integration-20261105/speed-corridor-study`, with a separate source-bound result for each speed.

Local execution identity: `0ca5d644a0a07503264fb470396185446a8b722fc6facad03699c478cea16aee`. Its private `build/station-energy-integration-20261105/energy-study` package binds the exact source, compiler, binary, request and results. A build in a different numerical/tool context has its own evaluation identity. CI uploads its own immutable example execution.

Verification commands: `cargo test --locked -p osr-station-energy --all-targets`, `cargo fmt --package osr-station-energy -- --check`, `cargo clippy --locked -p osr-station-energy --all-targets -- -D warnings`, and `OSR_TEST_STATION_ENERGY=1 python -m pytest -q --import-mode=importlib tests/test_station_energy.py tests/test_outline_approaches.py`. The local checks passed 21 Rust tests and 28 Python tests on each of Python 3.12 and 3.13, including independent arithmetic, energy-origin/reserve accounting, malformed requests and forged-result rejection.

