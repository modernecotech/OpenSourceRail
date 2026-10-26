# v0.6 native physical follow-up

OpenSourceRail pursues simple, locally repairable transport with passive wheel bogies and station-powered propulsion. This bounded campaign tests the current six-car comfort reference; it retains failed and numerically invalid results. **No physical train journey, manufacturing release or operating acceptance is established.** The [current design](../current/README.md) remains the reference geometry.

## What was executed

| Work | Result | Interpretation |
|---|---|---|
| Station motor | 17 current-excited GetDP cases plus one full 12.5 m primary / 9 m secondary | Real winding geometry; finite 2D height assumption and linear steel remain limitations |
| Full motor | 7.174 kN/car versus 11.103 kN required | Force reserve -3.929 kN; tested geometry fails |
| Numerical controls | Zero-current, phase reversal, current-squared and energy balance | Successful method checks do not qualify the motor |
| Peak steel field | 2.240 T versus the declared 1.3 T linear-domain limit | Out of model domain; nonlinear material and further convergence required |
| Braking | 24 actual Chrono executions at 10 ms and 5 ms | Six rigid bodies with pure rolling analytically reduced; no real wheel slide or WSP plant |
| Body | Member connectivity, native beam/solid fixtures and counted floor fit-up | Invalid interfaces remain rejected; no whole-body structural release |

## Corrected rolling energy and launch requirement

Counted wheels, axles and brake discs add **1770.387 kg/car of equivalent rotational inertia**. This changes acceleration, coast and braking energy; it adds no static axle weight. The 2 km normal-load reference is now **147.362 s**, with **8.952 kWh/train** launch work. These are requirements under declared resistance assumptions, not demonstrated trips.

## Station LIM: failed geometry, useful next experiment

The full test uses 140 A peak, 50 Hz, 20 m/s and 15 mm gaps at the 80°C conductor hypothesis. It calculates 143.5 kW mechanical output, 52.1 kW secondary heat and 43.6 kW primary copper heat per engaged module. Energy closes in the solver, but steel saturation, finite-height return currents, moving entry/exit, boundary/mesh convergence and repeated thermal duty remain unresolved. Installed available thrust stays **unknown**.

Bare primary copper and steel are **228.186 kg/m**, or **205.4 t per 900 m directional winding**. This excludes supports, insulation, cooling, converters, cables and installation. Station-only propulsion must earn its whole-system cost advantage.

All-series winding voltage exceeds a 750 V DC inverter bound. Ten parallel paths would meet only the equal-flux arithmetic voltage bound at about 990 A RMS per phase. Finite overlap creates unequal coil flux; actual branch voltage, current sharing, converters, cable mass and cooling remain unknown. Reconnection does not repair the force deficit or steel-field failure.

Short-primary force changes 0.91% on the last refinement, while the peak field changes 26.5%. Doubling primary length changes thrust per metre by 80.0%; length extrapolation is therefore not usable as an accepted force map. The tested primary fails; this is not a proof that every LIM design fails.

Next compare a larger magnetic cross-section, different slot/turn/connection designs and reduced air-gap only where the real suspension/rail clearance budget permits it. Use nonlinear steel data, independent finite-height confirmation and measured thrust/temperature before selecting a replacement. Lower speed or sparse boosters are explicit service alternatives, with complete journey and cost consequences.

## Independent braking and authority

The current brake model uses eight counted discs/car, opposed 100 mm piston hypotheses, 0.6 MPa pressure, pad friction 0.35, one-second response and a 0.4-second pressure-rise constant. These are research inputs, not supplier-qualified brake hardware. An ideal instantaneous adhesion limiter preserves rolling; actual slip/WSP latency and fade remain unknown. Receiving propulsion, aerodynamic drag and rolling resistance receive no emergency braking credit.

| Normally loaded train, initial 20 m/s | Stop distance | Lumped disc temperature |
|---|---|---|
| dry | 329.6 m | 66.3°C hypothesis |
| wet-downhill | 719.0 m | 77.0°C hypothesis |
| one-channel-lost | 1399.4 m | 124.2°C hypothesis |
| insufficient-adhesion | Cannot stop | 51.7°C hypothesis |

Wet/downhill means adhesion 0.05 on a 2% downgrade. The failed-channel case retains four working discs/car and heat capacity from those discs alone. At adhesion 0.03 on a 4% downgrade, gravity prevents stopping in this model. The crowd-load failed-channel run needs over 3 km. Halving the timestep changes stopped-case positions by about 0.05 m; energy balances use trapezoidal velocity work and record the native position integration bias separately.

