# T-ECU/A DIY assembly

Application-tier ECU (RFC 0007 §5). Single-redundant (not 2oo2).
One T-ECU/A per cab end × 2 per trainset.

## Bill of materials

| # | Part | SKU | Qty | Unit (USD) | Subtotal |
|---|---|---|---|---|---|
| 1 | Raspberry Pi CM5 8 GB Lite | SC1124 | 1 | 85 | 85 |
| 2 | RPi CM5 IO Board | SC1125 | 1 | 35 | 35 |
| 3 | Waveshare 2-CH CAN-FD HAT (HVAC + lighting buses) | 2-CH-CAN-FD-HAT | 1 | 28 | 28 |
| 4 | Quectel RM500Q-GL M.2 5G modem | RM500Q-GL | 1 | 80 | 80 |
| 5 | Quectel antennas 2×4 MIMO | YQ500-B7B | 1 | 35 | 35 |
| 6 | Waveshare SX1262 LoRa HAT (TRG-2 backup radio) | SX1262-LoRa-HAT | 1 | 18 | 18 |
| 7 | Adafruit ATECC608B trust anchor | Adafruit 4374 | 1 | 4 | 4 |
| 8 | UCTRONICS DIN rail Pi enclosure | U6277 | 1 | 25 | 25 |
| 9 | Mean Well HDR-60-24 DIN PSU | HDR-60-24 | 1 | 35 | 35 |
| 10 | Phoenix terminal block | UT 2.5 DIN | 1 | 8 | 8 |

**Subtotal: ~$353 per T-ECU/A.**

## What it runs

Per RFC 0005 §4.1 / §4.2: `osr-ato`, `osr-tcms`,
`osr-event-recorder`, `osr-tcn`, `osr-regen`, `osr-aux-power`,
`osr-hvac`, `osr-lighting`, `osr-pis-onboard`, `osr-hot-axle`,
`osr-cbm-onboard`, `osr-t2g`.

With `--features goa2-cab` it additionally pulls `osr-dmi` +
`osr-vigilance` for legacy cabbed fleets (RFC 0015 §10.2).

## Key point

**T-ECU/A is not safety-critical.** A failure degrades comfort
(HVAC, lighting, PIS), diagnostics visibility, or communications
availability. The T-ECU/S + T-OBS + brake relay chain stays
operational without it, so this is the simplest DIY host class:
one Pi, three HATs, one enclosure.

## Commissioning

```bash
sudo osr-selftest --role t-ecu-a
```

Exercises radios + CAN buses + ATECC608B + the application
crate set.
