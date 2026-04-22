# T-ECU/S v2 — CM5 SODIMM pinout on the baseboard

The CM5 is the non-safety application processor (RFC 0007 §4.2).
It hosts TCN-E, event recorder, GNSS, NFC balise reader — none
of these are on the safety-actuator path.

CM5 uses the Raspberry Pi CM5 SODIMM-like connector (260-pin
DDR4-style layout; Raspberry Pi datasheet for pin assignment).
This spec lists only the baseboard-side functions.

## Signals used

| CM5 pin function | Baseboard function | Notes |
|---|---|---|
| `GIG_ETHERNET` × 2 | To KSZ9031 Ethernet PHYs (U70, U71) via RGMII | TSN TCN-E A + TCN-E B |
| `PCIE_0` | Reserved for on-board diagnostic use | Not populated in revision A |
| `USB2_PORT0` | Debug port → USB-C connector J20 | For bench bringup |
| `USB3_PORT0` | Reserved | Unused |
| `GPIO2 / GPIO3` | I²C1 to ATECC608B A + B (via I²C switch for channel select) | Non-safety use — CM5 can read device IDs but cannot sign; all signing is done on the RP2350 side |
| `GPIO14 / GPIO15` | UART to u-blox NEO-F10N GNSS | |
| `SPI0 (GPIO10 / 11 / 9 / 8)` | To PN5180 NFC balise reader | |
| `SPI6` | To RP2350 A for one-way safety → app data stream | RP2350 is master; CM5 is slave; the net is also isolated via a separate ADuM1401 so a CM5 fault can't inject onto the safety SPI. |
| `PWM0` | LED bar graph on cab front (status) | |
| `SD_CARD` | eMMC-backed — use built-in eMMC on CM5, not external card | |
| `USB_BOOT` | Tied to a test pad for rpiboot recovery | |

## Unused CM5 pins

Per RFC 0007 §4.2 every unused CM5 pin is either: pulled to
the safe state via a 10 kΩ resistor (for pins with default
function), or left floating (for those datasheet says "may
float"). The v2 PCB designer follows the CM5 datasheet's
unused-pin handling table.

## One-way safety→app link (RP2350 A → CM5 via SPI6)

The safety→app data path is **strictly one-way**: RP2350 A is
the SPI master, CM5 is the slave. CM5 cannot initiate a
transfer; it can only consume what RP2350 A publishes.

Physical isolation via a second ADuM1401 (U32) ensures a CM5
brown-out / latch-up / runaway firmware cannot corrupt either
RP2350's behaviour — the isolator's output side is driven by
the RP2350, and the input side (to CM5) is high-Z from the
RP2350 perspective.

This is the RFC 0005 §13 "SIL-4 must not depend on SIL-2 at
runtime" implementation at the physical level.

## CM5 power-up sequence

1. Baseboard power-on: 5 V + 3.3 V rails stabilise.
2. Supervisor IC (U95) releases reset to RP2350 A + B.
3. RP2350 A + B boot (2 ms) and run self-test.
4. After self-test passes, RP2350 A toggles an enable pin that
   powers up the CM5 (via the CM5's `EN` pin wired to a high-
   side switch).
5. CM5 boots (Debian, ~60 s).

If RP2350 self-test fails, the CM5 never powers up — safety
partition validates first.

## CM5 reset logic

CM5 reset is gated by:
- Main supervisor reset (any rail undervolt).
- RP2350 A watchdog: if A loses heartbeat, CM5 gets a soft
  reset (so that post-reset the app side can't accept stale
  data from a crashed A channel).

CM5 cannot reset either RP2350 — deliberate, matches the
one-way architecture.

## External connections from CM5 side

- J20: USB-C device (bench bring-up).
- J21: HDMI (typically unused in cabinet; can be populated for
  depot troubleshooting).
- J22: M.2 slot (NVMe event recorder, per RFC 0007 §5 peripheral
  list — the event recorder NVMe actually sits on the T-ECU/A
  board; on T-ECU/S the M.2 slot is reserved unused in v2).
- J23: GNSS antenna (SMA to u-blox NEO-F10N).
- J24: NFC antenna (matched for 13.56 MHz; coil details per
  PN5180 datasheet).
