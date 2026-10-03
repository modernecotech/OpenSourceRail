# T-ECU-S hardware permission and fault contract

Status: requirements for a board designer; schematic, safety analysis and bench evidence remain open. Two evaluator channels are a reference architecture, not proof of a safety integrity level or independent hardware.

| Function | Required behaviour | Evidence before release |
|---|---|---|
| Channel A/B permission outputs | Default low at boot/reset; valid fresh agreement and local health required for high | GPIO startup, stuck-high/low and timeout traces |
| Independent heartbeat watchdog A/B | Directly inhibit the respective hardware driver on missing or invalid heartbeat | Window/deadline design; early/late/stuck tests |
| Voltage monitoring A/B | Detect local rail UV/OV; inhibit local output and reset as designed | Threshold, hysteresis, delay and transient tests |
| Peer cross-check | Isolated SPI, age/sequence/integrity checks; disagreement restricts permission | CRC/age/babble/open/short tests |
| Series output contacts | Both must close for permission; opening either removes permission | Actual series wiring, driver fault and welded-contact tests |
| Contact feedback | Detect discrepancy before movement and in periodic proof tests | Diagnostic coverage and proof-test interval analysis |
| Brake/traction interface | End-to-end fail-restrictive behaviour established with supplier actuator | Polarity, load, loss-of-power and recovery truth table |

**TPS3701 has no heartbeat watchdog input.** It is a voltage window detector and may be considered for voltage sensing only. Specify separate external watchdog functions for A and B, with channel-local reset/inhibition. A global reset, if used, cannot be the only safety output control. See [TI's specification](https://www.ti.com/product/TPS3701).

No relay part number, coil current, lifetime, EN 50155 qualification or failure-rate claim is released. A commodity SSR board is a bench simulated-load interface only. Select contacts and drivers from actual load and failure requirements, add suppression without unacceptable release delay, and diagnose welded contacts. The previous claim that two relays always fail safe is withdrawn: common power/ground, shared sensors, fused application data, wiring shorts, welded contacts and common firmware require explicit analysis.

Physical segregation, clearance/creepage, connectors, routing and insulation must follow the voltage/environment and fault study. A 1.5 mm layout target or successful KiCad DRC cannot establish independence, EMC or a safety case. Complete FMEA/common-cause analysis, fault injection, output proof tests and the board-specific release checklist.

The [bench integration source](../../../reference-integration.json) defines a Pico 2 allocation and reference output semantics. Custom RP2350A/B pins require a package-specific allocation; no native CAN-FD or Ethernet/RMII peripheral is assumed.
