# Powered-bogie research car: physical quotation handoff

This [machine-readable package](plan.json) is a **separate research child** of
the selected six-car passive-wheel reference. It does not change the selected
physical candidate, evaluation or selection, and it does not qualify a train
for prototype manufacture or passenger operation. Source hashes, child
physical identity and evaluation identity are in the JSON receipt.
The [powered-bogie electrical screen](../v07-powered-bogie/screen.json) has a
different research configuration identity and only calculated demand. A
coordinator must link its source and re-evaluate at this vehicle's mass before
claiming one integrated candidate or service result.

## One mechanically mated option

The option retains each 17 m car's 1,435 mm gauge, four axle positions
(−7.45, −5.35, +5.35, +7.45 m), two bogies at ±6.4 m, 44 fixed seats, two
wheelchair places and two +y door openings. It proposes one motor/gear
cartridge per axle: **24 driven axles in six cars**. Each car collects 1.5 kV
DC from a protected rigid overhead conductor through one roof collector.
The existing 82.8 kWh/car service battery remains service-only. No traction
battery or supercapacitor is counted in this option. The central passive
aluminium LIM fin and station primary are retired **only in the research
child**; their complete installed cost and mass have not been credited.

The car frame has x forward, y left and z above the rail running surface.
Motor cartridges have proposed 0.64 × 0.52 × 0.52 m boxes centred on each
existing axle at z=0.52 m. A proposed 50 mm three-axis swept reservation
leaves 52 mm nominal lateral clearance to the inner faces of the retained
brake discs and 106 mm to the floor underside. The motor's lowest swept
point after nominal wheel wear is 170 mm above rail. These are **necessary
geometry screens**, not measured bogie yaw, suspension travel, gear bore,
curve, turnout or tool access. The research child keeps the existing service
battery fit conflict open.

One independent rail-contact brake module per bogie carries two nominal 1 m
shoes, one on each rail. The [Knorr-Bremse MagnetAct catalogue](https://rail.knorr-bremse.com/media/2000-products/product-broschures/p-1269-magnetact.pdf)
gives a possible rigid-shoe packaging reference: 106 × 115 × 1000 mm,
75 kg/m and 72 kN/m **magnetic attractive** force. Twenty-four shoes would
be 1.8 t bare for a six-car train before actuators, mounts, cables and
protection. The catalogue's attractive force does **not** establish
longitudinal braking force on the proposed rail, its temperature duty or
compatibility with crossings. No vendor is selected. An electromagnetic
rail-contact brake also needs a protected excitation and actuator supply
during overhead-line loss. Coil power, stored fault energy, drop/stow
behaviour and independent fail-safe parking are unsized. The existing
service battery is not credited as a certified brake source.

With the high conditional normal-load budget and a 2% downgrade, an
independent stop at 0.6 m/s² with all wheel brakes unavailable requires
119.6 kN rail-direction force over the train. If one of twelve modules is
unavailable, each other module must deliver at least 10.9 kN, dissipate up
to 217 kW initially at 20 m/s, and absorb approximately 3.62 MJ over the
ideal 333 m deceleration distance. Reaction, build-up, uncertainty and
berthing margins are additional. The inherited μ=0.05 wheel-adhesion
hypothesis cannot be used to claim this independent stop.

## Mass and manufacture boundary

The seven proposed equipment groups have a **quotation allocation** of
1.345–2.670 t/car, including four motor/gear cartridges, two inverter and
cooling racks, one roof collector, HV protection, two complete bogie brake
modules, flexible cables/hoses and mounts. Retiring only the 275 kg/car of
counted passive secondary stock gives conditional *account arithmetic* of
20.292–21.617 t/car tare. This is not installed mass. The selected
10.090 t/car residual account, cable and mount locations, service-pack
overlap, supplier weights and physical CG are still unresolved. The
point-allocation CG range in the JSON excludes those quantities; the
whole-car CG and axle reactions remain `null`.

The [receipt](plan.json) counts proposed axle couplings, torque arms,
compliant mounts, bolts, brake slides/stops/pins, flexible HV and earth
loops, cooling supply/return hoses, and roof mounts for **one car**. Gearbox,
motor and axle bearing counts remain a named supplier question rather than
zero. It includes assembly order, lifting and isolation requirements,
downward brake-shoe removal over a pit, motor cartridge removal between
the existing discs, QA hold points and a repair record path. These are
quotation interfaces; fastening class, clearances, hours and tooling are
not yet approved.

Six collectors avoid inter-car traction HV jumpers but require an OLE
section-gap, arcing, wear, fault isolation and bridge/station clearance
study. A three-collector/two-car-pair alternative could reduce collectors
but adds HV jumpers, coupler service and fire/earthing interfaces; neither
has a priced installed comparison. Before selecting a prototype car, obtain
motor and brake supplier drawings, actual rail samples, measured dynamic
travel, collector/OLE site envelope, a car weighing and independent hot
and faulted stops.

Reproduce in a source-complete checkout:

```bash
python3 -m engineering.vehicle_parts.powered_bogie_prototype build --output /tmp/fresh-powered-car.json
python3 -m engineering.vehicle_parts.powered_bogie_prototype check --output docs/design-engine/v07-powered-vehicle/plan.json
python3 -m pytest -q engineering/vehicle_parts/tests/test_powered_bogie_prototype.py
```
