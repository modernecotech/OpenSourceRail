# M7 — Wayside sensor maintenance

**Scope:** per-section wayside intrusion-detection packs —
fence-line contacts, ROW-mounted LIDAR, ROW-mounted radar, CCTV
with AI classifier. See RFC 0016 §4 for the pack composition.

**Cross-refs:** [`osr-intrusion-detect`](../../../crates/osr-intrusion-detect/),
RFC 0016 §7.2 M7, RFC 0013 §4.4 (maintenance rulebook).

## Rules

### M7.1 — 30-day sensor-pack walk-through

Every wayside sensor pack is walked at 30-day intervals:
LIDAR and radar housings visually inspected for physical
damage and lens fouling, cable runs checked for rodent
damage, fence-line contact sensors spot-tested by induced
vibration, junction box door sealed.

**Why:** 30 days matches the M3 track-inspection cadence so
the walkthroughs can be combined and the crew makes one trip
instead of two. Most sensor faults develop over weeks, not
days — monthly is a reasonable detection floor.

### M7.2 — Post-weather inspection

After any RFC 0013 S4 weather event (haboob, heatwave,
flooding, lightning), maintenance inspects the wayside packs
in the affected sections within 48 hours. LIDAR + radar lens
cleaning is routine after haboob; fence-line contact re-set
is routine after lightning.

**Why:** weather is the single largest source of wayside-
sensor false positives and silent failures. Getting in
within 48 hours catches the obvious (dust-fouled lens) before
it becomes a sustained `Unknown` that an S7.2 ticket is
already addressing.

### M7.3 — Sustained-Unknown ticket response

A work ticket opened by dispatcher S7.2 (sustained `Unknown`
verdict) triggers an on-site maintainer visit within 4
hours of ticket creation. The maintainer performs a
calibration + self-test on each sensor, replaces any failing
unit from the depot spare pool, and issues a "returned to
service" confirmation to the dispatcher.

**Why:** the interlocking holds the section against revenue
traffic for the entire duration of the `Unknown`. Four hours
is the network-service cost budget: anything longer starts
to degrade timetable adherence to the point where the
dispatcher is re-routing or short-turning.

### M7.4 — Calibration after replacement

A replaced wayside sensor is re-calibrated against the
section's known rail-profile envelope before being committed
back into the `osr-intrusion-detect` evaluator. Calibration
uses the depot's reference retro-reflector at the published
lateral offsets from rail centreline; the first `Clear`
verdict after calibration is logged to the shift record.

**Why:** a replacement unit out of the box reads lateral
offsets off its own factory axis, not the section's rail
centreline. Skipping calibration is how sensor replacement
turns into a false-`Present` storm that reproduces the
failure on the next train.

### M7.5 — Fence-line continuity check

Every 90 days, the fence-line contact run is end-to-end
continuity-tested under sensor simulator stimulus. Any
continuity loss drives a segmented walk to isolate the
fault within 500 m.

**Why:** a quiet fence-line is *ambiguous* — it could mean
"no breach" or "sensor run broken for weeks." The 90-day
stimulus test distinguishes the two, which is what makes
the fence contact trustworthy as an I3 safety input.
