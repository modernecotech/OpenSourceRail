# Powered-bogie traction supply: bounded prototype decision screen

The [input](input.json) and [machine-readable screen](screen.json) compare three
**separate research physical candidates** descended from the selected passive
vehicle. The existing selected vehicle, evaluation and selection are unchanged.
The result is a numerical demand and procurement screen, not an installed
propulsion selection or approval to carry passengers. Its evaluation and source
identities are in `screen.json`.

This reuses the [same event-resolved demand model](../v07-demonstrator-propulsion/README.md)
for 1.5 and 2 km synthetic legs at −2%, level and +2% grades. It uses the
selected six 17 m cars, 276 normal places, 72 km/h cap, 0.4 m/s² commanded
acceleration, 0.6 m/s² independent stopping target and 120 s comparison
headway. The 160-person/car case is a **crowd structural and energy sensitivity**,
not an approved high-capacity operating formation. Neither case includes
unknown traction equipment in complete installed mass.

## Directional demand and supply choice

The most demanding normal-load analytical case here is the 2 km, +2% uphill
leg. It reaches the destination in 141.7 s with **1.866 MW peak mechanical
power** and **23.88 kWh mechanical motoring energy** per train. The explicit
85% drive-efficiency and 30 kW auxiliary hypotheses turn this into 2.225 MW
peak electrical demand and 29.28 kWh per leg. No regenerative braking credit
is taken. These values are required demand, not rated or measured equipment.

| Supply research candidate | 2 km, +2% sizing result | Prototype consequence |
|---|---:|---|
| Battery only, station charge | 97.6 kWh nominal for two legs with 60% usable window; 22.8 h⁻¹ peak discharge ratio; 3.35 MW charger at 35 s and 90% charge efficiency | Needs a high-power pack, contacts, cooling and station charger; not a small simple store. |
| Battery plus supercapacitor | If battery output is capped at 0.5 MW, capacitor supplies 14.69 kWh/leg and peaks at 1.73 MW; two-leg nominal capacitor 58.74 kWh at 50% usable window; charger remains 3.35 MW | Shifts peak power from battery but does not remove station energy and charging infrastructure. |
| Roof collector and protected rigid overhead 1.5 kV DC | 1.48 kA peak train current under the electrical hypothesis; 24 driven axles need about 77.75 kW peak mechanical each before a 25% rating allowance | Preferred **prototype research layout** for procurement and interface design. Supply, return, protection and rescue remain unqualified. |

The station-store figures are **hypotheses**, not supplier specifications. The
screen reports the required energy and power density for illustrative 300,
1,000 and 2,000 kg pack masses, instead of assigning an unverified battery or
capacitor mass. An existing 82.8 kWh selected-car service battery remains
service-only and is not counted as traction energy.

The 1.48 kA is ideal current at nominal voltage; supply sag and losses raise
the actual requirement. Simultaneous trains, feeder voltage drop, substation
count, protective sectioning and regeneration receptivity have **not** been
evaluated. The continuous supply removes a megawatt station charging task but adds a
roof collector, rigid overhead contact, sectioning, return, feeder, rectifier,
insulation, earthing, touch protection, emergency access and civil clearance.
Their dimensions, masses, cost and ratings remain unknown. [Siemens lists
750–1,500 V DC metro traction converter modules](https://www.mobility.siemens.com/global/en/portfolio/rolling-stock-components/traction-converters.html)
and [1,500 V DC overhead supply with motor bogies in light rail products](https://www.mobility.siemens.com/us/en/portfolio/rolling-stock/light-rail-vehicles.html).
Siemens lists 1C2M–1C4M converter configurations and 460–1,100 kW products
for the 750–1,500 V DC range. Six nominal 1C4M groups are therefore one
**quotation configuration**, subject to actual continuous and peak ratings,
cooling, regeneration and fault segregation. This establishes an available
technology family, not a matched supplier design, local-manufacturing price or
approval of the proposed railway.

## Traction and independent braking are separate gates

At +2% uphill, ideal uniform loading needs wheel–rail adhesion at least
**0.0633 with 24 driven axles**, or **0.0949 with 16 driven axles**, before
load transfer, wet rail, slip control and equipment mass. The 24-axle research
choice reduces the necessary adhesion bound but increases motor/gear/inverter
count. At the inherited μ=0.05 hypothesis, neither axle count is proven to
meet commanded acceleration on that grade.

For a normal-load 2% downgrade at 0.6 m/s², an optimistic low-speed necessary
bound needs **111.0 kN** independent train brake force. μ=0.05 wheel contact
offers at most **66.7 kN**, leaving **44.3 kN** to demonstrate through measured
higher adhesion or an independent rail-contact/track brake, plus parking and
faulted-stop margins. A [manufacturer's magnetic track-brake catalogue](https://rail.knorr-bremse.com/media/2000-products/product-broschures/p-1269-magnetact.pdf)
lists metro applications and magnetic *attractive* force, but it does not give
the longitudinal braking force for this rail, speed, temperature and gap.
No product has been selected and no brake-force credit has been taken.

The base demand predates added motor, gear, inverter, collector, cooling,
protection and brake mass. The screen therefore also tests **+0.8 and +2.1
t/car** as illustrative added-equipment sensitivities; at +2.1 t/car the
2 km, +2% mechanical peak rises to **2.022 MW**. Installed mass, centre of
gravity, axle reactions and structural/civil consequences remain open.

## First prototype quotation and test boundary

Request one itemised quote for 24 motor/gear/axle installations, six inverter
and protection groups, collector and rigid overhead contact, DC supply and
return, sectioning, regenerative sink, independent brake, separately sized
rescue store, cooling and all mounts, wiring and access. Return actual ratings,
mass, dimensions, local fabrication hours, supplier origins, replacement parts
and a **single installed price**. A supplier choice must include full-load
force/current/thermal maps, repeated 120 s duty, low-adhesion and faulted-stop
tests, conductor clearance and touch safety, plus protected tow on a surveyed
alignment. The [vehicle integration package](../v07-representative-car/README.md)
must reconcile this distinct child before it can become an installed candidate.

Reproduce without native CAD or supplier assumptions:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m engineering.design_search.powered_bogie_screen --check
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q engineering/design_search/tests/test_powered_bogie_screen.py
```
