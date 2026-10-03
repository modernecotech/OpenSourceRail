# T-OBS pin allocation and peripheral boundary

The machine-readable [Pico 2 bench allocation](../../../reference-integration.json) is the reference for both A and B local channels. It uses exposed GPIOs only. It replaces the former GP30–39 Pico allocation, GP14–17 ADC inputs, SPI secure-element and native CAN/RMII claims.

| GPIO | Bench function |
|---|---|
| 0 / 1 | I2C SDA / SCL for the channel-local ATECC608B breakout |
| 2 / 3 / 4 / 5 | SPI0 peer SCK / TX / RX / CS; suitable isolator, A controller and B peripheral |
| 10 / 11 / 12 / 13 | SPI1 external CAN-FD controller SCK / TX / RX / CS |
| 14 | Permission output to simulated-load driver |
| 15 | External hardware watchdog heartbeat |
| 16 / 17 / 18 / 19 | Laboratory ultrasonic triggers |
| 20 / 21 / 22 / 26 | Corresponding level-shifted timed digital echoes |

This is a proposed bench allocation. Peripheral IRQs, Ethernet controller bus, custom analog transducer AFE, debug pins and exact protocol/firmware mapping must be frozen before a board or image is released. Bench GPIO14 is not ADC0: Pico 2 exposes analog inputs on GPIO26–28. The custom chip package has a separate pinout; use its datasheet and never extrapolate the Pico header.

Pico 2 needs an external CAN controller plus transceiver. Ethernet also needs an external controller with a demonstrated data-rate/deadline budget. ATECC608B uses the selected I2C or single-wire interface, not SPI. Peer firmware and hardware tests must prove timing and fault behaviour; listing source filenames does not mean device drivers have been implemented.

Sources checked 3 October 2026: [Pico 2 datasheet](https://datasheets.raspberrypi.com/pico/pico-2-datasheet.pdf), [Microchip ATECC608B](https://www.microchip.com/en-us/product/ATECC608B).
