# DIY parts catalogue

Every SKU used across the five host classes, consolidated for
sourcing in bulk. Every item has ≥ 2 distributors so supply-
chain disruption at one source does not block a deployment.

Prices are 2026 retail in USD, at quantities of 1–10 units.
Bulk (50+) pricing typically 20–40 % lower per unit.

## Compute modules

| Part | SKU | Distributor 1 | Distributor 2 | Retail (USD) |
|---|---|---|---|---|
| Raspberry Pi Pico 2 | SC1630 | Official Pi Foundation | Mouser, DigiKey | $5 |
| Raspberry Pi CM5 8 GB Lite | SC1124 | Official Pi Foundation | Mouser | $85 |
| Raspberry Pi CM5 IO Board | SC1125 | Official Pi Foundation | Pimoroni | $35 |
| Radxa CM5 industrial-temp | rock-cm5-industrial | Radxa store | ALLNET china | $110 |
| Radxa CM5 IO Board | rock-cm5-io | Radxa store | ALLNET china | $40 |

## Communications HATs

| Part | SKU | Distributor 1 | Distributor 2 | Retail (USD) |
|---|---|---|---|---|
| Waveshare 2-CH CAN-FD HAT | 2-CH-CAN-FD-HAT | Waveshare | AliExpress-commodity | $28 |
| Waveshare SX1262 LoRa HAT (868 / 915 MHz) | SX1262-LoRa-HAT | Waveshare | Mouser | $18 |
| Quectel RM500Q-GL 5G modem (M.2) | RM500Q-GL | DigiKey | AliExpress | $80 |
| Quectel antennas (2 × 4 MIMO) | YQ500-B7B | DigiKey | Mouser | $35 / set |

## SIL-4 actuator path

| Part | SKU | Distributor 1 | Distributor 2 | Retail (USD) |
|---|---|---|---|---|
| 8-channel 24 V relay board, opto-isolated | SainSmart SSR-8DC24 | SainSmart | Amazon / AliExpress | $12 |
| Adafruit USB isolator | Adafruit 2107 | Adafruit | Mouser | $25 |
| SparkFun ADUM1401 isolator breakout | BOB-14712 | SparkFun | DigiKey | $25 |
| Adafruit ATECC608B breakout | Adafruit 4374 | Adafruit | DigiKey | $4 |
| ADS1115 16-bit ADC breakout | Adafruit 1085 | Adafruit | DigiKey | $15 |
| MCP23017 I/O expander breakout | Adafruit 732 | Adafruit | DigiKey | $7 |

## Obstacle-detect sensors (RFC 0015)

| Part | SKU | Distributor 1 | Distributor 2 | Retail (USD) |
|---|---|---|---|---|
| HC-SR04 ultrasonic transceiver (dev grade) | HC-SR04 | AliExpress | Amazon | $2 each |
| Murata MA40H1S-R (production grade) | MA40H1S-R | Mouser | DigiKey | $25 each |
| TI AWR1843BOOST 77 GHz radar eval | AWR1843BOOST | ti.com | Mouser | $500 |
| Livox HAP solid-state LIDAR | LIVOX-HAP | Livox direct | B&H Photo | $1500 |
| Raspberry Pi Camera Module 3 | SC0872 | Official Pi Foundation | Mouser | $35 |
| ArduCam stereo camera bracket | B0203 | ArduCam | Amazon | $18 |

## Wayside-intrusion sensors (RFC 0016)

| Part | SKU | Distributor 1 | Distributor 2 | Retail (USD) |
|---|---|---|---|---|
| Senstar FlexZone fence-line (per 100 m) | FlexZone-100 | Senstar dealers | — | $300 |
| Livox Mid-360 360° LIDAR | LIVOX-MID-360 | Livox direct | — | $900 |
| TI AWR1843BOOST (ROW-mounted) | AWR1843BOOST | ti.com | Mouser | $500 |
| Reolink RLC-810A 4 K IP camera | RLC-810A | Reolink | Amazon | $130 |
| Coral USB Accelerator (TPU) | coral-usb | Coral | Mouser | $60 |

## Enclosures + mechanical

| Part | SKU | Distributor 1 | Distributor 2 | Retail (USD) |
|---|---|---|---|---|
| UCTRONICS DIN rail Pi 5 case | U6277 | UCTRONICS | Amazon | $25 |
| Radxa CM5 industrial DIN enclosure | rock-cm5-din-industrial | Radxa store | — | $45 |
| Phoenix Contact 12-position 24 V terminal block strip | UT 2.5 DIN | DigiKey | Mouser | $8 |
| IP67 pole-mount cabinet 400 × 300 × 200 mm | RBM-5 | DigiKey | Allied Electronics | $110 |
| Cat 6a patch cable 1 m (TSN grade) | generic | Amazon / DigiKey | Any IT supplier | $5 |

## Field-wiring consumables

| Part | SKU | Distributor 1 | Distributor 2 | Retail (USD) |
|---|---|---|---|---|
| Insulated ferrules kit (0.5 / 0.75 / 1.5 mm²) | Knipex 97-99-910 | DigiKey | Amazon | $30 |
| Knipex ferrule crimper | 97-62-145-A | DigiKey | Amazon | $60 |
| Stranded wire 1.5 mm² (500 m spool, colour-coded) | LAPP 4520015 | LAPP catalogue | Amazon | $180 |

## Total first-article deployment cost

For **one Samawah line-1 trainset + adjacent 1-km wayside
section**:

| Bucket | Unit cost (USD) | Units | Subtotal |
|---|---|---|---|
| T-ECU/S per trainset | 240 | 2 | 480 |
| T-ECU/A per trainset | 300 | 2 | 600 |
| T-OBS per trainset (includes LIDAR) | 2 300 | 2 | 4 600 |
| W-SBC per junction box | 350 | 2 | 700 |
| Fence-line sensor (1 km) | 3 000 | 1 | 3 000 |
| ROW LIDAR × 5 + radar × 2 | 4 500 + 1 000 | 1 | 5 500 |
| CCTV + TPU | 190 | 2 | 380 |
| Enclosures, cabling, consumables | — | — | 1 500 |
| **Total** | | | **~$16 800** |

Scale per trainset (electronics + sensors only): ~$5 700. Scale
per km of wayside (section + sensors): ~$10 000.

For a full Samawah deployment (10 trainsets + 30 km of track =
~30 sections): **~$360 000 in electronics**. Compares to a
legacy CBTC system at ~€50M for an equivalent network — two
orders of magnitude difference dominated by NRE on the legacy
side.
