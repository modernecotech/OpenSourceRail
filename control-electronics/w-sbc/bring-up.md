# W-SBC bring-up — Radxa CM5 IO Board

**Goal:** validate the wayside host runs `osr-consensus` +
`osr-interlocking` + `osr-wayside-points` on a RK3588S Radxa CM5,
with the A55 little cluster isolated for the SIL-4 partition and
the A76 big cluster carrying non-safety services.

## Dev kits + parts

| Part | Qty | Notes |
|---|---|---|
| Radxa CM5 (8 GB + 32 GB eMMC, industrial-temp) | 1 | |
| Radxa CM5 IO Board | 1 | |
| SparkFun RS-485 breakout | 2 | One for switch-motor sim, one for HABD sim. |
| Test bench: 5-node consensus cluster | — | 4 more CM5 carriers OR a docker-compose simulator. |
| 24 VDC bench supply via ADuM isolator | 1 | |

## Steps

### W1 — Boot Debian with RK3588S BSP

1. Write Radxa Debian 13 image to eMMC via `rkdeveloptool`.
2. Expand rootfs, ssh login.
3. Update `/etc/default/cpufrq`: pin A55 cluster to 1.4 GHz, A76
   to ondemand.
4. Install Rust toolchain (same as T-ECU/A).

**Expected:** ssh login within 90 s of power-on.

### W2 — Workspace build

Same as T-ECU/A step A2. Build times on 8 GB A76 ~10 min.

### W3 — RT partition setup (safety role)

Configure the kernel for PREEMPT_RT on A76 and the A55 cluster
isolated for the safety partition:

```
isolcpus=0-3          # reserve A55 cores for safety
nohz_full=0-3         # tickless on safety cores
rcu_nocbs=0-3
```

Reboot. Verify `/proc/cmdline` contains the flags and `htop`
shows no processes scheduled on CPU 0-3.

### W4 — Consensus cluster bring-up

This step proves the W-SBC can host a consensus replica.

1. On the dev kit, run a local 3-node simulated cluster:

   ```bash
   cargo run --release -p osr-consensus --example local-cluster
   ```

2. Confirm leader election within 1 s.
3. Drive 100 proposals through; confirm all commit on every
   follower.
4. Kill one node; confirm re-election and continued progress.

**Expected:** clean leader election + commit progression + crash
recovery on the RK3588S silicon.

### W5 — Interlocking on the safety partition

Pin `osr-interlocking`'s MA computer to the isolated A55 cores:

```bash
taskset -c 0-3 cargo run --release --bin osr-sim -- \
  --config cities/catalogue/west-asia/Iraq/Samawah/samawah.toml --duration 600
```

**Expected:** the 10-minute Samawah run completes with zero
invariant violations; the MA computer's tick jitter (measured
via `osr-sim`'s internal timing) ≤ 5 ms.

### W6 — Wayside-points driver over RS-485

1. Connect one SparkFun RS-485 to a motor-driver sim (can be an
   Arduino reading the bus and toggling a digital output).
2. Build the `osr-wayside-points` standalone:

   ```bash
   cargo run --release -p osr-wayside-points --example switch-drive
   ```

3. Send alternating `SwitchCommand::Normal` / `SwitchCommand::Reverse`
   every 5 seconds.

**Expected:** motor drive toggles faithfully, detection
(simulated end-of-travel sensors) mirrors the command within
the 5 s RFC 0012 §4.2 throw budget.

### W7 — HABD input over RS-485

Simulate a hot-axle reading (raw temperature values) over the
second RS-485 link. Build the `osr-hot-axle-wayside` driver:

```bash
cargo run --release -p osr-hot-axle-wayside --example demo
```

**Expected:** temperature thresholding fires at configured
setpoint; the crate emits a `SpeedRestriction` event to the
consensus log simulator.

### W8 — Industrial-temp headroom

Place the Radxa CM5 in a 65 °C test oven (pre-deployment IP67
cabinet simulator) for 30 minutes with the W5 workload running.

**Expected:** no throttling, no CPU errors, no log anomalies.
RK3588S junction temp stays < 90 °C per the on-die sensor.

**FAIL-HW** if the board throttles or errors: the industrial-
temp variant may not be the one installed; confirm the P/N.

### W9 — PoE or dual-PSU input (optional)

If the cabinet-form-factor of the IO Board is present, validate
the dual-24V redundancy:

1. Run both PSU inputs; cut one; verify no service interruption.
2. Re-apply; confirm re-detection.

**Expected:** < 5 ms dropout at changeover.

## Bring-up report template

```markdown
# W-SBC bring-up report

- Runbook commit: <hash>
- Date: <YYYY-MM-DD>
- Radxa CM5 serial: <nnn>

## Results
| Step | Status |
|---|---|
| W1 (boot)        | PASS / FAIL-\* |
| W2 (build)       | PASS / FAIL-\* |
| W3 (RT + isol)   | PASS / FAIL-\* |
| W4 (consensus)   | PASS / FAIL-\* |
| W5 (interlocking)| PASS / FAIL-\* |
| W6 (points)      | PASS / FAIL-\* |
| W7 (HABD)        | PASS / FAIL-\* |
| W8 (thermal)     | PASS / FAIL-\* |
| W9 (dual-PSU)    | PASS / FAIL-\* / N-A |
```
