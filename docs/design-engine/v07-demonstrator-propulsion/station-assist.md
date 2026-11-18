# Station launch with bounded wheel assistance

This research comparison uses the retained six-car passive-wheel vehicle as its parent. It does not change the selected vehicle or Baghdad scheme. The digital route is a 2 km level or 2% uphill leg, with a 72 km/h cap. A station primary supplies traction through the first 500 m of leading-nose travel; onboard wheel traction then supplies the required work until braking. The receiving brake and rescue system remain independent of traction power.

The [machine-readable comparison](station-assist.json) binds the vehicle, demand model, station-module stock and storage assumptions by source and evaluation identity. The 500 m command requires at least **596.5 m of physical station primary** for full six-car fin engagement under the stated layout; the existing station-plus-booster comparison needs **943 m** across both sections. The launch section contains at least 48 addressed module pieces, 94 two-face joints and two bank ends. Its converters, feeders, isolation, cooling and protection still need quantities. These are minimum layout quantities, not a complete installed drive.

| 2 km leg | Station-only | Station + 250 m booster | Station launch + wheel assist |
| --- | --- | --- | --- |
| Level | Analytically reaches in 147.4 s | Analytically reaches in 143.3 s | 2.58 kWh wheel mechanical work; 159 kW peak wheel mechanical power |
| 2% uphill | Stalls before arrival | Analytically reaches in 160.6 s | 11.22 kWh wheel mechanical work; 693 kW peak wheel mechanical power |

On the uphill leg, the 85% assumed drive efficiency and 30 kW train auxiliaries imply about **14.4 kWh** to replenish per leg. A 35-second, 90%-efficient station charge would require about **1.64 MW per train**. A two-leg no-charge reserve at 60% usable fraction implies about **48 kWh nominal battery-only capacity**. With a 500 kW battery output cap, the model allocates about **5.6 kWh per leg** above that limit to a capacitor; at 50% usable fraction, two legs require about **22.4 kWh nominal capacitor capacity**. No module, cooling system, charger or supplier price has been selected.

At the parent vehicle mass, the uphill wheel-assist peak force needs an optimistic uniform-load adhesion coefficient of 0.078 with 8 driven axles, 0.052 with 12, 0.039 with 16, or 0.026 with 24. Applying the inherited 0.05 coefficient purely as a comparison gives a mathematical minimum of 13 driven axles. That coefficient is not a measured traction limit. The packet also recomputes wheel work and power for two added-equipment mass sensitivities; it does not treat the uninstalled drive as massless.

Procurement still needs a measured station force map and phase/current limits, motor and inverter torque/thermal maps, a battery/capacitor and charger specification, full installed mass and price, adhesion evidence, repeated 120-second duty, independent stopping, parking and protected rescue. The current output is an analytical research screen for choosing what to size next, not a manufacturing or operating release.

Regenerate with `python3 -m engineering.design_search.station_assist_screen`; check with the same command and `--check`.
