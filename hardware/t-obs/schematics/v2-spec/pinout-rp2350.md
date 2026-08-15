# T-OBS v2 — RP2350 A + B pinouts

Both RP2350s run identical firmware; pinouts are symmetrical
between A and B. The tables below give channel A; channel B
is identical with `_A` suffixes changed to `_B`.

## RP2350 A — GPIO map

| GPIO | Peripheral | Function |
|---|---|---|
| GP0 | UART0 TX | Debug UART to JTAG header J11 |
| GP1 | UART0 RX | Debug UART |
| GP2 | SPI0 SCK | ATECC608 A SPI |
| GP3 | SPI0 TX | ATECC608 A SPI |
| GP4 | SPI0 RX | ATECC608 A SPI |
| GP5 | SPI0 CS | ATECC608 A SPI CS |
| GP6 | SPI1 SCK | Cross-check SPI (A ↔ B via ADuM1401) |
| GP7 | SPI1 TX | Cross-check SPI MOSI |
| GP8 | SPI1 RX | Cross-check SPI MISO |
| GP9 | SPI1 CS | Cross-check SPI CS |
| GP10 | PWM0 | Ultrasonic UL drive trigger (40 kHz tone burst) |
| GP11 | PWM1 | Ultrasonic UR drive trigger |
| GP12 | PWM2 | Ultrasonic LL drive trigger |
| GP13 | PWM3 | Ultrasonic LR drive trigger |
| GP14 | ADC0 | Ultrasonic UL echo in (A-side bank) |
| GP15 | ADC1 | Ultrasonic UR echo in |
| GP16 | ADC2 | Ultrasonic LL echo in |
| GP17 | ADC3 | Ultrasonic LR echo in |
| GP18 | CAN FD TX | Radar CAN-FD TX (to TCAN1462) |
| GP19 | CAN FD RX | Radar CAN-FD RX |
| GP20 | RMII clock | TSN A 50 MHz clock to 88E6321 |
| GP21..GP28 | RMII data | TSN A PHY interface to 88E6321 |
| GP29 | GPIO | `OBS_CLEAR_A` output to AND-gate K1a |
| GP30 | GPIO | `WATCHDOG_A` output to TPS3701 |
| GP31 | GPIO (input) | Field-input 1 (spare) |
| GP32 | GPIO (input) | Field-input 2 (spare) |
| GP33 | GPIO (input) | Reset-in from TPS3701 |
| GP34..GP39 | GPIO | Debug / LED / spares |

## Analog

| Pin | Function |
|---|---|
| `VREF` | 1.024 V precision reference, from REF3012 |
| `ADC0..ADC3` | Ultrasonic echo channels (0 – 3.3 V range, 12-bit) |

## Timer allocation

| Timer | Use |
|---|---|
| TIMER0 | 10 Hz control loop tick — runs the `evaluate()` call |
| TIMER1 | 20 Hz ultrasonic drive + echo TOF |
| TIMER2 | 100 Hz watchdog heartbeat to TPS3701 |
| TIMER3 | Reserved |

## Firmware layout (channel A)

| Section | Purpose |
|---|---|
| `main.rs` | Scheduler: every tick, (a) drive ultrasonic transducers, (b) read radar + LIDAR-summary + camera-class from CM5 via TSN, (c) run `osr_obstacle_detect::evaluate()`, (d) emit `OBS_CLEAR_A`, (e) SPI cross-check with channel B |
| `ultrasonic.rs` | 40 kHz tone-burst drive, echo-detect TOF capture, stale-channel diagnosis |
| `sensor_ingress.rs` | Parse TSN frames from CM5 with detection lists |
| `crosscheck.rs` | SPI1 protocol to channel B — peer `Clear` bit + detection-list hash |
| `watchdog.rs` | 100 Hz `WATCHDOG_A` toggle |

The `osr-obstacle-detect` crate is the evaluator core; `main.rs`
wraps it in the I/O shell. All I/O is in `main.rs`; the
evaluator itself is pure.
