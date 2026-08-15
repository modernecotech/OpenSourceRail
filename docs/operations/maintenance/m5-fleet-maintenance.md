# M5 — Fleet maintenance

**Scope:** inspection intervals at the depot — daily, 7-day,
30-day, overhaul. Per RFC 0014 §5.1.

**Cross-refs:** RFC 0014 §§5.1, 5.2, [`osr-cbm-onboard`](../../../crates/osr-cbm-onboard/),
[`osr-cbm-backend`](../../../crates/osr-cbm-backend/), RFC 0013 §4.4 M5.

## Rules

### M5.1 — Daily inspection

Every trainset returning to depot is inspected daily at a
`main-heavy` or `secondary-medium` depot for: wheel and
tread visual (no flats, no cracks), door sealing (no visible
gaps), HVAC nominal, external body damage, and coupler face
integrity.

**Why:** daily inspection is the fastest feedback loop on
service wear. Catching a tread flat within one day of
formation prevents the flat from becoming a wheel spall
that requires reprofiling.

### M5.2 — 7-day inspection

Every trainset is inspected on a 7-day cycle for: wheel-wear
measurement (flange thickness, tread depth), friction-brake
pad thickness, battery-pack cell voltage spread, and under-
car wire harness chafe.

**Why:** 7 days is the cadence at which wheel wear becomes
measurably distinguishable from noise, and where a pad
approaching its wear limit can still be service-scheduled
without an emergency swap.

### M5.3 — 30-day inspection (EN 50126 A-class)

Every trainset is taken out of revenue service monthly for
a 30-day inspection: BMS deep-scan (every cell, every
temperature sensor, every contactor), motor-bearing
vibration spectrum, HVAC filter replacement, and
aux-inverter output quality check.

**Why:** the deep-scan items are diagnostic gold — they
catch failure precursors (cell imbalance, bearing harmonics)
that the daily and 7-day scans are not instrumented to see.
EN 50126 A-class is the safety-case-anchored interval.

### M5.4 — Wheel reprofiling

Wheels are reprofiled on the depot lathe at 150 000 km
cumulative service, or earlier if the 7-day inspection
records wheel wear exceeding the reprofile limit.

**Why:** 150 000 km is the RFC 0014 §5.2 CBM curve
intersection of wheel wear and reprofile cost. Earlier
reprofiling wastes wheel; later reprofiling risks flange
failure.

### M5.5 — Bogie overhaul

Bogies are overhauled at 600 000 km cumulative service at
`main-heavy` depots only. Secondary-medium depots do not
carry the jigs required for bogie overhaul.

**Why:** bogie overhaul requires frame-straightening jigs
and a wheelset press that would double the footprint of a
secondary-medium depot for a task that occurs once every
10+ years per trainset. Centralising at main-heavy is the
RFC 0014 archetype rationale.

### M5.6 — Body overhaul

The carbody undergoes overhaul at 10 years in service and
every 10 years thereafter: body shell corrosion inspection,
interior refurbishment, cable replacement, HVAC system
swap.

**Why:** body overhaul is a 20-40 year fleet life extension
activity. Skipping it shortens the fleet life from 40 years
to around 20 — a capital-planning catastrophe for the
deployment.

### M5.7 — CBM-triggered intervention

When `osr-cbm-backend` raises an amber condition on a
trainset component, the technician schedules intervention
within 7 days; a red condition triggers intervention within
24 hours, with the trainset held out of service in the
interim.

**Why:** CBM exists to move interventions from reactive to
scheduled. The 7-day and 24-hour windows are the RFC 0013
§4.4 thresholds calibrated against failure-mode progression
curves for the component classes in scope.
