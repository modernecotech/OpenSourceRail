# S4 — Weather and environmental

**Scope:** network-wide environmental overlays per RFC 0013 §6.

**Cross-refs:** RFC 0013 §6 + `lib/templates/climate-adapters.toml`.

## Rules

### S4.1 — Dust storm (haboob)

On a declared dust-storm event (visibility below 200 m or
PM10 above the climate-adapter threshold), the dispatcher
imposes a network-wide 50 % speed cap, issues a passenger PA
on every line, and alerts the depot to schedule post-event
axle-box and switch-machine inspections.

**Why:** dust defeats optical sensors and accelerates switch-
machine wear. The 50 % cap preserves stopping-distance
margin against a reduced-adhesion wheel-rail contact; the
post-event inspection catches the wear before it becomes a
failure.

### S4.2 — Heatwave

On a sustained ambient above 45 °C for 2 hours or more, the
dispatcher imposes a 15 % speed cap on continuous-welded-
rail spans (per RFC 0009 presets marked CWR) and schedules a
pre-dawn recalibration of switch-machine detection sensors.

**Why:** CWR buckling risk rises sharply above 45 °C rail
temperature; the speed cap reduces dynamic load. Switch-
sensor drift at high temperature is recoverable by
recalibration but misreads in the meantime can jam a route.

### S4.3 — Flooding

On measured rainfall exceeding 50 mm per hour, the dispatcher
places an inspection hold on at-grade civil spans (no
movement until walked by MOW); elevated and bridge spans
continue per RFC 0011 §5.

**Why:** at-grade track is vulnerable to ballast washout and
drainage-ditch overtopping, which neither `osr-wayside-
points` nor the driver can see from the cab. Elevated and
bridge spans drain by design.

### S4.4 — Lightning

On lightning strikes within 2 km of the alignment, the
dispatcher monitors radio backhaul closely. If both 5G and
LoRa backhaul are lost for more than 10 s, the dispatcher
accepts degraded-mode operations (manual block working per
D6) until backhaul recovers.

**Why:** lightning induces surges that can knock out multiple
backhaul paths simultaneously. The 10 s window distinguishes
a momentary flap from a sustained outage that warrants the
degraded-mode switch.

### S4.5 — Sandstorm recovery

After a sandstorm clears, the dispatcher holds full-speed
operations until MOW has walked each affected section and
confirmed switches are clear of drift. Restricted-speed
(50 %) operation may resume as soon as visibility lifts.

**Why:** drift in switch throats jams the points mechanism
and can be missed by detection sensors that have been
abraded by the same event. The walk catches it; the speed
cap keeps passengers moving while the walk is in progress.
