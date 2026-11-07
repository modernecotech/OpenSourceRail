# Candidate-linked station-pair comparison

**[Open the interactive comparison](index.html)** · [Results and traces](study.json.gz) ·
[Mass reconciliation](mass-reconciliation.json.gz) · [Manufacturing/construction draft](delivery-draft.json.gz)
· [Requirement/evidence assessment](requirement-assessments.json)

This is one executable path from the **605-type, six-car parts proposal** through
mass scenarios, available-rating hypotheses, Rust force-driven motion, independent
braking, fleet, civil quantities and a complete scoped budget. It creates no
movement authority, reference adoption or engineering approval.

## Results under the declared assumptions

The bounded study evaluates **48 cases**, from 16 physical
system definitions across four architecture families, two spacings and three speed
caps. **36 nominal conditional runs arrive**; 28
also meet the declared time, moving-jerk, energy-residual, static-hold and demand
screens. These are numerical research results, not the missing authenticated
physical journeys in the historical 112-bundle portfolio.

The next-experiment examples below both use a **1.5 km, two-station, two-track pilot**,
276 normal passenger places, 4,000 peak passengers/hour/direction and 85% planning
occupancy. The demand-led headway is **200 s**, providing **4,222.8 planning
places/hour/direction**. This is capacity arithmetic, not protected timetable proof.

| Next experiment | Actual peak / cap km/h | Moving time | Conditional loaded mass | Full grid kWh/departure | Pilot installed USD low / base / high |
|---|---:|---:|---:|---:|---:|
| Cable / 6 motors / 200 m | 44.4 / 50 | 172.7 s | 115.51 t | 20.08 | $9.05 / $24.96 / $75.50m |
| Powered wheels / 8 driven axles | 60.0 / 60 | 144.2 s | 125.88 t | 21.75 | $10.05 / $26.89 / $80.59m |

Prices include four trainsets for these pilot examples, two accessible stations,
two-track reference-box concrete quantities, rails/fasteners, shared supports,
erection allowances, candidate propulsion, grid and hotel chargers, protection,
depot, assembly/test/setup, integration and contingency. **These are not 30 km city
prices, supplier quotations or demonstrated mass-purchase discounts.** Purchased
custom and local-assembly scenarios primarily vary setup allowances; they do not
establish a make-versus-buy productivity advantage. The report provides all cost
accounts and 30-year discounted scenarios, including renewal and operating costs.

## What the comparison revealed

- **Mass is reconciled, not measured:** the exact counted catalogue plus explicit
  2/5/10 t installation reserves gives loaded, architecture-before-additions
  scenarios of approximately 101.19 / 115.51 / 137.30 t. Driven-wheel equipment is
  added separately. The 105.25 m body-plus-gap length, 24 service actuators and
  760 mm wheels belong to this new proposal. Actual installed CG, inertia, axle
  loads, trim, service access and full CAD assembly remain unresolved.
- **A speed cap is not a speed requirement.** The cheap six-motor, 200 m cable
  example peaks near 44 km/h under its 50 km/h cap. Its acceleration is force-limited
  despite requesting 1 m/s². Longer windows and larger drives remain visible
  alternatives; neither 72 km/h nor 900 m is prescribed.
- **Fault replay exposes failure:** mass and wind changes miss the berth with the
  nominal brake point. The ±2% grade controls expose missing hill-start protection
  and substantial downhill overrun. Power-loss and emergency-stop examples on
  level track use independent assumed pneumatic braking. They do not prove safe
  recovery, wheel-slide protection, brake temperature or an operational controller.
- **Jerk has two distinct results:** nominal moving jerk is calculated and screened;
  the final rolling-to-held-stop acceleration transition remains unresolved. The
  replay does not conceal emergency discontinuities or refit braking per fault.
- **Auxiliaries matter:** continuous 35 kW/car, a 50 kW/car control, dwell and
  terminal turn are accounted for, with 90% charging efficiency. Required dwell-only
  recharge power is shown separately from propulsion peak power; charger curves,
  battery SOC/temperature and depot/spare conditioning remain open.
- **No regeneration saving is credited.** Detached tug/rope kinetic energy is
  exported to a disposal/reset account, never silently donated to coasting. Return
  energy and reset-time/force allowances are counted. The eight-cycle thermal RC
  proxy is uncalibrated; reported journey peaks exclude reset-transient peaks and
  idle motor/copper losses. It is not a thermal qualification.
- **LIM and hybrid remain in the comparison:** absent candidate-specific available
  force maps produce explicit holds, unknown energy/power/mass additions and
  positive provisional cost reserves. They do not become zero-cost failures.

## From source to manufacture

The [parts catalogue](../vehicle-parts/index.html) supplies materials, multiplicity,
stock/process allowances, joint/fixing proposals, QA and repair methods. The
candidate-linked delivery draft scales those same parts to the pilot fleet, adds
architecture equipment, and lists construction quantities and assembly dependencies.
Its ERPNext-style records are **disabled**; no purchasing, work order or control
transaction is performed. Production capacity and construction duration remain
unknown until actual processes, drawings, sites and crews are sized.

The [civil geometry dossier](../viaduct-backends/README.md) provides the exact
20 m reference-box geometry for fresh quantity calculations. Earlier FEM loads,
prestress/reinforcement design, bearings, foundations and crane approval do not
transfer to this heavier/different candidate. The base lift reserve exceeds a
nominal 60 t class: configured radius/capacity, rigging and temporary stages need
an actual lifting study.

The standalone Rust kernel retains finite drive windows, force/power/contact caps,
external rope/tug mass, grade, wind, drag, independent brakes, event transitions,
temperature budget and work-energy residuals. Position is never reset to the berth.
Native requests, failed trials and resource receipts remain in the private run;
the portable packet contains all nominal/fault inputs and outputs for replay.
All source hashes, physical/evaluation identities and cost ownership are checked.

## Reproduce

```bash
./osr design station-pair plan
./osr design station-pair run --output /path/to/private/station-pair-run
./osr design station-pair publish --run /path/to/private/station-pair-run --output /path/to/fresh/publication
./osr design station-pair verify
./osr design station-pair verify --replay --state /path/to/private/replay
```

Verification checks current source, candidate, mass, accounting and artifact
identities. `--replay` separately rebuilds the locked Rust kernel and compares all
published nominal, fault and timestep-refinement outputs. It requires Cargo's
locked dependencies to be locally available. Independent tests cover numerical
energy closure, cap/transition handling, faults and cache integrity. Verification
does not grant physical acceptance.

### Evidence and next action

Outline comparison and scoped pricing: **complete under stated assumptions**.
Installed engineering, robust protected journey, manufacturing release and
operation: **open**. There is no integrated selection. Resolve measured hot-duty
force/brake/charger characteristics, installed equipment and axle reactions,
adaptive protected stopping/hill starts, coupling/reset/rescue, civil moving loads
and prototype correlation before advancing a candidate.

Study `cc1ba1bf47f188657d334e7f14ed0adb1ebc8da9176f4880b2b276aa7a8f9061` · body `907da3680bcbd01ffe1223652443e4e34a9f581e201385917a99edf4150bd90a`.
Canonical source: [engineering/station_pair](../../../engineering/station_pair/).
