# RFC 0021 — 800 V-Class LFP Battery and Traction Architecture

**Status:** Current reference architecture
**Date:** 2026-08-14
**Depends on:** [RFC 0008](0008-rolling-stock-reference-design.md), [RFC 0020](0020-crashworthiness.md), [RFC 0024](0024-battery-thermal-high-ambient.md), [RFC 0026](0026-charging-connector-reconciliation.md), [RFC 0028](0028-construction-quality-assurance.md)

## 1. Decision

OpenSourceRail uses one catenary-free, 800 V-class LFP architecture. The
promoted three-car train operates at approximately 650–700 V nominal and has:

- 675 kWh gross / 540 kWh routinely usable LFP;
- three independently serviceable 225 kWh gross car packs;
- two contactor-isolated strings per car, subject to the final pack study;
- six heavy-commercial-vehicle PMSMs and six matched controllers;
- 2.1 MW installed short-duration capability with a 1.8 MW control cap;
- direct-HV DC HVAC and isolated 110/48/24 V DC/DC domains;
- one protected roof-PV MPPT per car; and
- no traction transformer, train-wide auxiliary AC bus, or continuous
  wayside electrification.

Named products are RFQ reference candidates, not sole-source selections or
proof of railway suitability. Supplier qualification, railway environmental
tests, integration evidence, warranty, spares, and delivered scope remain
mandatory.

## 2. Per-car topology

```text
roof PV -> MPPT --------------------------+
station contact -> protected DC interface +--> 225 kWh LFP car pack
regenerative braking ---------------------+          |
                                                      +-> controller -> PMSM axle 1
                                                      +-> controller -> PMSM axle 2
                                                      +-> isolated LV DC/DC
                                                      +-> direct-HV DC HVAC
```

Each car protects and reports its own HV source. Train-level software may
coordinate power limits but cannot replace local BMS protection or assume
that either neighbouring car pack is available.

Required interface values include minimum/nominal/maximum voltage,
continuous and pulse current, regeneration overvoltage margin, contactor
interrupt rating, precharge energy, insulation thresholds,
creepage/clearance, cooling duty, EMC, and 50 °C derating. The provisional
normal upper voltage is 740 V until the selected controller and switching
transients are qualified together.

## 3. Reference traction candidates

- EVE-class liquid-cooled high-power/railway LFP cells and modules;
- Inovance HM47-class PMSM and LD32-class controller, one controller per
  motor; and
- Longertek-class direct-HV DC rail HVAC.

Equivalent equipment is acceptable when it satisfies the OSR interface
control document and qualification plan.

The gearbox ratio is derived from the selected motor torque-speed map; no
historic ratio is inherited. Acceptance covers AW0–AW3 acceleration, grade,
wet-rail adhesion, wheel wear, motor/controller overspeed, regenerative
braking, one-channel unavailable operation, and repeated-stop thermal duty
at 50 °C ambient.

## 4. Station DC architecture

```text
PV -> MPPT DC/DC -> station DC bus <-> 500 kWh LFP module(s)
grid AC -> rectifier --------------------^
                                          |
                           500 kW DC/DC --+--> interlocked platform contacts
```

The normal three-car station starts with one 500 kWh gross stationary-LFP
module, one 500 kW bidirectional DC/DC cabinet, and two mechanically separate
contacts sharing that single cabinet budget. Terminals use the same hardware
with longer dwell. At 700 V, 500 kW is about 714 A; at 650 V it is about
769 A. Power, current, efficiency, cable/contact loss, temperature derating,
battery charge acceptance, and simultaneous arrivals are enforced together.

A 60-second charge adds approximately 8 kWh after loss. It is a top-up, not a
full recharge. The onboard pack absorbs route-to-route imbalance and terminal
or depot dwell restores the daily energy balance.

The reference station power stage is a SINEXCEL PDS1-750K-H-class
bidirectional DC/DC converter configured to 500 kW. The station separately
provides isolation/earthing, insulation monitoring, cooling, contactors,
emergency isolation, and safe contact sequencing.

