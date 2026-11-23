# Airport service, train motion and traction supply

The 12 km Airport study uses six stops and double track. At a 15-minute interval it books 144 passenger trips in 18 hours, two empty positioning trips and six depot moves. The 20-minute study books 108 passenger trips and uses a 600-second phase at Al Qadisiya. That phase removes the terminal conflicts in the source-derived 117-second plan. The separate 30-minute study books 72 passenger trips.

The standalone benchmark holds the six-car formation at 149.05 t tare and 201.55 t loaded with 700 places. It starts at 06:00, books 35-second intermediate dwells and applies the same generated directional OD demand to both power layouts. Demand concentrates in commute hours. The nominal alignment is level. Research runs apply a constant 2% grade, 15% additional OD demand and a 120-second delay to the first Airport departure. The delay, grade and OD inputs can be replaced with a scenario supplied by the integrated evaluator. The benchmark results use generated demand and a planning mass basis.

| Normal service | Passenger trips completed | Places/hour/direction | Final unserved demand under generated OD |
|---|---:|---:|---:|
| 15 min | 144 / 144 | 2,800 | 0 |
| 20 min, retimed | 108 / 108 | 2,100 | 0 |
| 30 min | 72 / 72 | 1,400 | About 8,076 |

The generated benchmark takes arrivals from booked call times. Supplied hourly OD takes arrivals at actual boarding calls and conserves the full local day. The ledger separates riders waiting at their origin after a capacity denial, demand that appears after the last real boarding call, and riders aboard an incomplete trip. Completed passenger journeys plus these categories equal offered journeys. Boarding attempts and final capacity queues remain visible separately.

## Electrical comparison at 15 minutes

| Supply and condition | Passenger trips completed | Lowest live collector voltage | DC source energy |
|---|---:|---:|---:|
| 30-site radial, normal | 144 / 144 | 1,483 V | 21.26 MWh |
| 30-site radial, hot | 144 / 144 | 1,481 V | 21.26 MWh |
| 30-site radial, site out with restored feeds | 144 / 144 | 1,481 V | 21.26 MWh |
| 30-site radial, path isolation | 0 / 144 | 1,484 V | 17.25 MWh |
| 30-site radial, combined adverse case | 0 / 144 | 1,468 V | 18.12 MWh |
| Six-site paired, normal | 144 / 144 | 1,491 V | 21.23 MWh |
| Six-site paired, hot | 144 / 144 | 1,490 V | 21.23 MWh |
| Six-site paired, site out with restored feeds | 144 / 144 | 1,482 V | 21.08 MWh |
| Six-site paired, one path unavailable | 144 / 144 | 1,490 V | 21.24 MWh |
| Six-site paired, combined adverse case | 144 / 144 | 1,457 V | 22.16 MWh |

Each outage uses an explicit site and bay index. Radial isolation holds traffic upstream of the affected interstation block. The recorded collector voltage is for ports that remain live while trains travel or wait. The halted duty has a different amount of transport and energy consumption. The paired case assumes the surviving positive and return path is intact. The restored-feed cases assume isolation and switching are complete at the start of the day. The combined case also reduces source voltage 1%, increases the hot impedance a further 5% and increments driving and auxiliary demand by 5%.

