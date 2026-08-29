# T-ECU/A bring-up — Raspberry Pi CM5 IO Board

**Goal:** validate the application-tier host runs every non-safety
onboard crate and the TCN-E + TRG radios enumerate on a stock
CM5 carrier.

## Dev kits + parts

| Part | Qty | Notes |
|---|---|---|
| Raspberry Pi CM5 (4 GB + 32 GB eMMC) | 1 | |
| Raspberry Pi CM5 IO Board | 1 | |
| M.2 Hat+ (Waveshare or Pimoroni) | 1 | For NVMe + 5G modem. |
| NVMe SSD 256 GB | 1 | Event recorder ring buffer target. |
| Cat.22 5G M.2 module (unlocked) | 1 | TRG-1 primary radio. |
| LoRa SX1276 breakout on SPI | 1 | TRG-2 backup radio. |
| Mikroe CAN-FD Click 3 (x2) | 2 | Onto the IO Board's mikroBUS slots. |
| USB-C PD 5V/3A supply | 1 | |

## Steps

### A1 — Boot mainline Debian

1. Write Debian 13 `arm64` (with RPi kernel) to the CM5 eMMC via
   `rpiboot`.
2. First-boot: set hostname `tecus-devkit`, expand rootfs to NVMe.
3. Install Rust toolchain: `curl ... | sh`, `rustup default stable`.

**Expected:** ssh login within 60 s of power-on.

### A2 — Clone + build the workspace

```bash
git clone https://github.com/modernecotech/OpenSourceRail.git
cd OpenSourceRail
cargo build --release --workspace
```

**Expected:** clean build; 46 crates compile. Wall-clock ≤ 20 min
on a 4 GB CM5.

### A3 — Enumerate peripherals

Confirm each peripheral shows up in the kernel:

```bash
ip link show                # two Ethernet interfaces
ls /sys/class/net           # eth0, eth1
lspci                       # NVMe, 5G M.2
ls /dev/ttyAMA*             # UARTs
ls /dev/spidev*             # SPI buses
ls /sys/bus/i2c/devices     # I2C (TCN-E + ATECC608)
```

Tick each off in the report. Missing devices → check device-tree
overlay; common culprit is missing `dtoverlay=pcie2-1lane` or
equivalent in `config.txt`.

### A4 — TCN-E mock loopback

```bash
cargo test -p osr-tcn --lib -- --nocapture
cargo test -p osr-tcn --test roundtrip_single_payload -- --nocapture
```

**Expected:** both green. The UDP-over-loopback path (RFC 0006
v1.5) is the surrogate for the eventual TSN link.

### A5 — TRG-1 (5G) bring-up

Insert the 5G module into the M.2 slot. Install `ModemManager`
and `NetworkManager`.

1. Confirm `mmcli -L` lists the modem.
2. Activate a test APN: `mmcli -m 0 --simple-connect="apn=..."`.
3. Confirm IPv4 connectivity to a public endpoint.

**Expected:** working PDP context within 60 s of modem boot.

**Carrier choice:** bring-up is carrier-agnostic. For deployment
use, the `osr-t2g` SIM-profile spec ([RFC 0005 §3.2](../../docs/rfcs/0005-sbc-software-architecture.md#32-buses))
handles the operator's choice.

### A6 — TRG-2 (LoRa) bring-up

Connect SX1276 breakout to SPI0.

1. Build the `osr-t2g` diagnostic binary.
2. Run `osr-t2g-diag --link lora --tx-power 14dbm --channel 868.1`.
3. Confirm a second LoRa node (can be another dev board) receives
   the test packets with RSSI ≥ −110 dBm at 50 m line-of-sight.

**Expected:** ≥ 99 % packet delivery at 10 Hz test rate.

### A7 — CAN-FD bus test

Install two CAN-FD Clicks on the mikroBUS slots. Connect via a
CAN-FD transceiver test harness.

1. `ip link set can0 up type can bitrate 500000 dbitrate 2000000 fd on`.
2. `cansend can0 100##1.01020304`.
3. `candump can0` on the second Click receives the frame.

**Expected:** no frame loss at 1 kHz for 5 minutes.

### A8 — Shadow onboard stack in `osr-sim`

From the workspace:

```bash
cargo run --release --bin osr-sim -- \
    --scenario designs/west-asia/Iraq/Samawah/samawah.toml --duration 900 --status-every 60
```

**Expected:** the shadow onboard stack ran on every tick on the
CM5, consuming ≤ 20 % CPU, with zero invariant violations.

### A9 — Event recorder

```bash
osr-event-recorder-cli --tail 100 /var/log/osr/event.bin
```

**Expected:** the last 100 TCN-E frames from step A4 are
extractable. Ring buffer is working.

## Bring-up report template

```markdown
# T-ECU/A bring-up report

- Runbook commit: <hash>
- Date: <YYYY-MM-DD>
- CM5 serial: <nnn>

## Results
| Step | Status |
|---|---|
| A1 (Debian boot) | PASS / FAIL-\* |
| A2 (workspace build) | PASS / FAIL-\* |
| A3 (peripherals) | PASS / FAIL-\* |
| A4 (TCN-E loopback) | PASS / FAIL-\* |
| A5 (5G) | PASS / FAIL-\* |
| A6 (LoRa) | PASS / FAIL-\* |
| A7 (CAN-FD) | PASS / FAIL-\* |
| A8 (sim shadow) | PASS / FAIL-\* |
| A9 (event recorder) | PASS / FAIL-\* |
```
