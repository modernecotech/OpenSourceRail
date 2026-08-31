# DIY SD-card images

The planned application-host deployment boots from a prepared microSD card
carrying a minimal Linux base, an OSR role runner, `osr-selftest`, and the
per-deployment configuration. This page distinguishes that target from the
artifacts actually shipped today.

## Current source-build boundary

No signed OSR SD-card or Pico firmware image is published by v0.3.1. The Rust
workspace provides reusable control logic, simulation integration and the
`osr-selftest` software harness; it does not yet provide a board-support
package, bootable image recipe, hardware drivers or deployable RP2350 binary.

The commands below validate that the host-side integration libraries compile.
They do **not** create the `/usr/local/bin/osr-trainset-image` executable or a
`.uf2` file described by older drafts:

```bash
# On a build host (x86-64 Linux dev machine):
cd OpenSourceRail

# Cross-check the onboard integration library for the CM5 target.
rustup target add aarch64-unknown-linux-gnu
cargo build --release --target aarch64-unknown-linux-gnu \
    -p osr-trainset-image
```

Before any image can be flashed to pilot hardware, a deployment must add and
review all of the following:

- an operating-system image recipe with a pinned upstream base and packages;
- a role runner that drives the relevant libraries through reviewed hardware
  interfaces;
- CM5/Radxa board-support, device-tree and hardware-driver configuration;
- a genuine `no_std` RP2350 application and its watchdog/safety-I/O drivers;
- secure provisioning, update, rollback and key-rotation procedures;
- hardware bench tests, signed artifacts and reproducible-image checksums.

These are tracked as release gates in
[`../release-checklist.md`](../release-checklist.md). A deployment may use an
upstream operating-system image for bench development, but that is not an OSR
release image and must not command railway actuators.

## Planned signed artifacts

When the hardware gates close, each release must use filenames containing the
actual host, semantic version, hardware revision and content checksum. Paired
safety-channel firmware must identify its channel and refuse an incompatible
peer. Do not reserve fictional filenames in advance.

Every published image must be:

- **Signed** with the OSR project's ed25519 release key.
- **SHA-256 checksummed** for supply-chain verification.
- **Reproducible** — given the tagged workspace commit and pinned base-image
  digest, anyone can rebuild identical bytes.

Only flash an artifact after verifying its release signature, checksum, target
host and hardware revision. The release procedure will carry the exact command;
this document deliberately does not provide a destructive `dd` example for an
artifact that does not exist.

## Configuration

The planned image boots to a default config that will *not* proceed
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

The target systemd unit at `/etc/systemd/system/osr.service` will:

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
