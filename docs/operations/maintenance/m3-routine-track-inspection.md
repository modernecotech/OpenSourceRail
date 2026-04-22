# M3 — Routine track inspection

**Scope:** walking the line, visual checks, geometry-recording-car
cadence per RFC 0009 §9.

**Cross-refs:** RFC 0009 §9, RFC 0013 §4.4 M3.

## Rules

### M3.1 — Visual walk

Every section is walked visually every 7 days in the direction
of traffic. Walkers check for: missing fasteners, cracked
sleepers, rail-head spalling, ballast shoulder loss, and
vegetation encroachment.

**Why:** visual inspection catches the failures that
measurement misses (missing bolts, cracked concrete sleepers)
and measurement catches what visual misses (geometry drift).
Both cadences are non-redundant.

### M3.2 — Geometry recording car

The geometry recording car runs per RFC 0009 §9 preset
cadence: `standard-urban` every 90 days, `standard-metro`
every 60 days, `mainline-mixed` every 45 days. Output is
reconciled against the previous run to detect trend
deterioration.

**Why:** geometry drift (gauge, cant, alignment, twist) is
linear-predictable from trend data; a single reading is less
informative than the delta. The preset-specific cadence
reflects the loading severity of each preset.

### M3.3 — Post-weather inspection

Flooding, dust, or heatwave events (per S4.1–S4.3) trigger
an immediate post-event walk of affected sections before
full-speed service resumes. The walk is additional to, not
a substitute for, the 7-day routine walk.

**Why:** extreme weather produces failure modes (ballast
washout, drift-jammed switches, rail buckles) that the 7-day
walk won't catch in time. Post-event walks insert an extra
data point at the moment risk is elevated.

### M3.4 — Defect classification

Defects are classified at the point of discovery as QN1 (quality
note, alert) or QN2 (immediate action). QN1 is logged and
scheduled for the next maintenance window; QN2 raises a work
block under M2 and halts service through the affected
section until fixed.

**Why:** the classification is the inspector's judgement call
but it's binary — alert or act. Grey-zone intermediates
(semi-urgent, action-next-week) are how a QN2 becomes a
derailment.

### M3.5 — Turnout inspection

All turnouts are inspected monthly for bolt tightness, weld
cracks, switch-point closure, and detection-sensor alignment.
Findings are logged per switch id to `osr-wayside-points`.

**Why:** turnouts concentrate wear and are the single largest
derailment-risk feature on the railway. Monthly cycling keeps
the inspection window shorter than the failure window for
the known modes.

### M3.6 — Fence + intrusion walk

Every 30 days, the fence line is walked for breaks, damaged
gates, and evidence of animal intrusion. Breaks are
recorded, GPS-tagged, and scheduled for repair within
7 days.

**Why:** a fence break lets in both humans (trespass risk)
and animals (collision risk). The 30-day cycle catches
seasonal changes (grown-in gaps closing or new gaps opened
by flooding) before an incident.
