# S-SBC bring-up — RPi CM5 on Waveshare CM5-IO

**Goal:** confirm the station / depot host runs `osr-psd` +
`osr-afc` + `osr-tvm` + `osr-pis-station` + `osr-station-scada`
on a stock commodity carrier, with the small ATECC608 add-on as
the only custom-PCB piece.

## Dev kits + parts

| Part | Qty | Notes |
|---|---|---|
| Raspberry Pi CM5 (4 GB + 32 GB eMMC) | 1 | |
| Waveshare CM5-IO (commodity) | 1 | |
| ATECC608 breakout on I²C | 1 | The only custom PCB — a 30 × 20 mm carrier for the SE chip. |
| QR scanner (USB) | 1 | |
| NFC reader (USB, ACR122U or equivalent) | 1 | |
| Thermal receipt printer (USB) | 1 | |
| 10-inch HDMI screen | 1 | PIS display. |
| Test bench | — | |

## Steps

### X1 — Boot Debian

Same as T-ECU/A step A1, same image, same hostname pattern
(`ssbc-devkit`). No RT configuration — station role is SIL-0.

### X2 — Workspace build

Subset build: station-side crates only.

```bash
cargo build --release -p osr-psd -p osr-afc -p osr-tvm \
    -p osr-pis-station -p osr-station-scada
```

### X3 — ATECC608 add-on enumeration

```bash
i2cdetect -y 1        # see ATECC608 at 0x60
```

**Expected:** chip responds. Provision a test key via the
`osr-crypto` provisioning tool.

### X4 — Fare gate (osr-afc)

Connect QR scanner + NFC reader to USB. Run the AFC gate
simulator:

```bash
cargo run --release -p osr-afc --example gate-demo
```

Present a test QR code; present a test NFC token.

**Expected:** both decode + produce `FareAccepted` events within
100 ms.

### X5 — Ticket vending (osr-tvm)

Connect the receipt printer. Run:

```bash
cargo run --release -p osr-tvm --example tvm-demo
```

Drive a scripted purchase: scan product QR, submit mock mobile-
money payment, confirm printed receipt.

**Expected:** receipt prints within 3 s of payment confirmation.

### X6 — Passenger information (osr-pis-station)

Connect the HDMI screen. Run:

```bash
cargo run --release -p osr-pis-station --example display-demo
```

**Expected:** next-arrival list displays; mock incoming MA
updates refresh the arrival times.

### X7 — PSD controller (osr-psd)

With no physical PSD on the bench, use the crate's software-only
simulator. Run:

```bash
cargo run --release -p osr-psd --example psd-demo
```

**Expected:** the five-state PSD FSM transitions correctly on
simulated train-arrival + door-open / close events.

### X8 — Station SCADA

Launch:

```bash
cargo run --release -p osr-station-scada --example scada-demo
```

Simulate HVAC / lighting / escalator status inputs.

**Expected:** status dashboard populates; threshold alarms fire
within one tick of exceeding setpoint.

### X9 — Sustained run

Run all five station crates simultaneously for 1 hour.

**Expected:** CPU load ≤ 30 %, RAM ≤ 1 GB, no process restarts.

## Bring-up report template

```markdown
# S-SBC bring-up report

- Runbook commit: <hash>
- Date: <YYYY-MM-DD>
- CM5 serial: <nnn>

## Results
| Step | Status |
|---|---|
| X1 (boot)     | PASS / FAIL-\* |
| X2 (build)    | PASS / FAIL-\* |
| X3 (ATECC608) | PASS / FAIL-\* |
| X4 (AFC gate) | PASS / FAIL-\* |
| X5 (TVM)      | PASS / FAIL-\* |
| X6 (PIS)      | PASS / FAIL-\* |
| X7 (PSD)      | PASS / FAIL-\* |
| X8 (SCADA)    | PASS / FAIL-\* |
| X9 (1 h run)  | PASS / FAIL-\* |
```
