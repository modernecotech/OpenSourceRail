# DIY SD-card images

Every host class boots off a prepared microSD card. The card
carries a minimal Linux base, the OSR crate binaries for that
host class, `osr-selftest`, and the per-deployment configuration
file.

## Source-Build Path

Until signed pre-built images ship, each deployment builds its own
image from the workspace:

```bash
# On a build host (x86-64 Linux dev machine):
cd OpenSourceRail

# Cross-compile the onboard crate family for aarch64 (RPi CM5 target).
rustup target add aarch64-unknown-linux-gnu
cargo build --release --target aarch64-unknown-linux-gnu \
    -p osr-trainset-image    # for T-ECU/S + T-ECU/A
# or -p osr-obstacle-detect  # for T-OBS
# or -p osr-interlocking     # for W-SBC
# or -p osr-psd              # for S-SBC (and friends)

# Flash a base Raspberry Pi OS Lite image to the SD card
# using the official Raspberry Pi Imager.

# Mount the SD card and copy the compiled binary + config:
sudo cp target/aarch64-unknown-linux-gnu/release/osr-trainset-image \
    /mnt/sdcard/usr/local/bin/
sudo cp hardware/t-ecu-s/diy-assembly/sample-config.toml \
    /mnt/sdcard/etc/osr/config.toml
sudo cp hardware/diy-assembly/osr.service \
    /mnt/sdcard/etc/systemd/system/

# Eject, insert into the CM5 IO Board's microSD slot.
```

Then provide the two Pico 2 boards with their firmware:

```bash
# RP2350 Pico 2 firmware — no_std build.
cd crates/osr-atp     # or osr-obstacle-detect
cargo build --release --target thumbv8m.main-none-eabihf

# Flash each Pico 2 in turn while holding BOOTSEL + plugging USB.
# The Pico 2 appears as a mass-storage device; copy the .uf2:
cp target/thumbv8m.main-none-eabihf/release/*.uf2 /mnt/rpi-rp2/
```

## v0.2 — pre-built images

Per-host-class images at the project's release page will be:

- **`osr-t-ecu-s-v0.2.img.xz`** — RPi OS Lite + CM5 + `osr-trainset-image`.
  Plus two paired `.uf2` files (`osr-tecu-s-chan-a-v0.2.uf2`,
  `osr-tecu-s-chan-b-v0.2.uf2`) for the two Pico 2 boards.
- **`osr-t-ecu-a-v0.2.img.xz`** — CM5-only; no Pico 2 required.
- **`osr-t-obs-v0.2.img.xz`** + two paired `.uf2` per board.
- **`osr-w-sbc-v0.2.img.xz`** — Radxa CM5 bare-image; Pico 2
  optional for safety-critical points-machine interlocks.
- **`osr-s-sbc-v0.2.img.xz`** — RPi CM5-only.

Each image will be:

- **Signed** with the OSR project's ed25519 release key.
- **SHA-256 checksummed** for supply-chain verification.
- **Reproducible** — given the tagged workspace commit,
  anyone can rebuild an identical image.

Flash with the Raspberry Pi Imager or `dd`:

```bash
xz -d osr-t-ecu-s-v0.2.img.xz
sudo dd if=osr-t-ecu-s-v0.2.img of=/dev/sdX bs=4M status=progress
sync
```

## Configuration

Every image boots to a default config that will *not* proceed
past self-test until `/etc/osr/config.toml` is populated with:

- **`deployment_id`** — string identifier for the operator.
- **`entity_id`** — the unique ATECC608B-backed id for this
  specific unit (RFC 0017).
- **`role`** — host class (`t-ecu-s-A`, `t-ecu-s-B`, `t-ecu-a`,
  etc.).
- **Deployment key registry** — path or URL to the per-
  deployment `KeyRegistry` (RFC 0017 §3.2).
- **Network endpoints** — TSN neighbour list, OCC address.

Sample configs ship in each `<class>/diy-assembly/sample-config.toml`.

## Boot flow + self-test

Systemd unit at `/etc/systemd/system/osr.service`:

1. Wait for hardware-clock sync (PTP, if available, else NTP).
2. Validate the deployment config — reject if missing required
   fields.
3. Load the ATECC608B trust anchor — reject if absent or
   disagreeing with `deployment_id`.
4. Run `osr-selftest`:
   - Ping both Pico 2 channels (for 2oo2 boards).
   - Exercise each sensor's health check.
   - Confirm every RFC 0005 crate for this role loads.
5. Emit "ready" on the LED + TSN heartbeat.
6. Enter the main role loop.

If any step fails the unit holds in a red-LED fault state
and refuses to drive actuators. The custom-PCB v2 spec's
watchdog supervisor has an equivalent role; the DIY path
relies on systemd + the Pico 2's own watchdog.
