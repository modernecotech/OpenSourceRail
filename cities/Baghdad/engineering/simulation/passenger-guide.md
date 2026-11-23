# Airport platform movement, doors and summer cooling

A six-car train with 700 passengers needs about **259 kW thermal cooling at 40°C and 343 kW at 48°C** under the stated sun, humidity and door cycle. Full-train electrical demand is about **156 kW at 40°C and 243 kW at 48°C**, including fans, essential control and other train services. The six-car feeder trial allows 300 kW for the electrical interface. With two illustrative 24 kW cooling modules per car before ambient derating, the 48°C case has a **119 kW thermal deficit**. Cooling capacity and full-train electrical rating require separate supplier returns. [Vehicle geometry and essential service power](../../system.toml) · [Airport train interface trial](../mechanical/vehicle/section-trial.toml)

The cooling account separates roof, floor, walls and glass conduction, absorbed sun through roof and glazing, occupant sensible and latent heat, minimum outdoor ventilation, door exchange and internal heat. Fresh air and fan power include occupied and fixed terms. The hot case uses 18% relative humidity outdoors, 50% indoors and a 26°C interior target. The humid-air calculation and coefficient of performance are planning sensitivities. A procurement return needs tested capacity and COP at operating humidity and air temperature, duct static loss, filtration, fouling, failure duty, measured door infiltration and interior temperatures under a timed stop cycle. The motion study receives the electrical power needed to meet the thermal target. When cooling capacity falls short, the electrical budget can still carry that power but the assumed equipment cannot provide the target cabin conditions.

## Station movement and door transfers

The 125 m × 8 m straight island has 6.5 m of assumed horizontal circulation width after two 0.75 m edge reserves. The egress trial places 3 m entrance approaches at opposite ends. The desk model records the waiting queue before the train arrives and then adds the independently accounted arriving train only in the explicit discharge case. Under normal service it reports waiting density, train and platform passenger balance, busiest-door throughput and dwell. It assumes alighting first and scales movement at the busiest door to 1.6 times the mean.

For the 700-passenger departure example, 350 waiting passengers board and 175 alight from 525 on arrival. The busiest of 24 doors receives 35 movements. The screen gives 40.4 seconds before departure in the normal transfer calculation and 52.4 seconds with one assumed assisted transfer at that door. The scheduled dwell is 35 seconds. The three-car formation has 12 boarding-side doors and its centred berth increases approach distance from the island ends. Use actual opening and clearance times, boarding/alighting counts, uneven car loading and the available assisted boarding arrangement when setting dwell. [Airport station bay and platform interface](../prototype/civil-guide.md)

The doorway stack gives 1.310 m nominal trial clear width and 1.302 m when the assumed loaded distortion doubles, against a 1.300 m doorway trial target. The nominal straight gap is 75 mm. Survey the step and gap with passenger loading, wear, suspension travel, platform tolerances and stopping spread. Confirm the assisted boarding threshold, available lift and fallback route with the same survey. The open platform climate screen flags the effect of shade and leaves measured radiant temperature, heat refuge, accessible circulation and operational exposure limits open. [Doorway allowances](../prototype/doorway.toml)

## Horizontal native comparison

JuPedSim 1.4.2 uses the 125 m platform with 5 m long approach necks. Its collision-free speed model starts a fixed-seed population across the platform and routes it to the nearest available neck. Walking, slower walking and wheeled proxy groups use free speeds of 1.25, 0.75 and 0.55 m/s and circular body/vehicle envelopes. Each row tracks people reaching the horizontal exit line. Surveyed stairs, lift capacity and accessibility, equipment pinch points, interactions with people still alighting, protected refuge, detection/pre-movement, staff response and smoke exposure need separate modelling and evidence. [JuPedSim API and model definitions](https://www.jupedsim.org/v1.4.2/api/jupedsim/index.html)

| Population | Two approaches, seconds at 0.05 / 0.025 s step | One approach, seconds at 0.05 / 0.025 s step |
|---:|---:|---:|
| 350 | 109.65 / 109.53 | 208.50 / 208.43 |
| 700 | 163.15 / 153.20 | 301.70 / 296.30 |

Every run reached zero agents on the platform inside the 900 s simulation budget. Halving the time step changes the 700-person, two-approach result by 6.1%. The result needs further convergence and behavioural checks before it could support a station design. [Native geometry, solver digest and clearance traces](passenger-benchmark.json)

For a smoke/tenability handoff, the receipt lists the island and train envelope and the survey inputs needed for FDS. Obtain roof, void, edge and vertical route geometry, ventilation state, wind, fire-growth and material data, then agree the tenability criteria and mesh validation with the fire engineer. A clearance result ends at a horizontal line and supplies only one movement component of the required escape time.

## Reproduction

Run from the repository root. The desk model uses the Python standard library. The benchmark uses JuPedSim 1.4.2 from the project environment, saves solver digest, step size, geometry and remaining agents, and reserves and monitors the output filesystem. Choose a fresh output filename for a replay.

```sh
python3 -m cities.Baghdad.engineering.simulation.passengers
python3 -m unittest cities.Baghdad.engineering.simulation.test_passengers
.venv/bin/python -m cities.Baghdad.engineering.simulation.passengers --native build/airport-passengers-replay.json
```
