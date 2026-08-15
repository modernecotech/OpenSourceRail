# T1 — Station opening

**Scope:** daily station opening — power up, PIS check, fare-gate
test, PSD test, CCTV + PA handover.

**Cross-refs:** [`osr-pis-station`](../../../crates/osr-pis-station/),
[`osr-afc`](../../../crates/osr-afc/), [`osr-tvm`](../../../crates/osr-tvm/),
[`osr-psd`](../../../crates/osr-psd/),
[`osr-station-scada`](../../../crates/osr-station-scada/), RFC 0013 §4.3 T1.

## Rules

### T1.1 — Power-up sequence

Station staff power up subsystems in order: station SCADA →
PIS → fare (AFC + TVM) → PSD. Each subsystem must reach
"ready" on the station console before the next is started.

**Why:** PIS depends on SCADA time-sync; fare depends on PIS
for passenger display; PSD depends on fare for emergency-
release interlock. Out-of-order power-up races the
dependencies and produces spurious amber faults that waste
the opening window.

### T1.2 — PIS display self-test

Staff trigger the PIS self-test from the station console. The
test cycles each platform display through a colour pattern +
a sample "next train" message and reports OK per display to
`osr-pis-station`. Any display that fails self-test is
logged as a T1 fault and replaced or bypassed.

**Why:** a display that lights up but shows stale data is
worse than a dark display — passengers trust the wrong
information. The self-test exercises the end-to-end
rendering path, not just the backlight.

### T1.3 — Fare-gate test

Staff test each fare gate through a full open / close / emergency-
release cycle using a staff test card. Gates that fail to
close within 3 s or fail emergency release are taken out of
service and flagged for depot repair.

**Why:** a stuck-closed gate traps passengers in peak; a stuck-
open gate loses revenue and undermines fare enforcement. The
daily test catches both before passengers arrive.

### T1.4 — TVM test

Staff run a test purchase on each TVM: QR-code display,
mobile-money confirm, receipt print. Failed TVMs are taken
out of service with a paper "out of order" sign placed
physically on the machine.

**Why:** a TVM whose receipt printer has run out of paper
sells tickets passengers can't prove they bought, which
breaks fare enforcement downstream. The daily test catches
the mundane failures (paper, ribbon, mobile-money API key
expired).

### T1.5 — PSD test

At PSD-equipped stations, staff trigger a platform-side PSD
open / close / emergency-release cycle via the station
console. PSDs that fail open or close are locked open (not
closed) pending repair.

**Why:** a failed-closed PSD can trap a passenger on the
platform side of the door after train departure. Locking
failed PSDs open is the fail-safe choice — passengers can
still reach the platform but the PSD is visibly out of
service.

### T1.6 — CCTV handover

Staff assume CCTV monitoring from the OCC night watch via a
radio handover: confirmed cameras-OK count, outstanding
events logged overnight, any area under intrusion alert.

**Why:** OCC night watch covers many stations at low
attention; morning station staff cover one station at high
attention. The handover makes sure any overnight intrusion
alert is followed up on the ground, not filed and
forgotten.

### T1.7 — Ready-to-OCC

After T1.1–T1.6, staff post a "station ready" status via
`osr-occ`, which clears the station's morning-open flag in
the OCC roster. The dispatcher will not dispatch a first
revenue service to a station that has not posted ready.

**Why:** an unready station takes a first-service trainset
full of passengers with no working PIS, no open fare gates,
and possibly no PSDs. The explicit ready-post is the
handshake that prevents that.
