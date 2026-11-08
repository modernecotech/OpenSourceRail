# Candidate-linked station-pair comparison

**[Open the interactive comparison](index.html)** · [Full results and traces](study.json.gz) ·
[Mass reconciliation](mass-reconciliation.json.gz) · [Delivery draft](delivery-draft.json.gz) ·
[Requirement/evidence assessment](requirement-assessments.json).

This executable research path connects the **605-type, six-car parts proposal** to
mass scenarios, source-rating force hypotheses, Rust motion and braking, fleet,
civil quantities, costs and disabled manufacturing/construction records. It
compares a fixed nominal braking point with a bounded feedback controller on the
same physical configurations. No reference adoption or operating authority follows.

## What changed

The original experiment is [retained with its exact source epoch](../../archives/station-pair-fixed-control-20261107/README.md).
Its fixed controller remains reproducible. The current packet adds simulated
position, speed and acceleration observations, explicit uncertainty and response
bounds, pre-applied holding brakes and continuous distance feedback.

**Feedback braking points are never fitted offline or separately per fault.**
All mass, wind, grade, force and sensor experiments retain the same policy bounds
for each architecture. Grade and drive-fault notifications are explicit assumed
observations. Tests include both notified and unobserved partial drive failure.
The actual plant values remain separate from the controller's declared bounds;
posthoc domain diagnostics expose disagreements without passing truth to control.

The model travel boundary is **D**, the declared station target. The existing
plus/minus 2 m berth accuracy does not grant extra travel beyond D. Histories are
not snapped to a station. Bounded low-speed docking is permitted only where the
candidate already has powered hardware at the destination; cable designs receive
no invented force after their launch window.

## Results under assumptions

There are **48 nominal cases**: four propulsion families,
two station spacings and three speed caps. The fixed method gives
**36 conditional arrivals**; feedback gives
**18**. The viewer shows every paired result, including
short stops, departure holds, authority overruns and out-of-domain assumptions.
Arrival counts alone do not measure physical feasibility or qualified protection.

The original fixed cohorts remain in the paired experiments. Additional nominees
come from the feedback nominal screens, before inspecting the common fault suite.
They are next experiments, not an integrated selection. These examples use a **1.5 km,
two-station, two-track pilot**, 276 passenger places, 4,000 peak passengers/hour/
direction and 85% planning occupancy. The demand-derived 200 s headway provides
4,222.8 planning places/hour/direction; timetable protection remains unverified.

| Paired experiment | Actual peak / cap km/h | Feedback berth result | Pilot installed USD low / base / high |
|---|---:|---:|---:|
| Cable / 6 motors / 200 m | 41.9 / 50 | Held or missed berth | $9.05 / $24.96 / $75.50m |
| Powered wheels / 8 driven axles | 59.3 / 60 | 188.0 s | $10.05 / $26.89 / $80.59m |
| Cable / 6 motors / 350 m | 49.2 / 50 | 185.8 s | $9.10 / $25.06 / $75.78m |
| Powered wheels / 12 driven axles | 59.3 / 60 | 171.7 s | $10.37 / $27.51 / $82.15m |

Budgets include rolling stock, stations/access, reference-box concrete quantities,
rails/fasteners, shared supports, erection, propulsion, grid/hotel chargers,
protection, depot, assembly/test/setup, integration and contingency. Failed or
held journeys retain an explicit provisional runtime allowance; their energy and
whole-life operating totals stay unknown. **These are pilot budgets, not 30 km
city prices, quotations or demonstrated bulk-purchase discounts.** Local assembly
versus purchased-custom figures primarily vary setup allowances, not proven
productivity. Every cost account states its basis and exclusions.

## Findings that remain important

- A passive train can brake but cannot add energy after leaving its powered
  window. A short stop is retained as a performance failure; it is not corrected
  by moving the recorded position. Receiving-side positioning equipment would
  require its own physical definition, quantities, cost and dynamic evaluation.
- On a constant +2% climb, the base 6% rotating-mass hypothesis gives at most
  approximately **653 m coast from 60 km/h**, even ignoring air drag. The current
  200/350 m launch windows leave 1,150–1,800 m to travel. Better control cannot
  fix that energy deficit: change propulsion, speed or alignment.
- The 35.56 kN brake-force and 90% controller-floor assumptions leave little
  worst-case downhill authority at high mass. Slower running, conservative
  refusal or a separately engineered brake/architecture change can be necessary.
  No bound is weakened to make a candidate pass.
