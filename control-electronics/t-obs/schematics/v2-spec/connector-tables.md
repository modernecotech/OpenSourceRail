# T-OBS v2 — connector tables

All external connectors use M12 series for field-side I/O
(matches T-ECU/S and T-ECU/A). Internal ribbon + FFC for the
nose-cone camera + ultrasonic drive runs.

## External connectors

| Ref | Type | Purpose | Pinout |
|---|---|---|---|
| `J1` | M12 D-code (female, 4-pin) | 24 V power input A | `1`: VIN+; `2`: VIN−; `3`: shield; `4`: NC |
| `J2` | M12 D-code (female, 4-pin) | 24 V power input B (redundant) | same as J1 |
| `J3` | M12 X-code (female, 8-pin) | TSN Ethernet A to T-ECU/S | 1000BASE-T pairs 1/2, 3/4; shield on case |
| `J4` | M12 X-code (female, 8-pin) | TSN Ethernet B to T-ECU/S | same as J3 |
| `J5` | M12 T-code (female, 4-pin) | CAN-FD to mmWave radar | `1`: +5V_radar; `2`: CAN_H; `3`: GND; `4`: CAN_L |
| `J6` | M12 X-code (female, 8-pin) | 1000BASE-T + 12V-PoE-class to LIDAR | TSN pairs + 12 V power contacts |
| `J7` | M12 A-code × 2 (female, 4-pin each) | Ultrasonic transducer A bank (2 transducers — upper-left + upper-right) | `1`: DRIVE+; `2`: DRIVE−; `3`: ECHO+; `4`: ECHO− |
| `J8` | M12 A-code × 2 (female, 4-pin each) | Ultrasonic transducer B bank (2 transducers — lower-left + lower-right) | same as J7 |
| `J9` | 30-pin FFC (0.5 mm pitch) | MIPI-CSI to stereo camera pair | 2-lane MIPI + power; internal to nose |
| `J10` | USB-C | Debug + OTA console on CM5 | USB 2.0 data; shell grounded |
| `J11` | 10-pin 0.1" header | JTAG / SWD to RP2350 A | ARM Cortex-M33 debug |
| `J12` | 10-pin 0.1" header | JTAG / SWD to RP2350 B | same as J11 |

## Field-wiring checklist

**Ultrasonic transducer mounting.** Four transducers per nose,
one in each quadrant of the obstacle field:

| Transducer | Mount | M12 | Aim |
|---|---|---|---|
| `US_UL` | Upper-left of nose cowl | J7, pair 1 | 10° above horizontal, left of centreline |
| `US_UR` | Upper-right of nose cowl | J7, pair 2 | 10° above horizontal, right of centreline |
| `US_LL` | Lower-left of nose cowl | J8, pair 1 | 5° below horizontal, left of centreline |
| `US_LR` | Lower-right of nose cowl | J8, pair 2 | 5° below horizontal, right of centreline |

Channels overlap; any single transducer failure is tolerated
by the evaluator as a stale channel (fires `UltrasonicStale`
→ EB, which is conservative). The full four-channel coverage
is needed for the `Clear` verdict.

**Radar mount.** Single TI AWR1843 module centred on the nose
cowl, 3 m above rail head, pointed along the centreline with
zero roll. Mounting bracket is part of the nose-cone assembly
drawing; vendor module ships with a standard M12 T-code
interface so the field cabling is off-the-shelf.

**LIDAR mount.** Below the radar, centred, tilted 2° down for
ground-plane detection. Protective hood for dust-storm
sheltering — the hood adds a small window obstruction but
matches the Middle East deployment climate where LIDAR point
density would otherwise collapse during a haboob.

**Stereo cameras.** Below the LIDAR, 500 mm baseline, both
cameras locked in a rigid bar to preserve calibration. Angle
matches radar (zero roll, zero tilt).

## Cable lengths + derating

| Interface | Max cable length | Notes |
|---|---|---|
| 24 V power | 3 m | From trainset aux bus entry to J1/J2; 1.5 mm² wire |
| TSN Ethernet A/B | 5 m | To T-ECU/S; Cat 6a minimum, shielded |
| CAN-FD to radar | 1 m | Radar is on the nose cowl; short run |
| LIDAR Ethernet | 1 m | LIDAR is on the nose cowl; short run |
| Ultrasonic | 0.5 m | Transducers are on the nose cowl; trace to AFE kept short |
| MIPI-CSI | 150 mm | FFC only; inside the nose cavity |

## Nose-cone integration

The T-OBS baseboard mounts to the backplate of the nose-cone
assembly with M4 captive nuts on a 180 × 120 mm bolt pattern.
Sensors mount directly to the cone's inner frame; cabling
between sensor and baseboard is < 500 mm throughout.

The nose-cone panel itself is RF-transparent (polycarbonate
+ UV stabiliser, 8 mm thick) — radar and ultrasonic see
through it without meaningful attenuation. The cone is a
service item with a 10-year replacement interval under the
RFC 0013 M5 30-day inspection cycle.
