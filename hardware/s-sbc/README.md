# S-SBC — Station / Depot

**Role:** Host for [`osr-psd`](../../crates/osr-psd/),
[`osr-pis-station`](../../crates/osr-pis-station/),
[`osr-station-scada`](../../crates/osr-station-scada/),
[`osr-afc`](../../crates/osr-afc/), [`osr-tvm`](../../crates/osr-tvm/).

Indoor deployment; no rail-industry environmental rating required.

## SoC + baseboard

Raspberry Pi CM5 on a commodity carrier (e.g. Waveshare CM5-IO).
**No custom baseboard.** The station enclosure carries the I/O.

This is a deliberate deviation from the other classes: sheltered
indoor environments don't warrant the custom engineering, and every
hour saved on baseboard bring-up goes into the passenger-facing work
that actually differentiates an OpenSourceRail deployment.

See [RFC 0007 §7](../../docs/rfcs/0007-hardware-reference-designs.md#7-class-s-sbc-station--depot)
for the commodity-carrier rationale.

## Peripherals (from the commodity carrier)

- 2 × Gigabit Ethernet (station LAN + PSD/gate network)
- 4 × USB 3.0 (QR scanner, NFC reader, receipt printer, TVM bill
  acceptor)
- HDMI for passenger-facing display
- USB-C console
- ATECC608 add-on over I²C (the only custom piece — a small 30 × 20
  mm PCB that plugs onto the CM5 I/O header)

## Target BOM

~€130 total — CM5 module + carrier + small SE add-on.

## Status

Pilot / DIY track: the station-side software stack already runs on
stock Waveshare carriers in the development lab. Integration evidence
is still pending.

Custom-board track: usually unnecessary for S-SBC. The only custom
piece is the small ATECC608 add-on (two ICs + passives), tracked as a
v2 deliverable alongside the other classes for consistency.