The model solves voltage at each moving collector through source droop, sectional positive and return resistance, track allocation and local sensitivity. It restricts available motoring effort by collector voltage and per-train current, then propagates the delivered effort into the next speed and position. It limits regeneration to local auxiliaries and simultaneous receptive loads. It calculates conductor dissipation from current and impedance separately from source and collector energy. Source and branch current, a branch RMS bound, predicted ride-through and protection holds remain available for equipment enquiries. [Moving-load and regenerative receptivity formulation](https://scholarworks.aub.edu.lb/items/001f9c49-7a43-414d-bb8f-17e74d57ab98)

In the 2% grade research cases, the 15-minute paired layouts complete the passenger diagram with 33 seconds of maximum arrival delay. The six-site arrangement with the central failure reaches 1,449 V. Eight equally spaced sites reach 1,459 V, shifted six-site locations reach 1,457 V, and the six-site conductor with 25% lower resistance reaches 1,455 V. Two additional six-site trials move the outage toward the ends. The paired combined replay at 1 second changes daily DC energy by 0.04%, minimum voltage by about 0.46 V and peak source power by about 0.30 MW against the 2-second result. The peak remains sensitive to the numerical step and service demand.

Comparable planning price scopes in the retained procurement estimate yield approximately $394m–$454m for the radial layout and $132m–$248m for the paired layout. These ranges include the traction line, source groups and utility tie-ins. Firm installed offers, comparable upkeep boundaries, renewals, thermal duty, approved protection and utility capacity are open. Every economic ranking is held. [Procurement estimate](../prototype/sourcing-estimate.json)

## Independent tool executions

SUMO 1.28.0 completes all 146, 110 and 72 passenger-plus-positioning route trips for the three intervals. It uses directed tracks, rail signals, a separate vehicle for each booked trip and a custom Airport train model. Passenger trips use the selected full case mass and positioning trips use tare. The traction table limits wheel force by the required acceleration at that mass and the available nominal wheel power divided by speed. Rolling force follows the same mass and resistance acceleration as the coupled model. Directional node elevations supply the assumed grade. The native model uses a mass factor of 1.0, matching the coupled model's translational mass assumption. It reads back the serialized traction, resistance and mass values in the receipt. [SUMO custom railway dynamics](https://sumo.dlr.de/docs/Simulation/Railways.html) · [Trip records](https://sumo.dlr.de/userdoc/Simulation/Output/TripInfo.html)

Independent SUMO launch controls scale force, mass and nominal wheel power by formation. Floating-car speed readback gives 0.60 m/s² for both three- and six-car trains. Halving the traction table while keeping mass and resistance gives 0.29 m/s². Doubling mass at the original force and resistance gives 0.30 m/s². SUMO covers the booked directional line trips and fixed-mass physics, while the coupled model covers the common terminal, yard, OD-dependent mass and available DC power. A separate three-car, 20-minute test on a 2% grade completed 110 of 110 trips but only 330 of 550 stop calls. SUMO reported 220 skipped downhill stops and 55 emergency-stop warnings. The adapter checks completed stop records and reports skipped stops and emergency braking warnings. Graded native stopping remains open.

Pandapower 3.5.3 solves two synthetic balanced 33 kV layouts at the coincident DC peak for each 15-minute nominal layout. The weakest modeled bus is about 0.992 pu nominal and 0.961 pu in the weak-grid sensitivity. The load allocation uses actual simultaneous DC source loads with illustrative transformer, rectifier efficiency and power factor. Baghdad utility connection locations, short-circuit duty, impedances, voltage, harmonic obligations and protection are open. [Balanced AC power flow](https://pandapower.readthedocs.io/en/latest/powerflow/ac.html)

## Verification and reproduction

[Motion evidence receipt](motion-evidence.json) contains 39 cases, native tool versions and compact outputs, model input digests, evaluation identities and the 1-second check. Verify source and receipt integrity with system Python. To rerun native tools use the project environment with SUMO/netconvert and pandapower. The rerun also writes full-resolution train and per-site CSV traces and SUMO input, trip and stop XML when a trace directory is supplied.

```bash
python3 -m cities.Baghdad.engineering.simulation.motion_evidence
.venv/bin/python -m cities.Baghdad.engineering.simulation.motion_evidence --regenerate --trace-dir build/baghdad-motion-evidence
.venv/bin/python -m pytest -q cities/Baghdad/engineering/simulation/test_motion_power.py
```

For an integrated input use `motion_power.evaluate(inputs, output_dir=None)`. Pass the same inputs and evaluation to `motion_evidence.crosscheck(inputs, result, output_dir=None)` for SUMO and pandapower. The 24×6×6 hourly OD matrices use physical station order in both directions and local civil time. The supplied full-train auxiliary load is in kW. Grade is a signed percent in the Airport–Al Qadisiya direction. The service runs on the declared 12 km chainage datum.

The campaign uses a steady resistive DC circuit, fixed mass within each leg, a single selected outage location per replay and a simplified shared terminal. It supports digital comparison. Field route profile, adhesion and brake tests, isolation timing, equipment and conductor heating, smoke and evacuation cases, witness tests and approval remain open.
