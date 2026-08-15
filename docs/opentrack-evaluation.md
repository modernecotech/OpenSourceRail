# OpenTrack Evaluation

Status: accepted architecture decision  
Reviewed: 2026-08-14

## Decision

OpenTrack does not replace SUMO or the native OpenSourceRail simulator in the
default toolchain.

OpenTrack may be used as an optional, independently procured railway-capacity
cross-check after a Samawah interchange trial. OpenSourceRail will incorporate
the useful analysis classes natively, using open schemas and deterministic
tests, rather than depending on OpenTrack at build, CI, city-generation, or
deployment time.

This preserves three deliberately different roles:

| Tool | Authority in OSR | Role |
|---|---|---|
| `osr-sim` | Authoritative for OSR control and energy behaviour | 800 V battery/charging, BMS reserve, roof PV, depot service, adaptive headways, movement-authority and onboard safety monitors |
| Eclipse SUMO | Open, reproducible independent screen | Geometry-shaped timetable execution, opposed services, junction/road interaction, feeder and multimodal sensitivity |
| OpenTrack | Optional licensed independent review | Rail-specific running time, headway, block occupation, timetable robustness, delay propagation, signalling and capacity comparison |

## Why It Is Useful

The current OpenTrack product describes support for metro, light rail and
tram systems; continuous speed/distance movement constrained by signalling and
timetables; line/station capacity and minimum-headway calculation; block,
moving-block, CBTC, ATP and ATO studies; infrastructure and train failures;
Monte-Carlo delay runs; and power/energy outputs. It also represents gradients,
speed limits and train tractive-effort/speed characteristics. Those capabilities
are better aligned with rail capacity work than SUMO's generic microscopic
traffic model.

Official product information also lists railML 1.0 and 2.2 import/export for
infrastructure, timetables and rolling stock, plus OpenTrack XML/ASCII and a
SOAP-over-HTTP API. This makes a controlled comparison technically feasible.

Sources:

- [OpenTrack Railway Simulation product description](https://www.opentrack.ch/opentrack/opentrack_e/opentrack_e.html)
- [ETH Zürich archived OpenTrack project description](https://archiv.ivt.ethz.ch/oev/opentrack/index_EN.html)
- [OpenTrack API description](https://www.opentrack.cz/opentrack_api_cz.html)

## Why It Is Not The Default

The official site presents a separately distributed full application and a
two-train-limited Light version, with access and API details handled through
the vendor. No open-source licence or public source distribution is identified
there. OSR therefore treats OpenTrack as proprietary external software unless
a procurement review proves otherwise. That inference must be rechecked before
any trial.

Making it the default would prevent an unlicensed contributor or CI runner from
reproducing a city package. Its advertised railML support also stops at 2.2,
whereas `osr-alignment` currently exports a limited railML 3.2 infrastructure
document. A direct round trip is not available today.

SUMO must remain because it is open and automatable and answers road,
pedestrian, feeder and multimodal questions that are outside OpenTrack's main
railway-capacity role. `osr-sim` must remain because neither external tool is
the authority for OSR's battery charging, BMS reserve, distributed movement
authority, onboard obstacle detection, depot rotation or safety monitors.

## Current Capability Gap

| Analysis | `osr-sim` now | SUMO city deck now | OpenTrack trial value | OSR disposition |
|---|---|---|---|---|
| Timetable/headway execution | Yes, scheduled and energy-adaptive | Yes, small deterministic service sample | Detailed timetable construction and robustness | Keep both open implementations; compare results |
| Continuous train motion | Rest-to-rest trapezoidal/triangular profile | Generic rail vehicle kinematics | Differential speed/distance with train characteristics | Add gradients, resistance and tractive-effort curves natively |
| Safe separation | OSR section occupancy and movement authority | Rail signals on per-line screening edges | Fixed/short/moving blocks and critical-headway analysis | Add occupation/headway evidence export natively |
| Interchange conflicts | Logical transfer groups; no full junction timetable model | Current lines are largely independent | Route occupation and station capacity | Add explicit route/conflict graph before acceptance |
| Disturbances | Named equipment/safety faults | Not a robustness study | Initial/station delays, failures and Monte Carlo | Add seeded stochastic timetable robustness runner |
| Energy | OSR-specific battery, charging, PV and sites | Not authoritative | General train power/energy | Keep OSR authoritative; compare mechanical duty only |
| Multimodal/road interaction | Out of scope | Appropriate independent tool | Not the primary purpose | Retain SUMO |

## Interchange Trial

The first trial is limited to Samawah Line 1 and must not modify the canonical
design.

1. Define a simulator-neutral OSR operations exchange containing topology,
   routes, station chainage, gradients, speed limits, dwell, timetable,
   consist mass/length, acceleration/braking limits and tractive-effort data.
2. Add a railML 2.2 export adapter specifically for the OpenTrack trial. Do not
   downgrade or replace the existing railML 3.2 alignment export.
3. Obtain a lawful full-version licence and written automation/API terms. The
   two-train Light limit is not sufficient for capacity or robustness work.
4. Import the same canonical exchange into `osr-sim`, SUMO and OpenTrack; use
   identical stop patterns and operating assumptions.
5. Compare running time, minimum headway, block/route occupation, energy at
   wheel, delay recovery and timetable conflicts. Record model differences,
   not merely percentage agreement.
6. Export results to a vendor-neutral JSON summary with tool version, input
   hashes, random seeds and acceptance tolerances. Never require an OpenTrack
   binary to read retained evidence.

Adoption fails if the trial loses station/route identifiers, needs unreproducible
GUI edits, cannot run with controlled seeds, cannot export reviewable results,
or requires OpenTrack-specific data to become canonical.

## Native OSR Work Packages

The following functions are approved for implementation independently of an
OpenTrack purchase:

- `OPS-SIM-001`: simulator-neutral network, vehicle and timetable exchange;
- `OPS-SIM-002`: gradient, curve resistance, adhesion and tractive-effort/speed
  integration in `osr-sim`;
- `OPS-SIM-003`: route locking plus block/route occupation and minimum-headway
  reports;
- `OPS-SIM-004`: seeded initial-delay, station-delay and equipment-failure
  ensembles with percentile punctuality and recovery metrics;
- `OPS-SIM-005`: timetable conflict, knock-on delay and turnback recovery
  analysis;
- `OPS-SIM-006`: Samawah cross-tool benchmark and documented tolerances.

Until OPS-SIM-001 through OPS-SIM-005 pass their benchmarks, city engineering
summaries must describe timetable and capacity outputs as screening evidence,
not calibrated operational acceptance.
