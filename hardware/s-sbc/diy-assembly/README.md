# S-SBC DIY assembly

Station / depot SBC (RFC 0007 §7). Non-safety; already designed
around commodity parts.

## Bill of materials

The S-SBC v2-spec already uses the official RPi CM5 IO Board
as its baseboard — the custom and DIY paths converge for this
host class.

| # | Part | SKU | Qty | Unit (USD) | Subtotal |
|---|---|---|---|---|---|
| 1 | Raspberry Pi CM5 8 GB Lite | SC1124 | 1 | 85 | 85 |
| 2 | RPi CM5 IO Board | SC1125 | 1 | 35 | 35 |
| 3 | microSD 32 GB | commodity | 1 | 10 | 10 |
| 4 | Adafruit ATECC608B (optional; only for PSD signing) | Adafruit 4374 | 1 | 4 | 4 |
| 5 | Station cabinet, 19" 1U rackmount (indoor) | commodity | 1 | 25 | 25 |

**Subtotal: ~$159 per S-SBC.**

For outdoor TVM kiosks where ambient exceeds the RPi OT3 range,
swap the RPi CM5 for the Radxa CM5 industrial-temp (drop-in
SO-DIMM replacement) — adds ~$70.

## What it runs

`osr-psd`, `osr-station-scada`, `osr-pis-station`, `osr-afc`,
`osr-tvm`, `osr-historian` (regional), `osr-cbm-backend`
(depot-adjacent S-SBCs).

## Why no custom PCB is planned

Station-side functions are non-safety and all interfaces are
commodity (USB for TVM + fare-gate, HDMI for PIS, 1000BASE-T
for backhaul). Nothing demands custom silicon.

## Commissioning

```bash
sudo osr-selftest --role s-sbc
```

Exercises PSD-controller state machine, AFC HMAC paths, TVM
communication, PIS rendering.
