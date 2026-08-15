# RFC 0002 — Energy Sizing Method

**Status:** Current
**Depends on:** [RFC 0021](0021-battery-traction.md), [RFC 0024](0024-battery-thermal-high-ambient.md), [RFC 0026](0026-charging-connector-reconciliation.md)

## 1. Purpose

This RFC defines the calculation method for onboard energy, station storage,
charging, solar generation, and grid backup. Equipment selection is governed
by RFC 0021.

## 2. Canonical equipment units

| Unit | Reference |
|---|---:|
| Onboard gross energy | 225 kWh LFP per car |
| Onboard routinely usable energy | 180 kWh per car |
| Normal stationary storage module | 500 kWh gross LFP |
| Station charger cabinet | 500 kW bidirectional DC/DC |
| Cabinet current limit | 825 A |
| Platform contacts | 2 sharing one cabinet budget |
| Nominal train DC range | 650–700 V |
| Charger efficiency used in planning | 98% unless qualified data replaces it |

Additional capacity is built by repeating these units. The generator does not
create a separate high-power charger product.

## 3. Sizing sequence

For every line and service window:

1. Calculate car-km from route length, headway, fleet turns, deadhead, and
   depot movements.
2. Apply the selected train's kWh/car-km and climate/HVAC factor.
3. Simulate every station arrival, dwell, contact conflict, conversion loss,
   current ceiling, battery acceptance limit, and charger outage.
4. Protect 20% onboard SOC unless a stricter deployment rule applies.
5. Add terminal/depot balancing dwell before adding stationary modules or
   cabinets.
6. Size PV from local hourly yield, temperature, soiling, shading, and
   maintenance availability.
7. Size grid import/export for the residual energy and resilience duty.

The design passes only when the full service window meets SOC reserve,
service-completion, thermal, and failed-equipment criteria. Daily energy
balance alone is insufficient.

## 4. Reference train

The promoted three-car set contains 675 kWh gross / 540 kWh usable energy.
The other catalogue families use the same 225/180 kWh per-car module basis.
Energy intensity starts at 2.4 kWh/car-km before deployment climate uplift;
the simulator and measured duty replace that planning seed as evidence
matures.

## 5. Station and grid rules

- Passenger stations start with one 500 kWh module and one 500 kW cabinet.
- Terminals gain energy through dwell, not different hardware.
- Four-car high-throughput families use three complete modules/cabinets and
  six-car families use four. These counts keep energy-derived dwell near the
  peak-service envelope in the canonical large-city simulations.
- Contacts never each receive the full shared-cabinet rating simultaneously.
- Grid AC is rectified once into the station DC bus; the train never consumes
  station AC.
- Solar is an energy source, not a guarantee of instantaneous charging power.
- Grid outage, charger outage, low-solar, and simultaneous-arrival cases are
  mandatory.

## 6. Evidence

Every generated deployment records input hashes, equipment-unit counts,
minimum SOC, service completion, curtailed/exported energy, grid import,
charger contention, adaptive-service events, and invariant violations.
