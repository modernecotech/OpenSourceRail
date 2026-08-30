# T-ECU/S v2 — safety-critical nets

The 2oo2 composite fail-safe architecture from RFC 0007 §4.1
lands on the PCB as a set of explicit nets + a passive logic
block (the AND-gate relay stage). This doc lists every
safety-critical net, what drives it, where it goes, and what
guarantees the PCB layout must provide.

## Net list

| Net | Driven by | Destination | Guarantee |
|---|---|---|---|
| `EB_DRIVE_A` | RP2350 A GPIO | Input A of AND-gate K1 | Never shorted to `EB_DRIVE_B`; ≥ 1.5 mm clearance |
| `EB_DRIVE_B` | RP2350 B GPIO | Input B of AND-gate K1 | Same |
| `EB_RELAY_COIL` | Output of AND-gate K1 | EB relay K1 coil | Drops EB relay when either drive goes low |
| `TRACTION_CUT_A` | RP2350 A | Input A of AND-gate K2 | Same class as EB |
| `TRACTION_CUT_B` | RP2350 B | Input B of AND-gate K2 | Same |
| `TRACTION_CUT_COIL` | K2 output | Traction-cut relay | |
| `CROSS_CHECK_MOSI` | RP2350 A SPI | ADuM1401 isolator input A | Galvanic-isolated; routed through the isolator chip |
| `CROSS_CHECK_MISO` | ADuM1401 isolator output B | RP2350 B SPI | |
| `WATCHDOG_A` | RP2350 A heartbeat GPIO | Supervisor TPS3701 WD A input | Pulse at ≥ 10 Hz; missing → TPS3701 resets RP2350 A |
| `WATCHDOG_B` | RP2350 B heartbeat GPIO | Supervisor TPS3701 WD B input | Same |
| `WATCHDOG_RESET_OUT` | TPS3701 | Global reset net (both RP2350s + CM5) | Drops all processors if *both* watchdogs fail |
| `SAFETY_3V3_A` | LDO TLV755-A output | RP2350 A VDD | Monitored by TPS3701; undervolt → A reset |
| `SAFETY_3V3_B` | LDO TLV755-B output | RP2350 B VDD | Same |

## Routing rules

### Clearance

Any two nets from the table above that end in `_A` vs `_B`
must have ≥ 1.5 mm PCB clearance. This prevents a single
solder-short from defeating the 2oo2 argument.

### Crossing

If `*_A` and `*_B` must cross (unavoidable on a 4-layer
stackup), the crossing point uses a guard trace (GND fill) on
adjacent layers to minimise capacitive coupling.

### Via placement

No via for `*_A` placed within 1 mm of any via for `*_B`.
Separate via arrays.

### Shared return

Both `*_A` and `*_B` nets use the solid GND plane — sharing
return is acceptable and necessary (only one GND net on the
board). The guarantee is symmetry, not isolation.

## 2oo2 AND-gate stage

Each safety output (EB, traction-cut, fire suppress) is gated
through an external 2oo2 AND relay stage:

```
  EB_DRIVE_A ────►│relay K1a│────┐
                  │(SPDT NO) │   │
                  │          │   ├────► EB_RELAY_COIL
  EB_DRIVE_B ────►│relay K1b│────┘
                  │(SPDT NO) │
                  └──────────┘
```

Both K1a AND K1b energise to close the circuit. If either
input drops, the output opens. Series connection, no sneak
paths.

**Why two relays, not a logic-gate IC?** A logic-gate IC is a
single-point failure (shorted output, stuck-at-1, upset).
Two relays are mechanically redundant — you'd need both coils
to weld-fuse simultaneously, orders of magnitude less likely.

### Relay choice

- **Part:** Panasonic DS-series 24 VDC coil SPDT.
- **Coil:** 24 V, 150 mA pull-in, 10 mA hold.
- **Contact:** 2 A at 30 VDC DC-rated (AgSnO2 contacts).
- **Mechanical life:** 10M cycles (per datasheet).
- **Electrical life:** 100K cycles at rated load (per datasheet).
- **Shock / vibration:** EN 50155 compliant.

### Fail modes

| Failure | Detected by | Effect |
|---|---|---|
| K1a coil open | Supervisor monitors output voltage; if `EB_RELAY_COIL` is low while both drives are high → alarm | EB stays held (fail-safe apply because the relay drops open) |
| K1a welded contact | Detected only on next open-close cycle; integrated into RFC 0013 D1.2 brake test | Pre-service test catches — trainset returns to maintenance |
| K1b coil open | Same as K1a | Same |
| K1b welded | Same | Same |
| Both K1a+K1b welded | Not detected directly by driver; CBM schedule (RFC 0013 M5) replaces relay at N cycles | **v2 addendum:** supervisor monitors drive-vs-coil correlation; any drive change that does NOT produce a coil change within 50 ms raises amber fault. |
| K1a contact stuck open | Coil energises but circuit doesn't close | Output stays open → EB applied (fail-safe) |

## Hardware watchdog

A tri-input TPS3701 supervisor monitors:
- `SAFETY_3V3_A` — must stay in the ±5 % window.
- `SAFETY_3V3_B` — same.
- `WATCHDOG_A` + `WATCHDOG_B` — both must pulse.

Trip logic:
- Either undervolt OR either watchdog fail → reset that
  channel only (not both).
- Both watchdogs fail → hard reset everything + drop EB
  relay via direct drive to `EB_RELAY_COIL` independent of
  the AND-gate stage.

## Boot validation

On power-on:
1. Both RP2350s boot with `EB_DRIVE_A = EB_DRIVE_B = 0`
   (drives default low).
2. After self-test, each RP2350 raises its drive to 1 (brake
   released, ready for operation).
3. If either self-test fails, that channel's drive stays at 0,
   and the AND gate keeps EB applied.

This means a half-failed board **always fails safe** — the
failed channel's drive is low, so the AND gate output is low,
so the EB relay is dropped.

## Proof obligation for the KiCad designer

The v2 schematic must preserve every safety net in the table
above. A DRC (design rule check) pass before gerber export
must check:

1. Every `*_A` and `*_B` pair has ≥ 1.5 mm clearance.
2. No net name collision (typos in the schematic translating
   the safety structure to layout).
3. The AND-gate stage uses two physically separate relays.
4. Both watchdog inputs of the supervisor have independent
   traces to their respective RP2350s.
5. The fail-restrictive logic (drive-low = brake-apply) is
   traceable end-to-end.

DRC output pasted into `deviations-log.md` as the safety-
case evidence for this board revision.