- Simulated sensor biases, weaker-than-assumed brakes, delayed response and
  unsupported tailwind remain explicit experiments. An arrival outside the
  declared controller domain never establishes protected operation.
- Final rolling-to-held-stop jerk, wheel-slide response, flexible-train dynamics,
  brake heating, engagement and rescue still need appropriate models and evidence.
  Emergency and supervisory discontinuities retain their calculated jerk.

## Same-candidate manufacture, mass and cost

The [parts catalogue](../vehicle-parts/index.html) supplies materials, quantities,
stock/process allowances, fixings, routes, QA and removal methods. Its 110,404 BOM
units are reconciled in grouped occurrences, with shared inter-car parts counted
once. Explicit 2/5/10 t installation reserves produce normal-loaded, before-drive-
addition scenarios of approximately 101.19 / 115.51 / 137.30 t. These are counted
stock and allowances, not measured installed weights. Driven-wheel additions are
separate; installed CG/inertia, actual axle loads, trim and complete CAD remain open.

The body-plus-gap length is 105.25 m. End coupler projection, usable platform
margin, installed equipment clashes and moving interfaces remain unknown. The
exact [20 m civil geometry](../viaduct-backends/README.md) feeds fresh quantities,
without inheriting earlier FEM loads, reinforcement, foundations or crane approval.
The base lifting reserve exceeds a nominal 60 t class; actual radius, rigging and
erection stability need a lifting study. Draft records are disabled: no purchasing,
work order or control transactions occur. Production capacity and construction
programme duration remain unverified.

Energy includes propulsion, cable return/reset, continuous 35 kW/car auxiliaries,
dwell, terminal turn and 90% charging efficiency; a 50 kW/car control is retained.
Charging power is distinct from propulsion peak. Battery/charger limits and
spare/depot conditioning remain open. No regeneration credit is invented.
The repeated-duty RC proxy is uncalibrated, excludes idle motor/copper losses,
and its reported journey peak excludes reset-transient peaks.

The controller uses braking-curve principles described in the
[ERA introduction, sections 3.1–3.3](https://www.era.europa.eu/system/files/2022-11/Introduction%20to%20ETCS%20braking%20curves.pdf):
state uncertainty, braking buildup and track characteristics must be explicit.
This research method is not an ETCS implementation or compliance claim.

## Common fourteen-scope accounting

The [expanded lifecycle ledgers](lifecycle-ledgers.json.gz) separately reconcile
all fourteen scopes, including explicit land/utilities, rescue, reliability,
component renewals, omitted station/depot maintenance and final disposal.
These extend the original pilot budget without double-counting its accounts.
The table above retains that original narrower budget for comparison. Financing,
taxes, customs and exchange-rate policy remain separate project layers. Missing
journey electricity keeps complete NPV unknown. The exact earlier feedback
publication is [retained](../../archives/station-pair-feedback-20261107/README.md).

## Reproduce and challenge

```bash
./osr design station-pair plan
./osr design station-pair run --output /path/to/private/station-pair-run
./osr design station-pair publish --run /path/to/private/station-pair-run --output /path/to/fresh/publication
./osr design station-pair verify
./osr design station-pair verify --replay --state /path/to/private/replay
./osr design station-pair history-verify
```

Verification checks source, physical/evaluation identities, identical controller
policies, mass, cost ownership and every generated artifact. `--replay` rebuilds
the locked Rust kernel and compares published fixed/feedback nominal, fault and
refined-timestep outputs. Requests, unsuccessful trials, errors and resource
receipts remain in the private run. Source development and numerical execution use
separate directories; the worker process has explicit resource limits, not a
claimed OS sandbox.

Outline comparison and scoped pricing: **complete under assumptions**.
Installed engineering, robust protected service, manufacturing and operation:
**open**. Resolve measured actuator/brake/charging characteristics, installed
geometry, axle reactions, receiving/positioning behaviour, civil moving loads and
prototype correlation before advancing an integrated design.

Study `188d82f25ed2d26bf5e7e4e99d620764f1379434c4262d55735f6754ab0cf304` · body `907da3680bcbd01ffe1223652443e4e34a9f581e201385917a99edf4150bd90a`.
[Canonical source](../../../engineering/station_pair/).
