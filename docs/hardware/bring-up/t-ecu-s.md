# T-ECU/S bring-up — two Raspberry Pi Pico 2 boards in 2oo2

**Goal:** validate that the [RFC 0007 §4](../../rfcs/0007-hardware-reference-designs.md#4-class-t-ecus-train-safety-kernel)
2oo2 safety architecture works on real silicon before we draw the
custom baseboard. After this runbook, a pair of Pico 2 boards
runs `osr-atp` + `osr-brake` + `osr-odometry` in composite
fail-safe mode with per-tick SPI cross-check.

## Dev kits + parts

| Part | Qty | Notes |
|---|---|---|
| Raspberry Pi Pico 2 | 2 | Each carries one RP2350 — the safety MCU. |
| ST-Link V3 or Pico probe | 2 | SWD debugger per Pico. |
| Breadboard + jumpers | 1 set | SPI cross-link + shared inputs. |
| 3-phase quadrature encoder sim | 1 | Can be an Arduino-generated square-wave pair. |
| BMI088 breakout | 1 | Feeds both Picos via separate SPI chip selects. |
| 24 VDC bench supply | 1 | Via an ADuM isolator IC for input simulation. |
| Relay 2oo2 stage (optional) | 1 | Two SPDT relays in AND — validates the final actuator gating. |

## Steps

### S1 — Build the harness

Wire each Pico to:

- **Shared inputs** (both Picos read the same signal, on separate
  pins): one pulse input (sim wheel tach), one digital input (sim
  emergency plunger), IMU chip-select line.
- **Private SPI cross-check link:** Pico-A SPI0 ↔ Pico-B SPI0
  (CLK, MOSI, MISO, CS). ~1 MHz clock.
- **Debug UART:** each Pico's UART0 to a USB-serial adapter for
  log capture.

Write the topology into the bring-up report at step R0.

### S2 — Flash the Pico test firmware

From the workspace:

```bash
cargo build --release --target thumbv8m.main-none-eabihf \
  --bin tecus-bringup
```

(The `tecus-bringup` binary is a dev-only test harness in
`deployments/devkit/tecus-bringup/` — planned for landing
alongside this runbook; for v1 of this document the binary is a
future session's deliverable.)

Flash each Pico with the same binary via SWD. Both Picos boot
into the identical code path; 2oo2 runs at identical-software
redundancy.

**Expected:** green LED blinks at 1 Hz on both Picos. Red LED off.

**FAIL-HW** if either Pico fails to boot: replace Pico.
**FAIL-SW** if the binary fails to flash: check toolchain pin.

### S3 — Verify the SPI cross-check

Connect a logic analyser between the two Picos on the SPI lines.

1. Power both Picos.
2. In the analyser, expect a message exchange every 10 ms:
   frame format is `[seq: u32][osr_atp_output: u32][
   osr_brake_output: u32][crc16: u16]`.
3. Ground-truth: both messages must match byte-for-byte after
   the first 5 exchanges.

**PASS:** 100 consecutive 10 ms frames match.

**FAIL-SW** if frames diverge: inspect the `tecus-bringup`
log output via UART; there will be a divergence report.

### S4 — Simulate an input disagreement

On the harness, break one of the shared input lines — e.g. cut
the wire to Pico-B's wheel-tach input.

**Expected within 100 ms:** both Picos:
1. Halt their computed brake output (emit `BrakeCommand::Emergency`).
2. Drop their relay-drive outputs.
3. The relay 2oo2 stage (if wired) opens, releasing the test
   brake pressure.
4. Both Picos' red LEDs solid.

**PASS:** emergency-brake actuation within 100 ms of the input
disagreement.

**FAIL-SW** if either Pico keeps driving its output: bug in the
cross-check invariant — file against `osr-atp` + `osr-brake`.

### S5 — Verify the wheel-tach input

Drive the shared pulse input at 500 Hz (≈ 4.2 m/s with a
410 pulses/m calibration).

**Expected:** UART log from both Picos shows
`odom.speed_mmps ≈ 4200`; the two speeds must match within 50 mm/s.

**FAIL-SW** if speeds diverge > 50 mm/s with identical input:
likely a timing-quantization bug — file against `osr-odometry`.

### S6 — Verify the emergency plunger

Assert the sim plunger input.

**Expected:** both Picos immediately command `BrakeCommand::Emergency`
on their output pins. The 2oo2 AND gate in the harness sees both
high → drives the relay drop → test brake applies.

**PASS:** relay drop latched within 50 ms.

### S7 — CM5 handshake (optional)

If an RPi CM5 IO Board is also present, wire an SPI-slave link
between Pico-A and the CM5. Boot the CM5 with the app-side
bring-up test binary.

**Expected:** CM5 receives the same per-tick cross-check messages
over SPI and logs them in JSON to `/var/log/osr/ecus.log`. This
proves the one-way safety → app data path
([RFC 0007 §4.2](../../rfcs/0007-hardware-reference-designs.md#42-soc-picks)).

### S8 — Performance envelope

Run the 2oo2 cross-check harness for 1 hour. Measure:

- Cross-check message rate: must stay at 100 Hz ± 1 Hz.
- Missed frames: 0.
- Cross-check mismatches: 0.
- Average tick jitter: ≤ 1 ms.

A 1-hour clean run is the "boot certifiable" bar for the v2
baseboard proceed-gate.

## Bring-up report template

```markdown
# T-ECU/S bring-up report

- Runbook commit: <hash>
- Date: <YYYY-MM-DD>
- Engineer: <name>
- Pico A serial: <nnn>
- Pico B serial: <nnn>

## Results
| Step | Status |
|---|---|
| S1 (harness) | PASS / FAIL-\* |
| S2 (flash)   | PASS / FAIL-\* |
| S3 (cross-check) | PASS / FAIL-\* |
| S4 (input disagreement) | PASS / FAIL-\* |
| S5 (wheel tach) | PASS / FAIL-\* |
| S6 (plunger) | PASS / FAIL-\* |
| S7 (CM5 handshake) | PASS / FAIL-\* / N-A |
| S8 (1 h run) | PASS / FAIL-\* |

## Notes
<observations, anomalies, links to logs>
```
