# T-OBS v2 — safety-critical nets

Same 2oo2 composite fail-safe architecture as T-ECU/S: two
RP2350 channels cross-check over SPI, both must agree through
an external AND-gate relay stage to assert (or release) the
brake-demand line that feeds into the T-ECU/S brake-fault
chain.

## Net list

| Net | Driven by | Destination | Guarantee |
|---|---|---|---|
| `OBS_CLEAR_A` | RP2350 A GPIO | Input A of AND-gate K1 | Only asserted when channel A has evaluated `Clear` or `RestrictedSpeed` on the current tick; ≥ 1.5 mm clearance from `*_B` |
| `OBS_CLEAR_B` | RP2350 B GPIO | Input B of AND-gate K1 | Same semantics on channel B |
| `OBS_BRAKE_DEMAND` | Output of AND-gate K1 (inverted) | T-ECU/S brake-demand bus input | Asserted *if either channel disagrees* — fail-restrictive; feeds T-ECU/S own 2oo2 EB relay |
| `CROSS_CHECK_MOSI` | RP2350 A SPI1 | ADuM1401 isolator input A | Galvanically isolated cross-check; SPI @ 1 MHz |
| `CROSS_CHECK_MISO` | ADuM1401 isolator output B | RP2350 B SPI1 | Return path for the cross-check |
| `WATCHDOG_A` | RP2350 A heartbeat GPIO | TPS3701 WD A input | ≥ 10 Hz pulse; missing → local reset of channel A |
| `WATCHDOG_B` | RP2350 B heartbeat GPIO | TPS3701 WD B input | Same on channel B |
| `OBS_RESET` | TPS3701 global reset | Both RP2350s + CM5 | Asserts if both watchdogs fail; concurrent with brake-demand asserted via the AND gate |
| `SAFETY_3V3_A` | LDO TLV755-A | RP2350 A VDD | Monitored by TPS3701; undervolt → channel A reset |
| `SAFETY_3V3_B` | LDO TLV755-B | RP2350 B VDD | Same on channel B |
| `US_ECHO_A[0..3]` | Ultrasonic AFE A bank | ADC_A bank → RP2350 A | 4-channel analog-in, routed on inner layer with GND sandwich |
| `US_ECHO_B[0..3]` | Ultrasonic AFE B bank | ADC_B bank → RP2350 B | Same — independent AFE + ADC per channel (not shared with A) |
| `RADAR_CAN_H/L` | TCAN1462 bus | RP2350 A + RP2350 B + CM5 | CAN-FD shared bus; each channel independently parses radar detections |
| `LIDAR_ETH` | LIDAR KSZ9031 | CM5 primary; detection summaries forwarded to A + B over TSN | 1000BASE-T — off the safety-critical path at the PHY level (safety evaluator sees only the post-fusion detection list) |

## Routing rules

### Clearance

Any two nets that end in `_A` vs `_B` must have ≥ 1.5 mm PCB
clearance. This prevents a single solder-short from defeating
the 2oo2 argument.

### Ultrasonic front-end independence

The four ultrasonic channels use **independent AFE + ADC per
channel per side** (A and B each see 4 echo traces through
their own AD7091 ADC). No ADC is shared between A and B. This
keeps the ultrasonic safety belt as two truly-independent
evaluators, matching the 2oo2 claim.

### Radar CAN-FD multidrop

The radar CAN-FD bus is shared by A, B, and CM5 — which is
permitted because CAN is a broadcast bus with per-receiver
CRC. Each channel independently receives and validates the
radar frames; disagreement in the parsed detection list
between A and B feeds back through the cross-check and raises
the `PeerDisagreement` verdict.

### LIDAR Ethernet to CM5 only

LIDAR point clouds land on CM5 for fusion and classification.
CM5 emits a summary detection list (≤ 4 entries per tick) back
to A + B via the TSN A/B ring. The RP2350s do not talk to the
LIDAR directly — the path is not safety-primary, and a LIDAR
PHY fault shows up as a stale-detection-list on A + B which
fires the O4b verdict (RestrictedSpeed).

### Crossing

Where `*_A` and `*_B` must cross (unavoidable on 4-layer), a
GND guard trace on the adjacent layer keeps capacitive
coupling below 2 pF.

### Via placement

No via for `*_A` placed within 1 mm of any via for `*_B`.
Separate via arrays, one per side.

## 2oo2 AND-gate stage

Same passive-relay design as T-ECU/S K1. Two Panasonic DS-series
24 VDC SPDT relays in series — both must energise to release
the `OBS_BRAKE_DEMAND` line (inverted polarity: energised =
Clear, de-energised = demand EB).

```
  OBS_CLEAR_A ─►│relay K1a│──┐
                │(SPDT NO)│  │
                │         │  ├──► OBS_BRAKE_DEMAND
  OBS_CLEAR_B ─►│relay K1b│──┘         (inverted)
                │(SPDT NO)│
                └─────────┘
```

Both K1a AND K1b must hold closed to release the brake demand.
If either input drops, `OBS_BRAKE_DEMAND` is asserted, T-ECU/S
sees brake-demand on its 2oo2 AND-gate input, and commands EB
through its own K1/K2 stage.

**Why two relays, not a logic-gate IC?** Same argument as
T-ECU/S safety-nets §2oo2 — a logic-gate IC is a single-point
failure; two mechanical relays need both coils to simultaneously
weld-fuse, orders of magnitude less likely.

## Boot validation

1. Both RP2350s boot with `OBS_CLEAR_A = OBS_CLEAR_B = 0`
   (de-asserted, brake demand on).
2. After self-test (ultrasonic ping check, radar heartbeat,
   LIDAR ping reply, ATECC608 handshake), each channel raises
   its `OBS_CLEAR` line when its evaluator has produced a
   first valid `Clear` verdict.
3. If either self-test fails, that channel's `OBS_CLEAR` stays
   low and the AND gate keeps brake demand asserted — trainset
   remains immobile until recovery via the locked keyswitch.

This means any half-failed T-OBS module **always fails safe**:
no `Clear` on one side means no release from the AND gate,
means brake-demand asserted, means T-ECU/S commands EB.

## Proof obligation for the KiCad designer

The v2 schematic must preserve every safety net in the table
above. A DRC pass before gerber export must verify:

1. Every `*_A` and `*_B` pair has ≥ 1.5 mm clearance.
2. Ultrasonic AFE + ADC are duplicated per channel (no
   single AFE feeds both A and B).
3. CAN-FD bus termination on the radar path is present and
   correct (120 Ω at each bus end).
4. The AND-gate stage uses two physically separate relays with
   independent coils.
5. Both watchdog inputs of the TPS3701 have independent traces
   to their respective RP2350s.
6. The fail-restrictive logic (`OBS_CLEAR` = 0 → brake demand
   asserted) is traceable end-to-end.

DRC output pasted into `deviations-log.md` as the safety-case
evidence for this board revision.
