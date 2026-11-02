# Conditional repeated-duty thermal sensitivity

This study reconstructs synthetic train-aggregate loss from the retained selected-vehicle P1 journey trace, with its 0–500 m command window and 120 s departure period. It is not a stationary-bank motor model or a result for the selected 900 m winding.

| Case | Peak, continuous cooling | Peak, cooling suppressed for prelaunch |
|---|---|---|
| low | 51.645 °C | 51.823 °C |
| base | 37.248 °C | 37.307 °C |
| high | Held: controller-speed-limit | Held: controller-speed-limit |

The first hypothesis adds the prelaunch energy as an adiabatic impulse and cools continuously for the full departure period. The second suppresses all aggregate cooling during the prelaunch interval within that same period. Both repeat the recorded synthetic loss pulse unchanged with temperature and use exact exponential cooling for piecewise constant power; this is a separate assumption from the journey forward-Euler update.

Incomplete cases are held and are not repeated. These calculations do not establish actual thrust, fixed-bank current or cooling, station occupancy, train-tail clearance, a physical journey or thermal qualification. Overlap, zero cooling and temperature domain limitations are recorded in the complete result. Earlier superseded attempts and failed tests are retained; some early producer bytes were not retained and their outputs are not claimed to be replayable. The original runtime is not independently attested and no filesystem or network sandbox was enforced.
