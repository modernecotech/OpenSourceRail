# Compact acceleration and alternative launch mechanisms

Reference vehicle `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`; six 17 m cars, 276 normal places, 2 km and 120 s target headway.
Normal accounted mass is 22.672 t/car; complete installed mass remains unknown.

The reference's **825.005 m shared envelope = 496 m outgoing + 329.005 m receiving**, rounded 825 m; catalogue 900 m.
Launch-only hardware is compared separately. Receiving motors are optional; independent qualified brakes remain mandatory.

|Speed km/h|Acceleration m/s²|Constant-a travel m|Time s|Jerk 0.5 travel m|Peak train force kN|Peak train mechanical MW|
|---:|---:|---:|---:|---:|---:|---:|
|43.2|0.4|180.0|30.0|184.8|63.9|0.766|
|57.6|0.4|320.0|40.0|326.4|65.1|1.041|
|72.0|0.4|500.0|50.0|508.0|66.6|1.332|
|43.2|0.6|120.0|20.0|127.2|93.2|1.118|
|57.6|0.6|213.3|26.7|222.9|94.4|1.510|
|72.0|0.6|333.3|33.3|345.3|95.9|1.919|
|43.2|0.8|90.0|15.0|99.6|122.5|1.470|
|57.6|0.8|160.0|20.0|172.8|123.7|1.980|
|72.0|0.8|250.0|25.0|266.0|125.3|2.506|
|43.2|1.0|72.0|12.0|84.0|151.8|1.822|
|57.6|1.0|128.0|16.0|144.0|153.1|2.449|
|72.0|1.0|200.0|20.0|220.0|154.6|3.092|
|43.2|1.2|60.0|10.0|74.4|181.2|2.174|
|57.6|1.2|106.7|13.3|125.9|182.4|2.918|
|72.0|1.2|166.7|16.7|190.7|183.9|3.679|

At **72 km/h and 1.0 m/s²**, constant-acceleration launch travel falls from 500 m to **200 m**, and launch time from 50 s to **20 s**. Required train force is **154.6 kN** and peak mechanical power **3.092 MW**.
The complete launch-only fin envelope is **296.5 m**. Rotary options need at least **14 × 250 kW shaft units** under the declared transmission assumption; this is demand sizing, not a product approval.
Adding the assumed 0.5 m/s³ jerk ramps gives **220.0 m travel and 22.0 s** before engagement margins. Passenger comfort, wheelchair protection and the integrated jerk journey remain unverified.

Higher acceleration shortens the launch but raises force, peak power and passenger-interface demands. Jerk columns are launch bounds, not rerun journeys.
Full-train LIM launch coverage also includes initially occupied fins: travel + 104.5 − 8 m. Outgoing reach alone is not installed winding length.

|Mechanism|Useful quantitative comparison|Missing engineering and cost scope|
|---|---|---|
|Shared LIM|900m retained comparator|Launch/receiving maps, converters, cooling and all installed works|
|Compact launch LIM|Travel+train fin span; higher per-metre cost break-even ratio|Higher thrust/current/heat per metre; independent brake and renewal effects|
|Pinch rollers|Sum of contact normal forces ≥F/μ; rotary shaft power and 250 kW unit counts|Clamp/strip attachments, contact gaps, coupling loads, failed release and tyre wear|
|Winch/capstan|Line tension ≥F, drum torque ≥F×radius; 100/200 m stroke and reset-cycle bounds|Grip/trolley/return path, anchors, rope wear, coupling release and parallel resource count|
|Wheel traction with short feed|Driven weight fraction ≥F/(μmg); two of 12 bogies explicitly screened|New powered bogies/vehicle mass, collectors, live-feed protection, adhesion and recovery|

The 250 kW shaft motor is a sizing hypothesis, not a supplier product selection. Transmission/motor/VFD efficiencies and friction are explicit assumptions in result.json.
No unit prices are invented. Break-even requires `Lcompact*ccompact + extra fixed/braking/lifecycle costs < 900*creference`; all omitted scope remains open.
Two-shift production/construction and two/three-shift operating scenarios are retained; workforce and availability require a delivery model.

Intamin documents a [friction-wheel launch example](https://www.intamin.com/project/quantum-accelerator/); Doppelmayr documents [rope-propelled rail APMs](https://www.doppelmayr.com/en/systems/automated-people-mover/). These establish principles, not this railway's cost, performance or approval.

Every available-force, thermal, wear, braking, coupler, maintenance, accessibility and physical-acceptance gate remains open.
Comparison `94e5b344a2efd6008ee4fae0911e9518cc99c4b9f5d44100a9e10243b0b544c6`.
