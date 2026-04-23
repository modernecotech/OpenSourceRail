# W-SBC DIY assembly

Wayside SBC (RFC 0007 §6, RFC 0016). Deployed in trackside
junction boxes, pole-mount cabinets, or under-platform housings.
One W-SBC per instrumented track section.

## Bill of materials

| # | Part | SKU | Qty | Unit (USD) | Subtotal |
|---|---|---|---|---|---|
| 1 | Radxa CM5 industrial-temp (RK3588S) | rock-cm5-industrial | 1 | 110 | 110 |
| 2 | Radxa CM5 IO Board | rock-cm5-io | 1 | 40 | 40 |
| 3 | SainSmart 8-channel 24 V opto-isolated relay (switch-motor 2oo2 stage) | SSR-8DC24 | 1 | 12 | 12 |
| 4 | Adafruit ATECC608B | Adafruit 4374 | 1 | 4 | 4 |
| 5 | MCP23017 I/O expander (8 isolated DI, 4 isolated DO) | Adafruit 732 | 1 | 7 | 7 |
| 6 | Waveshare 2-CH CAN-FD HAT (radar bus + switch-motor CAN) | 2-CH-CAN-FD-HAT | 1 | 28 | 28 |
| 7 | IP67 pole-mount cabinet 400 × 300 × 200 mm | RBM-5 | 1 | 110 | 110 |
| 8 | Radxa CM5 DIN-rail industrial enclosure | rock-cm5-din-industrial | 1 | 45 | 45 |
| 9 | Mean Well HDR-60-24 DIN PSU | HDR-60-24 | 1 | 35 | 35 |
| 10 | Phoenix Contact 24-position terminal block | UT 2.5 DIN | 2 | 8 | 16 |
| 11 | Cat 6a 5 m patch (TSN backbone to adjacent W-SBC) | generic | 2 | 5 | 10 |

**Subtotal: ~$417 per W-SBC.** Add intrusion-sensor pack
(LIDAR / radar / camera / fence-line) separately per RFC 0016.

## What the W-SBC hosts

Per RFC 0005 §4.6 the W-SBC runs the wayside SIL-4 + SIL-2
crate family:

- `osr-interlocking` — Movement Authority computer
- `osr-consensus` — Raft log node (3-node minimum cluster per line)
- `osr-wayside-points` — switch-machine controller (SIL-4)
- `osr-intrusion-detect` — RFC 0016 wayside-intrusion evaluator
- `osr-balise` — balise registry
- `osr-level-crossing` — LX controller where applicable
- `osr-hot-axle-wayside` — HABD
- `osr-energy-site` — PV / battery dispatch at solar-equipped sites

Not every W-SBC needs every role — the junction box near a switch
runs `osr-wayside-points`; the one near a PV site runs
`osr-energy-site`. The per-W-SBC role config is in
`/etc/osr/config.toml` on the SD card.

## Architecture

```
 ┌─ IP67 pole-mount cabinet ──────────────────────────────────────┐
 │                                                                 │
 │   Mean Well HDR-60-24 PSU: 24 V in (cabinet bus) → 5 V         │
 │                                                                 │
 │   Radxa CM5 IO Board                                            │
 │     ├── HDMI (commissioning)                                     │
 │     ├── USB-C (console)                                          │
 │     ├── 2× 1000BASE-T Ethernet (TSN backbone + LIDAR)           │
 │     ├── 40-pin GPIO ──► Waveshare CAN-FD HAT                    │
 │     ├── I²C ──► ATECC608B (consensus-entry signing)              │
 │     └── MCP23017 ──► 8 isolated DI (fence-line sensors,          │
 │         ► 4 isolated DO (switch-motor relay drive + LX barrier)  │
 │                                                                 │
 │   SainSmart 8-ch relay (2oo2 AND for switch-motor):            │
 │     Both CM5 A+B GPIO routes must close to energise motor       │
 │                                                                 │
 │   Terminal block (Phoenix UT 2.5 DIN):                          │
 │     VIN+ / VIN- / EARTH                                         │
 │     FENCE-1-A ... FENCE-1-B (fence-line sensor pair)            │
 │     LIDAR-ETH / LIDAR-POWER                                     │
 │     RADAR-CAN-H / RADAR-CAN-L / RADAR-POWER                     │
 │     SWITCH-MOTOR-A / SWITCH-MOTOR-B                             │
 └─────────────────────────────────────────────────────────────────┘
```

## Safety architecture

W-SBC's SIL-4 argument differs from T-ECU/S: where the train
uses hardware 2oo2 at the CPU level (two Pico 2s), the wayside
uses **consensus-level redundancy** — three W-SBCs in a Raft
cluster per line, any two outvoting a faulty third.

At the **actuator output** level (switch motor, LX barrier),
the W-SBC still uses the 2oo2 AND-gate relay pattern — two
CM5 GPIO outputs each drive one relay in the series chain to
the actuator coil. Both must close for the actuator to move.
A single CM5 GPIO stuck-at-high cannot energise the motor by
itself.

The 2oo2 at the actuator, plus consensus at the logic, plus
the intrusion-detect gate (d) in `section_available_to` (RFC
0016 v2), is what gives wayside its SIL-4 argument end-to-end.

## Sensor integration (per RFC 0016)

Each W-SBC serves a single track section (typically 500 m –
1 km). The intrusion-detect sensor pack plugs in via:

| Sensor | Interface | Cable |
|---|---|---|
| Livox Mid-360 360° LIDAR | 1000BASE-T + 12 V barrel | Cat 6a + 12 V DC |
| TI AWR1843BOOST radar | CAN-FD | M12 4-pin T-code |
| Reolink RLC-810A 4 K camera (optional) | 1000BASE-T PoE | Cat 6a |
| Senstar FlexZone fence-line (opt) | 2× isolated DI | Twisted pair |

All field-side connections run through the cabinet's MCP23017
(isolated DI) or Ethernet switch (LIDAR + camera).

## Boot + commissioning

```bash
sudo osr-selftest --role w-sbc
```

Exercises the configured intrusion-sensor pack + switch-motor
output (if applicable) + ATECC608B signing chain + Raft
cluster membership. Refuses to enter service until all three
Raft peers are reachable.

## Climate considerations

The Radxa CM5 industrial-temp variant is rated −40 °C to
+85 °C ambient. For Samawah's +55 °C summer shade inside a
pole-mount cabinet is ~65 °C interior — well inside spec.

Dust resilience: the IP67 cabinet + radxa's conformal-coated
option keeps the electronics serviceable through a haboob.
LIDAR housings need wipe-down after each storm per RFC 0013
M7.2 — the rest of the cabinet is maintenance-free until the
annual inspection.
