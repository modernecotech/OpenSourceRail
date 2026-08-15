# RFC 0024 — LFP Thermal Design for High Ambient Temperature

**Status:** Current
**Depends on:** [RFC 0021](0021-battery-traction.md)

## 1. Envelope

The reference train and station equipment must operate in 50 °C ambient and
survive the deployment's declared parked/solar-soak condition. Supplier cell,
module, controller, converter, HVAC, coolant, and enclosure limits replace
generic curves before release.

## 2. Thermal architecture

- Every 225 kWh car pack uses monitored liquid cold plates.
- Each car can isolate its pack and cooling branch.
- Stationary 500 kWh modules use their qualified enclosure cooling system.
- Pumps, fans, valves, pressure, flow, coolant temperature, and leak detection
  are diagnosable.
- Battery cooling is preserved ahead of comfort HVAC during load shedding.
- Fire-mist water and battery coolant are separate circuits.

## 3. Control rules

Charge and discharge current are derated from measured cell temperature,
coolant state, SOC, and supplier limits. Charging is inhibited before any
qualified cell-temperature ceiling is crossed. A failed cooling branch cannot
be hidden by train-level averaging.

The simulator applies ambient/HVAC energy uplift and converter derating, but
does not substitute for cell electrothermal modelling or a climatic-chamber
test.

## 4. Evidence

- selected-cell electrothermal model correlated to supplier/lab data;
- repeated acceleration, regen, and 500 kW dwell-charge duty at 50 °C;
- parked solar soak and restart;
- loss of pump, fan, flow, coolant, sensor, and station cooling;
- thermal propagation and outward-vent interaction;
- passenger-surface temperature and saloon heat ingress; and
- cooling energy, mass, service access, and leak containment.
