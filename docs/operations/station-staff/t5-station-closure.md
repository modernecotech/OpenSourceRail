# T5 — Station closure

**Scope:** end-of-day shutdown. Evacuation (normal last-train
passenger clear), equipment powerdown, CCTV handover to OCC
night watch.

**Cross-refs:** RFC 0013 §4.3 T5.

## Rules

### T5.1 — Last-train clear

After the last revenue service departs, staff confirm the
platform is clear of alighting passengers and that no
passenger is attempting to board a non-revenue trainset.
The last-train clear is timestamped to the station log.

**Why:** the last train is where passengers are most likely
to miss a stop or fall asleep. The explicit clear establishes
that the platform was empty at a known time, which is
important for any later incident report.

### T5.2 — Platform + concourse walk

Staff walk the platform, stairs, concourse, and fare-paid
area checking for unattended items, sleeping passengers,
and equipment left out. Sleeping passengers are woken and
escorted out; unattended items follow T2.4.

**Why:** station closure without a walk leaves people inside
a locked station overnight, which has happened at many real
systems. The walk is the non-negotiable final sweep.

### T5.3 — Fare-gate + TVM lockout

Fare gates are locked in the closed-no-entry position; TVMs
are switched to "out of service" display and physically
secured. Night-mode lighting (50 % level) is switched on.

**Why:** open fare gates overnight invite entry to a station
with no staff presence; lit TVMs invite tampering. The
lockout and the out-of-service display remove the
temptation.

### T5.4 — PIS off-hours banner

The PIS is switched to the off-hours banner (first-train
timetable for tomorrow, emergency contact, no moving content).
Displays that would otherwise show "no service" are put into
standby instead.

**Why:** "no service" on a PIS overnight conditions passengers
to ignore PIS in the morning when "no service" would be real.
The dedicated off-hours banner is unambiguous.

### T5.5 — PSD overnight position

At PSD-equipped stations, PSDs are driven to the fully-closed
position for overnight. The PSD fault log is flushed to
`osr-station-scada` so morning staff can review overnight
anomalies.

**Why:** closed PSDs overnight prevent unauthorised platform
access from the concourse and reduce track-side dust
accumulation on PSD guide rails.

### T5.6 — CCTV handover

Staff hand over CCTV monitoring to the OCC night watch via
radio, acknowledged by the OCC night operator with a
countersigned entry in the station log.

**Why:** CCTV without a watcher is CCTV for post-hoc review
only. The handover ensures someone is always watching, and
the countersignature makes the moment of handover
auditable.

### T5.7 — SCADA low-power mode

The station SCADA is left in low-power mode (displays off,
core services running, heartbeat to the OCC active).
Services that can be off overnight (PA, TVM, non-critical
lighting) are switched off.

**Why:** the station still needs to respond to an overnight
event (fire, intrusion, flood) so the core SCADA stays on;
everything else reduces overnight load on the station-solar
battery bank.
