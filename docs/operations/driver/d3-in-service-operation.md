# D3 — In-service operation

**Scope:** between-station running. Speed within the ATP envelope,
vigilance acknowledgement cadence, station dwell handling,
passenger communication.

**Cross-refs:** [`osr-atp`](../../../crates/osr-atp/),
[`osr-vigilance`](../../../crates/osr-vigilance/), RFC 0013 §4.1 D3.

## Rules

### D3.1 — Speed within the envelope

In GoA 1 (manual) the driver's commanded speed stays ≤ 95 % of
the ATP envelope displayed on the DMI. In GoA 2 (ATO) the
driver verifies the actual speed tracks the ATO command within
± 1 m/s; any divergence greater than 2 m/s is reported as a
fault via `DMI → Fault → ATO divergence`.

**Why:** the ATP emergency trip activates at envelope +
`OVERSPEED_EMERGENCY_MARGIN_MMPS` (0.5 m/s per RFC 0005);
riding the envelope wastes margin and creates nuisance trips
on gradient transitions.

### D3.2 — Vigilance acknowledgement cadence

The driver acknowledges the vigilance prompt within 5 s of
each pulse. Nominal cadence is 30 s; a 5 s warning window
precedes a Tripped state. The driver does not pre-emptively
ack before the prompt.

**Why:** pre-emptive acks defeat the vigilance purpose —
`osr-vigilance` only accepts an ack that arrives in the
current window. Repeatedly missing the window and recovering
is logged as a pattern of driver fatigue and flags a rostering
review.

### D3.3 — Station approach

The driver begins the next-station announcement at 15 s from
arrival and confirms the ATO's deceleration profile matches
the DMI's target stopping point. The master controller stays
in the `ATO supervising` position through approach.

**Why:** the ATO's brake profile targets a ± 0.5 m stopping-
point accuracy; a driver late-overriding the brake command
compromises that accuracy and can leave a car or two outside
the PSD zone.

### D3.4 — Passenger announcements

The driver makes the next-station PA at 15 s before arrival
using the text `osr-pis-onboard` auto-populates. Ad-hoc
announcements (dispatch hold, weather speed restriction)
follow the phrasing guide in the station staff rulebook
[T2.5](../station-staff/t2-passenger-boarding.md).

**Why:** inconsistent train-vs-station announcements are a
quiet quality-of-service loss that compounds. One voice style
across touchpoints helps system trust.

### D3.5 — Passenger alarm response

If the passenger-emergency alarm fires (`DMI: passenger alarm
at car N, door P`), the driver stops the trainset at the next
station if within 30 s travel, otherwise immediately. In both
cases the driver makes a PA announcement and radios OCC with
Cat I4.

**Why:** a midline stop extends passenger-trapped time. If the
next station is ≤ 30 s away, completing to the station gets
ground help there faster than a midline stop + rescue coupling.

### D3.6 — Speed restrictions

The driver honours every `SpeedRestriction` entry on the DMI
without exception. Weather, track-work, and dispatcher-manual
restrictions all manifest the same way: DMI shows the
restricted speed, ATP's envelope tightens accordingly, the
driver's commanded speed respects the envelope per D3.1.

**Why:** restrictions exist because a condition has been
inspected and found. Ignoring one defeats the inspection that
produced it. The ATP enforcement is the final safety net —
not the primary mechanism.
