# Design option results — 18 September 2026

These experiments address per-line mileage failures. They do not establish
peak-headway delivery, passenger capacity, multi-day energy sustainability or
engineering/operating acceptance. All service thresholds and timetable windows
remain unchanged. The generator baselines match the checked-in scenarios.

## Baseline and unsuccessful charging-only trials

The retained [Samawah baseline](../../docs/operating/status/rehearsals/samawah-service-qualification.json)
passes nominal service but fails four degraded cases on line 1. Its 270-second
charging dwell is increased in two exploratory trials:

| Line 1 dwell | Hot climate | Aged battery + heat | Missed charging stops | Overall |
| --- | ---: | ---: | ---: | --- |
| 270 seconds (baseline) | 87.26% | 87.54% | 88.34% | Failed; pad outage also fails |
| 300 seconds | 88.82% | 86.83% | 87.69% | Failed |
| 330 seconds | 87.64% | 86.65% | 87.53% | Failed |

Values are delivered/scheduled line mileage. Longer stops do not monotonically
improve service: charging time competes with circulation and station occupation.
The charging-only trials pass the pad-outage case but leave three failures.
Their [300-second](exploratory/dwell300/qualification.json) and
[330-second](exploratory/dwell330/qualification.json) reports retain full input
snapshots and validator hashes. They predate the sealed option runner; they are
exploratory evidence, not promoted candidates.

## Controlled fleet and energy options

The city-scoped Workbench view loads the sealed bundles listed in
[catalogue.json](catalogue.json), including unsuccessful options. Each bundle
records generic/city settings, effective input changes, resource deltas, exact
source dependencies and the full nominal/eight-case qualification.

### Samawah: fleet capacity as well as charging time

| Option on line 1 | Nominal | Hot climate | Aged + heat | Missed charging | Degraded cases passed |
| --- | ---: | ---: | ---: | ---: | ---: |
| 300 seconds + 12 trainsets | 93.01% | 89.25% | 89.58% | 89.95% | 6/8 |
| 300 seconds + 20 trainsets | 94.19% | 92.79% | 92.69% | 91.02% | 8/8 |

The [12-train option](examples/samawah-fleet12/qualification.json) fails both heat
cases. The [20-train option](examples/samawah-fleet20/qualification.json) passes the
complete nominal and eight-case suite across all three lines. Its line-1 fleet
increases from 53 to 73; the whole city increases from 108 to 128. Each powered
line-1 stop gains 30 seconds of charging dwell. The grid-outage line-1 result is
84.42%, above its separate 60% requirement. These are demonstrated alternatives,
not proof that 20 trains is the minimum addition or the least-cost solution.

### Mosul: outage endurance

The [controlled energy option](examples/mosul-energy/qualification.json) adds
three storage modules and 300 kWp solar at each of nine line-2 sites: **27 modules,
13,500 kWh storage and 2,700 kWp solar** in total. Existing charge/discharge rates,
charger power, fleet and timetable remain unchanged. Line 2's ten-hour all-site
outage delivery rises from **51.81% to 88.78%**. All six lines pass nominal service
and all eight degraded cases; the lowest outage result is line 4 at 62.97%, above
the existing 60% emergency floor. The separate [exploratory energy run](exploratory/line2-energy/qualification.json)
also passed before the sealed workflow rerun.

Across both cities, six full candidate suites were executed (54 runs of 90,000
simulated seconds): three exploratory and three controlled. The controlled
12-train Samawah option fails; the controlled 20-train Samawah and Mosul energy
options pass. This is a targeted design comparison, not an exhaustive parameter
sweep, calibrated demand study or least-cost optimization.

Resource counts are planning deltas, not approved purchase orders. Added trainsets
also add initially charged onboard energy; a 25-hour run does not establish a
repeatable multi-day charging/stabling cycle. Added solar generation requires real
area and calibrated weather assumptions. Extra storage remains constrained by the
existing site discharge and charger power limits. Cost, maintenance, supplier,
site and independent operator reviews are still required.
