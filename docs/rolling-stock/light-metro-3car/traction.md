# Traction + auxiliary power — `light-metro-3car`

Per RFC 0008 §3.2. All-electric; no pneumatic / hydraulic systems
on the safety-actuator path. Regenerative braking is the default
mode; friction disc brake blends in below 8 km/h and handles
emergency brake application.

## Propulsion topology

```
  [120 kWh Na-ion under-seat pack, Car A] ──DC── [SiC inverter] ── [powered bogie A]
  [120 kWh Na-ion under-seat pack, Car B] ──DC── [SiC inverter] ── [powered bogie B]
  [120 kWh Na-ion under-seat pack, Car C] ──DC── [SiC inverter] ── [powered bogie C]

  Station charger → side-pin / pantograph-down dock → per-car DC link
```

Each car is electrically self-contained. A car can isolate its own
pack and traction equipment while the rest of the consist remains
recoverable at restricted speed. `osr-bms` manages per-car contactors,
cell balancing, and SoC / SoH estimation.

## Batteries

| Parameter | Value |
|---|---|
| Chemistry (default) | Sodium-ion (Na-ion) |
| Chemistry (alternate) | LFP (drop-in, per-operator) |
| Nominal pack voltage | 1 500 V DC |
| Pack capacity (each car) | 120 kWh usable (~150 kWh nameplate at commissioning) |
| Consist total capacity | 360 kWh usable |
| Module count per pack | 8 under-seat modules per car |
| Cell chemistry | 3.0–3.7 V Na-ion (CATL / HiNa / local equiv.) |
| Pack mass | ~0.9 t per car, ~2.7 t consist total |
| Location | Under longitudinal seats, split both sides of the saloon |
| Thermal management | Chiller-fed cold plates tied into the HVAC loop |
| Fire containment | Sealed aluminium module boxes with side vent duct and aspirating smoke detection (feeds `osr-fire-safety`) |

Pack sizing per RFC 0002: 360 kWh gives roughly one route length
plus 20 % reserve and HVAC uplift at 50 °C ambient. Normal service
energy is replaced during station dwells.

## Traction motors

| Parameter | Value |
|---|---|
| Count | 6 (two axles on each of three powered bogies) |
| Type | Permanent-magnet synchronous (PMSM), axle-mount |
| Continuous rating | 180 kW per axle |
| Peak rating | 320 kW per axle (≤ 60 s) |
| Rated torque | 1 800 Nm at wheel |
| Efficiency at peak | ≥ 96 % |
| Mass | 520 kg each |
| Cooling | Water (shares cold plate with SiC inverter) |
| Bearing grease | Sealed-for-life; EN 50155 grade |

Peak onboard motor output (six motors, both directions) = 1 800 kW,
matching RFC 0008 §1.

## Inverters

| Parameter | Value |
|---|---|
| Count | 3 (one per powered bogie) |
| Type | 3-phase voltage-source, silicon-carbide MOSFETs |
| Rating | 360 kW continuous, 600 kW peak |
| Switching frequency | 5 kHz nominal |
| Efficiency at peak | ≥ 98 % |
| Cooling | Forced water via cold plate, shared with motor |
| Volume | 450 × 300 × 180 mm per inverter |

Reference parts: Wolfspeed SiC MOSFET half-bridges (e.g.
CAB450M12HM3) or local equivalent. Controlled by `osr-traction`
firmware on the T-ECU/S safety MCU (RP2350).

## Reduction gear

- Single-stage helical, 6.5:1 ratio.
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
  F_motor_peak = 1 800 Nm × 6.5 / 0.43 m = 27.2 kN
```

Adhesion is the binding constraint at wet-rail AW3. Per-axle
tachometer feeds `osr-traction` anti-slip which clamps torque
to ≤ 0.9 × F_adhesion under wheel-slip detection (matches
`osr-brake` WSP conservative property B4).

## Station charging

- Primary connector: side-pin per RFC 0026.
- Alternate connector: pantograph-down OppCharge-style dock where
  platform geometry requires it.
- Dock: passenger stations at roughly 1 km spacing, buffered by
  station solar PV + stationary Na-ion battery.
- Charge power: 500 kW nominal; 1 000 kW at terminals or high-load
  stations.
- Dwell charge: 60 s at 500 kW adds ~8 kWh; 60 s at 1 MW adds
  ~17 kWh before losses.

**No continuous catenary.** Pantograph is raised only at
discrete charging docks where the alternate connector is selected.
This is the catenary-free bet from
[ARCHITECTURE §D7](../../ARCHITECTURE.md#d7-energy--buildings).

## Regenerative braking

- `osr-regen` arbitrates between:
  1. Battery absorb (preferred, unless pack SoC > 95 %).
  2. Station-dock export (if in contact with a charging dock).
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
| Door motors | 2 kW total (centre door pairs, not simultaneously) | |
| Recovery cabinet + onboard controls | 0.5 kW per end | |
| Compressor (for air-horn only — NO brake air) | 0.5 kW | |

Total aux design load: ~75 kW at AW3 in Samawah climate (hot
day + full HVAC). `osr-aux-power` shed-load logic runs HVAC at
reduced compressor duty when pack SoC < 30 %.

## v2 deliverables (not in v1)

- PMSM motor winding data + thermal FEA.
- SiC inverter gate-driver schematic + PCB stackup.
- Pack battery management system (BMS) detail schematic.
- Station charging connector + dock mechanical drawings.
- Adhesion + slip simulation at 0.05 / 0.1 / 0.15 friction.
- Worst-case thermal analysis for battery pack under 50 °C
  ambient + fast-charge.
