# Traction + auxiliary power — `light-metro-3car`

Per RFC 0008 §3.2. All-electric; no pneumatic / hydraulic systems
on the safety-actuator path. Regenerative braking is the default
mode; friction disc brake blends in below 8 km/h and handles
emergency brake application.

## Propulsion topology

```
  [Na-ion battery pack A] ──DC─┐
                               ├── 1500V DC bus
  [Na-ion battery pack B] ──DC─┤
                               │
  [Pantograph dock, 1500V DC] ─┤  (charging only; no catenary)
                               │
                           ┌───┴───┐
                           │       │
              [SiC inverter 1]    [SiC inverter 3]
                  (Bogie 1)          (Bogie 3)
                       │                   │
              [PMSM motor 1]        [PMSM motor 3]
                 (axle-mount)         (axle-mount)
```

Two battery packs (one under Car A, one under Car C). Either
pack alone can deliver enough energy for safe-stop + inching
back to depot. `osr-bms` manages per-pack contactors, cell
balancing, and SoC / SoH estimation.

## Batteries

| Parameter | Value |
|---|---|
| Chemistry (default) | Sodium-ion (Na-ion) |
| Chemistry (alternate) | LFP (drop-in, per-operator) |
| Nominal pack voltage | 1 500 V DC |
| Pack capacity (each) | 450 kWh |
| Consist total capacity | 900 kWh |
| Module count per pack | ≤ 30 |
| Cell chemistry | 3.0–3.7 V Na-ion (CATL / HiNa / local equiv.) |
| Pack mass | 7.5 t each (15 t consist total) |
| Location | Underfloor of Car A (pack A) + Car C (pack B) |
| Thermal management | Forced-air cooling with 6 kW chiller-fed cold plate |
| Fire containment | Steel battery-bay enclosure with aspirating smoke detection (feeds `osr-fire-safety`) |

Pack sizing per RFC 0002: 900 kWh gives one full round-trip at
Samawah peak headway (4 min) + 20 % reserve + HVAC uplift at
50 °C ambient per RFC 0003 climate envelope.

## Traction motors

| Parameter | Value |
|---|---|
| Count | 2 (one per driving bogie) |
| Type | Permanent-magnet synchronous (PMSM), axle-mount |
| Continuous rating | 200 kW |
| Peak rating | 600 kW (30 s) |
| Rated torque | 1 800 Nm at wheel |
| Efficiency at peak | ≥ 96 % |
| Mass | 520 kg each |
| Cooling | Water (shares cold plate with SiC inverter) |
| Bearing grease | Sealed-for-life; EN 50155 grade |

Peak traction power (both motors, both directions) = 1 200 kW,
matching RFC 0008 §1.

## Inverters

| Parameter | Value |
|---|---|
| Count | 2 (one per driving bogie) |
| Type | 3-phase voltage-source, silicon-carbide MOSFETs |
| Rating | 300 kW continuous, 600 kW peak |
| Switching frequency | 5 kHz nominal |
| Efficiency at peak | ≥ 98 % |
| Cooling | Forced water via cold plate, shared with motor |
| Volume | 450 × 300 × 180 mm per inverter |

Reference parts: Wolfspeed SiC MOSFET half-bridges (e.g.
CAB450M12HM3) or local equivalent. Controlled by `osr-traction`
firmware on the T-ECU/S safety MCU (RP2350).

## Reduction gear

- Single-stage helical, 3.8:1 ratio.
- Axle-mounted; no separate gearbox.
- Oil-bath, sealed for 600 000 km (matches RFC 0008 §5 bogie
  overhaul interval).
- Mass 120 kg per bogie.

## Adhesion budget

At 14 t/axle and coefficient of friction 0.1 (wet rail,
conservative), each powered axle can transmit:

```
  F_adhesion = 14 000 kg × 9.81 m/s² × 0.1 = 13.7 kN
```

Per-motor torque at wheel (wheel radius 0.43 m):

```
  F_motor_peak = 1 800 Nm × 3.8 / 0.43 m = 15.9 kN
```

Adhesion is the binding constraint at wet-rail AW3. Per-axle
tachometer feeds `osr-traction` anti-slip which clamps torque
to ≤ 0.9 × F_adhesion under wheel-slip detection (matches
`osr-brake` WSP conservative property B4).

## Opportunity charging

- Pantograph: roof-mounted on Car A and Car C. Single-arm
  PZ-series or local equivalent, 1 500 V DC + 400 A contact.
- Dock: overhead bus bar at terminal + depot-terminal stations
  (RFC 0010 archetype `terminal` / `depot-terminal`).
- Charge power: up to 1 000 kW (matches `charging_power_kw` in
  RFC 0010 stations template).
- Raise/lower actuation: electrical (no pneumatic).
- Inter-trip charging: 60 s dwell at a 1 000 kW terminal adds
  ~17 kWh — roughly 2–3 km of operation.

**No continuous catenary.** Pantograph is raised only at
charging docks. This is the catenary-free bet from
[ARCHITECTURE §D7](../../ARCHITECTURE.md#d7-energy--buildings).

## Regenerative braking

- `osr-regen` arbitrates between:
  1. Battery absorb (preferred, unless pack SoC > 95 %).
  2. Pantograph export (if in contact with terminal dock).
  3. Dump resistor (only if neither of the above is available;
     roof-mounted).
- Blend-down to friction brake below 8 km/h; friction holds
  down to rest.

## Auxiliary power

Aux inverter (400 V / 3-phase AC output + 110 V / 24 V DC):

| Load | Nominal power | Notes |
|---|---|---|
| HVAC (3 units — one per car) | 60 kW total | |
| Interior + exterior lighting | 6 kW | |
| PIS displays + onboard compute | 2 kW | |
| Door motors | 4 kW total (all 24 doors, but not simultaneously) | |
| Cab DMI + controls | 0.5 kW per cab | |
| Compressor (for air-horn only — NO brake air) | 0.5 kW | |

Total aux design load: ~75 kW at AW3 in Samawah climate (hot
day + full HVAC). `osr-aux-power` shed-load logic runs HVAC at
reduced compressor duty when pack SoC < 30 %.

## v2 deliverables (not in v1)

- PMSM motor winding data + thermal FEA.
- SiC inverter gate-driver schematic + PCB stackup.
- Pack battery management system (BMS) detail schematic.
- Pantograph + dock mechanical drawings.
- Adhesion + slip simulation at 0.05 / 0.1 / 0.15 friction.
- Worst-case thermal analysis for battery pack under 50 °C
  ambient + fast-charge.
