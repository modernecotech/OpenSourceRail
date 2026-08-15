# Traction and DC Power — 800 V-Class Reference

**Controlling decision:** [RFC 0021](../../rfcs/0021-battery-traction.md)

The three-car train is three electrically self-contained cars coupled into
one coordinated consist. Each car carries one 225 kWh gross / 180 kWh
routinely usable liquid-cooled LFP pack, two independent traction
controllers, two PMSMs, isolated low-voltage DC/DC equipment, direct-HV DC
HVAC, and one roof-PV MPPT.

```text
Car A: roof PV -> MPPT -----+
       station contact -----+-> 225 kWh LFP -> controller -> PMSM axle 1
       regenerative braking +             -> controller -> PMSM axle 2
                                             -> isolated LV DC/DC
                                             -> direct-HV DC HVAC

Cars B and C repeat the same package.
```

There is no traction transformer, continuous catenary, train-wide AC
distribution, or central auxiliary inverter. Internal electronic motor
drives inside qualified HVAC equipment remain permitted.

## Battery and DC link

| Parameter | Reference value |
|---|---:|
| Chemistry | LFP |
| Consist gross / routinely usable | 675 / 540 kWh |
| Per-car gross / routinely usable | 225 / 180 kWh |
| Architecture class | 800 V-class |
| Nominal operating voltage | 650–700 V DC |
| Provisional normal upper voltage | 740 V DC |
| Under-seat modules | 8 per car, 4 per side |
| Electrical segmentation | 2 contactor-isolated strings per car, subject to topology study |
| Cooling | Liquid cold plates, with independent pack limits at 50 °C ambient |
| Monitoring | Cell/module voltage and temperature plus compartment off-gas detection |

The 740 V provisional limit preserves operating margin below a 750 V-class
candidate controller ceiling. Cell count and SOC window are not released
until controller transient withstand, regeneration overvoltage, contactor
interrupt duty, precharge, isolation monitoring, creepage/clearance, and
charger compatibility are jointly verified.

An identified module hazard causes string- or pack-level isolation according
to the proved topology. The design does not claim individual series-module
bypass.

## Traction equipment

| Parameter | Reference envelope |
|---|---:|
| Motor count | 6, two per powered bogie |
| Controller count | 6, one per motor |
| Type | Heavy-commercial-vehicle-class PMSM/controller set |
| Candidate motor | Inovance HM47-class or qualified equivalent |
| Candidate controller | Inovance LD32-class or qualified equivalent |
| Candidate motor short peak | 350 kW for supplier-qualified duration |
| Installed hardware peak | 2.1 MW |
| Initial train control cap | 1.8 MW |
| Cooling | Per-axle liquid loop branch with monitored flow and temperature |

Supplier names define RFQ and packaging references, not sole-source
requirements. The interface control document shall state voltage/current,
CAN message mapping, torque accuracy, safe-torque-off behavior, thermal
limits, ingress protection, shock/vibration, EMC, fault reporting, mounting,
coolant, and connector requirements.

## Gearbox and adhesion closure

The previous 6.5:1 gearbox ratio is withdrawn. The selected ratio must be
derived from the qualified motor torque-speed map, 760/680 mm new/worn wheel
diameters, 90 km/h service speed, overspeed margin, grade requirement, and
thermal duty.

Analysis shall cover:

- AW0 through AW3 acceleration and jerk;
- dry and wet rail, including coefficient-of-adhesion sweeps at 0.05, 0.10,
  and 0.15;
- maximum wheel torque at new and worn diameter;
- field-weakening and motor/controller overspeed;
- one-controller and one-car-pack unavailable operation;
- regenerative-braking acceptance at high SOC;
- continuous grade and repeated 1 km stop duty at 50 °C ambient; and
- gearbox bearing, lubrication, sealing, and maintainability.

The 1.8 MW control cap remains the release value until these analyses show a
larger command improves timetable performance without exceeding adhesion,
battery, converter, or cooling limits.

## Station charging interface

- Primary mechanical interface: automated conductive side contact.
- Station cabinet: one 500 kW bidirectional DC/DC stage.
- Cabinet current ceiling: 825 A reference.
- Contacts: up to two platform contacts sharing one interlocked cabinet
  budget; they are never each allocated 500 kW simultaneously.
- Normal dwell: approximately 60 seconds, giving about 8 kWh after losses.
- Terminal: same 500 kW hardware with a longer balancing dwell.
- Train protection: HVIL, insulation monitoring, precharge, weld detection,
  touch-safe sequencing, emergency isolation, and BMS charge limit.

At 700 V the ideal current at 500 kW is about 714 A; at 650 V it is about
769 A. The simulation and controller enforce power, current, battery charge
acceptance, conversion loss, and ambient derating at the same time.

## Rooftop PV

The existing approximately 15.12 kWp train roof array is retained as an
auxiliary-energy offset and SOC-maintenance source, not the primary traction
supply. Each car has its own MPPT, isolation switch, combiner, protected DC
interface, and removable wiring route. Solar cables are not embedded in the
roof laminate.

Both bonded flexible and rail-mounted rigid module packaging remain
prototyping candidates until wind, vibration, fire, bonding, water-ingress,
and replacement evidence selects one production arrangement.

## Auxiliary power

| Domain | Architecture |
|---|---|
| HVAC | Direct 650–700 V DC input rail unit with internal motor electronics |
| Safety controls | Redundant isolated 24/48 V DC/DC domains |
| Doors and lighting | Isolated LV DC distribution with local protection |
| PIS, CCTV and compute | Separate isolated service domain with load shedding |
| Pumps and cooling | Monitored DC supplies; fire-mist pump independent per car |

Loss of a nonessential service domain must not remove braking, door release,
fire detection, emergency lighting, communications, or pack isolation.

## Fire protection interface

Each battery module is enclosed, monitored for temperature and off-gas, and
vented outward. Each car carries a small water reservoir, DC pump, monitored
stainless distribution line, and mist nozzles serving only battery
compartments. The system cools adjacent modules and slows propagation; it
does not claim to terminate cell-level thermal runaway.

Traction controllers, DC/DC equipment, and HVAC electronics use
fire-resistant metal enclosures, detection, and electrical isolation. They
do not have automatic gaseous or water-mist suppression. The saloon has no
automatic sprinkler or CO2 flooding system.

## Release evidence

- Pack cell/string topology and voltage/transient analysis.
- Motor/controller/gearbox duty-cycle simulation and dynamometer evidence.
- AW3 adhesion, grade, acceleration, regen, and stopping analysis.
- 50 °C train and station converter thermal/derating tests.
- Charger shared-contact arbitration and failed-cabinet scenarios.
- Battery-module propagation, vent and mist flow/pressure tests.
- EMC, shock/vibration, ingress, insulation and high-potential tests.
- Supplier-neutral interface control drawings and acceptance procedures.
