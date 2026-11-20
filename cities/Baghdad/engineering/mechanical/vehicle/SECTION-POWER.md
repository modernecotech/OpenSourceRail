# Train weight and traction supply for the first Baghdad network

The six-car train weighs **201.092 t** in the crowd-load planning case. Six sets of braced carbody and bogie members account for 31.177 t of cut steel. The finished train tare and crowd payload are open. The supplier return keeps these accounts separate until every group has a scoped weight.

At the published uphill duty the train requests **5.004 MW** of traction converter capacity. Each additional loaded tonne changes this request by 24.9 kW at the same speed, acceleration, grade, efficiency and rating margin. A complete weight return replaces the planning crowd total for this screen.

## Can the supply support coincident trains?

Each trial uses a 1.50 kV open-circuit source and a 1.35 kV planning floor. Dividing the route length by the site allowance gives a representative 4.94 km feed bay. Identical independent circuits feed one common collector bus halfway between the supplies. A coincident pair shares this bus in the electrical model. Actual positions, cross-feeds and section boundaries require a route design.

Each branch has 10 mΩ source droop, 8 mΩ/km outward resistance and 4 mΩ/km return resistance. A 20 s rectangular traction rating pulse repeats at the peak service headway, with 0.300 MW per train of auxiliaries throughout. The single-feed case isolates one source while retaining the other path to the same midpoint.

| Live feeds | Coincident trains | Collector kV | Peak kA/feed | RMS kA/feed | Mean conductor heat kW | Equivalent loop loss kW | Voltage result |
|---:|---:|---:|---:|---:|---:|---:|---|
| 2 | 1 | 1.426 | 1.86 | 0.69 | 27.8 | 37.2 | within voltage screen |
| 2 | 2 | 1.344 | 3.95 | 1.45 | 125.3 | 167.5 | below voltage screen |
| 1 | 1 | 1.344 | 3.95 | 1.45 | 62.6 | 83.8 | below voltage screen |
| 1 | 2 | 1.127 | 9.41 | 3.46 | 354.4 | 474.0 | below voltage screen |

Results below the floor quantify requested duty before converter derating, current limiting or protection operates. The circuit solves the high-voltage constant-power operating point. It retains loss of equilibrium when demand exceeds the transfer limit. Conductor heat covers the outward and return resistances. Equivalent loop loss also includes source droop, whose voltage regulation can have a different physical heat loss. Metal temperature, contact sharing and annual energy require measured duty and thermal impedances.

## Where can braking energy go?

A level stop from the speed cap at 0.60 m/s² takes 33.3 s in the trial. The initial kinetic energy is 11.17 kWh. At 82% wheel-to-bus efficiency, electrical braking offers up to 9.16 kWh, starting at 1.98 MW. The calculation neglects drag, gradients and rotating inertia and holds the rectifier non-reversible.

With only the braking train's 0.300 MW auxiliary load receptive, 2.57 kWh can be used and **6.59 kWh** needs another sink or equivalent mechanical braking, up to 1.68 MW electrical at the start. If an accelerating train draws 5.304 MW on the same ideal bus throughout the stop, up to 9.16 kWh can be used. The ideal-bus figure assumes full availability of those loads. Current limits, feeder separation, overvoltage and train timing can reduce reception. Budget independent stopping at zero network receptivity. No energy credit enters the published cost estimate from this trial.

## What to price

The first network allows 30 supply sites, 114 powered track sections and 296.4 track-km of conductor. Each train has 24 driven axles and 4 shoe sets. Ask the supplier to mark the feed lengths, rectifiers, outfeeds, section breakers and isolators, return bonds, cross-bonds, depot boundary, test points and isolation zones on its single-line drawing. Price installation, enclosures, access, cooling, testing, spares and replacement. Breaker and bond counts follow the approved topology.

The protected conductor has a **$52.29m** first-network present-cost advantage over overhead under the current 30-year assumptions. A one-off **$1.314m direct premium per site** across all 30 sites would consume it after design, test and project allowances, with every other cost fixed. The separate equipment-only threshold is **$0.124m extra per track-km** with line renewal included. These are alternative uses of the same margin. Deduct existing allowances and comparable overhead upgrades before comparing incremental returns.

Return actual hot conductor, return and joint resistances, utility short-circuit levels and rectifier droop/current limits. Supply motoring, auxiliary and regenerative current traces, shoe-current sharing, conductor and cable thermal ratings, rail-to-earth measurements, accessible voltage limits, protection coordination and a witnessed isolation procedure. Replay the working timetable with train positions and measured load curves, including braking into a non-receptive section. Independent braking, touch voltage, faults and thermal qualification remain open.

[Vehicle weight-return instructions](README.md#weighing-the-installed-train) · [Electrical trial inputs](section-trial.toml)