A nominal receiving zone is not an independent stopping envelope. Dispatch needs qualified brake curves, earlier fault detection, protected overrun distance or lower route speed, plus recovery and evacuation. A seating/admission policy does not remove crowd and degraded-brake checks. The [HydroAct brochure](https://rail.knorr-bremse.com/media/2000_products/2900d_product_broschures/p-1236_hydroact.pdf) is an RFQ comparator; it does not qualify the model actuator, pressure system, disc or fade curve.

## Body connections and numerical validity

The retained upper frame lacks positive-volume connections to the lower chassis. Twenty post-base feet/risers add 66.143 kg of material. Connecting the upper frame requires real floor penetrations, not overlapping stock. The new fit-up subtracts actual skin/core/bond cutouts and counts 72 collar pieces, omitting eight door-adjacent flanges.

The resulting proposal adds **77.154 kg/car**, before unknown weld/fastener/seal hardware. Native FreeCAD checks changed stock volumes, reopen and STEP export. The checked subset has **0 positive-volume clashes**; full-car installation, floor-cap strength, joints, fire, fatigue and repair access remain open. The proposed connection is not silently added to the selected vehicle. Frame calculations include 66.143 kg of post connectors; the separate floor-fit alternative adds a further 11.011 kg. They are not one composed installed vehicle or a qualified common structural model.

The earlier B32R offset-joint run returned a successful process code but failed force balance and refinement. An independent two-beam fixture exposed the unsupported native rotational interface. Those results are **numerically invalid**, not evidence that the complete car passes or fails. [CalculiX documentation](https://www.dhondt.de/ccx_2.23.pdf) constrains rotational equations on expanded beams; algebraic rigid-motion checks alone were insufficient.

The corrected replacement meshes actual hollow walls with full-integration C3D20 solids and translational equations only at contact, load and support planes. A reduced-integration solid trial also showed an unphysical local mode in thin connector feet despite balanced reactions. It is rejected. The final full-integration model records separate slender-cantilever, load/reaction and mesh-refinement checks; the beam-only and reduced-integration failures remain independently identified. **The frame-only stiffness screen still fails:** connecting the upper frame improves deflection, but cannot establish adequate stiffness by itself. Actual joins, composite-panel shear contribution, local stress, buckling, fatigue and flexible-body modes remain unqualified. Detailed case values and model domains are retained in the summary.

| Full-integration frame-only case | Maximum vertical displacement | Screen versus 25.6 mm |
|---|---|---|
| retained-frame-contact-only / normal-fine | 150.51 mm | fail |
| counted-post-base-connections / normal-fine | 111.59 mm | fail |
| counted-post-base-connections / empty | 86.89 mm | fail |
| counted-post-base-connections / crowd | 169.92 mm | fail |
| counted-post-base-connections / asymmetric-braking | 114.97 mm | fail |

Deeper side-sill alternatives are counted in the summary as next experiments. They add material and change underside clearance; none has a passed structural/swept-clearance screen or is adopted. A participating composite shell is another explicit stiffness alternative requiring its own load-transfer model.

## Evidence, storage and reproduction

[Machine-readable summary](summary.json) · [Source and payload manifest](manifest.json) · [Motor inputs/logs/scalars](motor-short.tar.gz) · [Full motor inputs/logs/scalars](motor-full.tar.gz) · [Braking 10 ms](brakes-10ms.tar.gz) · [Braking 5 ms](brakes-5ms.tar.gz) · [Invalid native frame](frame-invalid.tar.gz) · [Explicit-solid frame](frame-solid.tar.gz) · [Floor fit-up CAD](floor-fit.tar.gz)

Motor and frame compact archives retain the complete original SHA-256 index, exact model inputs, logs and scalar outputs. Bulky mesh/field files remain in ignored local run directories; remote artifact storage is not configured. A compact archive can verify its retained bytes but cannot replace full raw native verification. Reproduction commands and exact tools are in the retained inputs/logs and source below. No raw evidence was rewritten to make a screen pass.

```bash
.venv/bin/python -m engineering.station_rail.closure_round --verify
# Reproduce native workers into fresh directories, then publish:
# station_motor.run(...), long_motor.run(...), braking.native_run(...),
# body_solid_frame.run(...), body_floor_fit.run(...)
# Chrono workers require build/trip-dynamics/environment/chrono/bin/python
.venv/bin/python -m engineering.station_rail.closure_round --publish
```

All 266 city maps/geographies are preserved. City performance regeneration, equal-service economics and the physically coupled launch–coast–arrival demonstration remain held. v0.5 evidence and v0.6.0 tag remain unchanged.