Four-car high-throughput deployments use three complete 500 kWh storage
modules and 500 kW cabinet/contact units; six-car deployments use four. The
counts are the lowest standard-module quantities that keep the canonical
large-city EOL-battery and maximum-climate simulations within their service
floor. Storage power and the grid interface scale with the repeated modules;
generated CAPEX carries every module. High-throughput fleet sizing also
retains the aggregate onboard reserve demonstrated by the degraded-energy
suite rather than shrinking solely because charging dwell becomes shorter.
This is replication of one standard module, not a separate 1 MW product tier.

## 5. Battery fire protection

IEC 62928 is a design and test input. Each under-seat module has a
fire-resistant enclosure, outward gas vent, temperature monitoring, and
off-gas detection. The pack must limit propagation for the required
evacuation interval.

Each car has an independent localized cooling system:

```text
water reservoir -> monitored DC pump -> stainless distribution pipe
                 -> battery-compartment mist nozzles
```

The mist cools adjacent modules and restricts propagation; it does not claim
to stop cell-level thermal runaway. Passenger saloons have no automatic
sprinklers or CO2 flooding. Controllers, DC/DC equipment, and HVAC electronics
use fire-resistant metal enclosures, detection, and electrical isolation.

The staged response is:

1. Validate the event and inhibit charging.
2. Isolate the affected string or car pack according to the proved topology.
3. Restrict traction, alert TCMS/OCC, and request the nearest safe platform.
4. Discharge localized mist around the affected compartment.
5. Apply emergency braking if containment or essential control is lost.
6. Release doors only where the train/platform hazard assessment permits.

Reservoir level, pump current, line pressure, flow, nozzle continuity, sensor
disagreement, and isolation state are diagnosable.

## 6. Body and service interfaces

The welded S355 underframe and spaceframe carry bogie, coupler, crash,
anti-climber, and longitudinal loads. Composite side, portal, skirt, nose,
ceiling, and roof cassettes use:

- 3-2-1 datum location with an asymmetric anti-reversal key;
- standardized captive fasteners;
- a controlled adhesive/sealant groove plus mechanical retention;
- defined bonding points; and
- keyed service connectors.

Composite cassettes may contain empty HVAC ducts, drains, cable raceways,
clips, and equipment bosses. Cables, pipes, sensors, fans, filters,
evaporators, dampers, and lights remain removable through access covers and
are never encapsulated in laminate.

## 7. Procurement targets

Planning targets, pending comparable delivered-scope RFQs:

| Equipment | Target |
|---|---:|
| Complete 675 kWh traction-battery system | 65–80 kUSD/train |
| Six motor/controller sets | 48–72 kUSD/train |
| HV distribution/contactors | 8–12 kUSD/train |
| LV DC/DC equipment | 5–10 kUSD/train |
| Roof-PV MPPT/DC equipment | 2–4 kUSD/train |
| 500 kWh stationary-LFP module, BMS/cooling/enclosure/protection | 35–40 kUSD/site |
| 500 kW DC/DC power stage | 10–20 kUSD/site |
| Contact/protection/control package | 10–15 kUSD/site |

These are affordability gates, not quotations. RFQs separate hardware,
qualification, software/interface support, warranty, spares, delivery, and
local integration.

## 8. Release gates

The architecture is not released for manufacture until these close:

- cell/string count and voltage/transient margin;
- isolation, earthing, HVIL, precharge, and fault interruption;
- gearing, acceleration, adhesion, grade, overspeed, and thermal duty;
- dwell charging, simultaneous arrivals, charger outage, low-solar days,
  terminal balancing, and minimum route SOC;
- propagation, vent routing, mist flow/pressure, failed-suppression behavior,
  detection latency, and evacuation time;
- composite fire/smoke/toxicity, insert pull-out, bond durability, water
  ingress, module-removal time, and repair method;
- mass, centre of gravity, axle load, crash load path, and FEA; and
- supplier RFQs and qualified-equivalent interface evidence.
