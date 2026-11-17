# v0.7 affordable railway: first engineering decision gate

**17 November 2026.** This is a bounded engineering decision record, not a
physical design release. The selected v0.6 reference remains the passive-wheel,
six-car vehicle `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.
Its station propulsion installation has not been selected. The evidence below
keeps physical candidate, evaluation and selection identities separate.

## One service and price control

The [fresh, source-verified 30 km packet](../line30-current-20261117/README.md)
uses the **synthetic level** 30 km, two-track, 12-station corridor. It is not a
Samawah alignment. It fixes 8,280 offered normal places/hour/direction, a
maximum 120 s headway, 44 seats and two wheelchair places per car, no planned
standing, six 17 m cars, 72 km/h launch cap, 35 s dwell and 30 years of
operation. Its requirements ID is `a18e0f20b6ec40e067aff40213b312ae756f7f3389ee5b43059225cf92d05ff4`;
rate assumption ID `206d3aed6928722c29f3594683962d5af4512888728ce189db6c3a3754351df6`.
The new evaluation is `947dd7cbcac7c260da721150912fba47531c96fd3f7a28365c394249608ee869`,
manifest `b455f1f9cfa98bd41d958c736862e75578c831d287db7b5c95ca48b5a82af2c4`.
The retained [older line30 packet](../line30-benchmark/README.md) has two
source-hash mismatches and remains historical.

The cable-capstan **analysis anchor** has planning base installed capital
**$737.991 million ($24.600 million/route-km)** and 30-year whole-life NPV
**$1.568 billion**. The coupled low/base/high capital sensitivities are
$205.438m/$737.991m/$3,661.546m; these are not probability bounds. At 276
normal places/train and 30 trains/hour, the base capital is about **$89,129
per offered peak place/hour/direction**. The conditional schedule uses 45
active plus seven reserve trainsets. Complete installed mass, actual traction
force, independent braking, recovery, turnback conflicts and charging duty
remain open. The 35 kW/car auxiliary case relies on additional terminal
charging; its 35 s per-leg energy balance fails in the current packet. This
is not an operating or physical acceptance.

Lifecycle cost per **actual passenger-km** is unknown without patronage and
occupancy. The earlier roughly 700-place train would offer roughly 21,000
places/hour at the same 120 s headway; spacing it at 300 s would offer roughly
8,400 but violate this benchmark's maximum headway. It needs a distinct
formation, platform, fleet and service evaluation before cost comparison.

## Equal-service architecture screen

| Family | Current evidence | Decision |
|---|---|---|
| Station-powered passive wheels | [36 bounded local-leg cases](evidence/station-power-20261117-a/README.md) vary 1.5/2/3 km spacing, 0/1/2% uphill grade and 250/500 m launch commands. A 3 km +1% or +2% leg stalls with either command; a 2 km +2% leg stalls. No installed force/current/thermal map or complete cost. | Retain as reference hypothesis for level or shorter/graded route studies. Reject those tested long uphill legs under the stated cap. Do not select an installed drive. |
| Powered wheels | Demand trajectories reach the tested targets analytically, but the 0.1 adhesion hypothesis fails the optimistic driven-axle floor in several adverse-grade cases. Motor, gearbox, inverter, store/feed, cooling, protection, bogie mass and cost are uncounted. | Research candidate only; no equal-scope installed or whole-life price. |
| Ferrite-assisted support | [Ferrite audit](evidence/ferrite-20261117-a/result.json) retains candidate `a79a21a0767355fcb6518471769e532a04e2e23f4bd33db90968ef4a385df5bd`. Its counted tare is 25.619 t/car, not complete installed mass; sampled support/propulsion and M8 splice screens fail. A later 8,280-capacity arithmetic study uses a **different NdFeB** candidate `957f7e4e2e0e98b575810fb0c568554968fc1eb0715fb673827a16bcf63d400b`. | Ineligible for a same-candidate 30 km price or service claim; retain as research. |

An independent necessary energy check confirms the most important station
screen. At the 20 m/s cap, ideal coast up a 1% grade can gain at most
`v²/(2g) = 20.39 m` of height, even with zero resistance or braking reserve.
After a 500 m launch in a 3 km leg, 2.5 km of 1% uphill track rises 25 m;
the train cannot reach the receiving station by coasting. This confirms the
failure without relying on the detailed drag model. The same bound is even
stronger at 2% grade. It does **not** disqualify the level synthetic route or
establish the performance of an actual installed drive.

Independent friction braking at 0.6 m/s² needs an optimistic adhesion floor
near 0.063 on level track and 0.083 on a 2% descent, under uniform axle load
and no extra installed mass. The campaign's 0.05 hypothesis does not meet that
floor. Actual adhesion, parking, emergency stopping, failed-stator recovery
and repeated 120 s electrothermal duty require measurement and review.

## A civil sequence worth building and measuring

The [civil packet](evidence/civil-20261117-box20-segmented-001/README.md)
defines a **separate physical candidate**
`abcf7e942fd1337c9872869d684ac9a8055ce94bd3e9c35de0dbcbe07f49ac82`:
two 10 m match-cast box segments per 20 m span, a keyed joint and continuous
post-tension proposal, braced temporary midspan tower, independent 8 m piers
and 3 m square spread footings on a *hypothetical* 200 kPa soil. Its evaluation
is `79b896dc9517a00414245af473411b675f8eb03898788897812fa2d949458367`.
The whole 20 m beam's 59.18 t bare stock exceeds the declared 35 t road and
60 t hook-at-12 m screens; each proposed 10 m piece is 29.59 t bare with a
34.20 t provisional hook requirement. The 3 m footing has a 167.37 kPa
gravity-only pressure hypothesis: it passes 200 kPa and fails 100 kPa.

| Quantity | 2 km, two-track demonstrator | 30 km extrapolation |
|---|---:|---:|
| 20 m beam spans | 200 | 3,000 |
| Independent piers and footings | 202 | 3,002 |
| 10 m segment lifts | 400 | 6,000 |
| Bearing packages | 800 | 12,000 |
| Beam concrete | 4,456 m³ | 66,845 m³ |
| Declared direct fastener sets | 14,000 | 210,000 |

The illustrative one-crane, two-shift **100 workdays for the 2 km lifts** is
only lift throughput; cure, foundations, rail, access, utilities, restrictions
and interruptions are not included. The existing whole-beam process gives a
**30,448 person-hour proxy floor** for 2 km (12,800 beam factory, 12,800 site
erection, 4,848 support field hours); revised joint and temporary work, QA,
rework and local supplier capability are not measured. The fresh unsegmented Class C civil proxy
is $107.703m for 30 km ($3.590m/route-km), not a price for this segmented
candidate. Its joint, tower, extra crane cycles, temporary foundations and
site access are unpriced. Moving-load stress for the whole beam cannot qualify
the segmented joint, torsion, lifting/prop-release stages, soil, settlement or
actual crane radius. No accepted viaduct cost or construction months per km
can yet be stated.

The **1.5–2 km demonstrator** should first investigate soil and access; then
fabricate and load-test one jointed span, pier, bearing and footing; verify the
crane chart and haul route; erect a monitored span; and test rail datum,
vehicle interface, braking, protected access and repair. Count actual person
hours, rejected parts, disruption and local supplier inputs at every stage.

## One car and one removable door

The [car/door packet](evidence/car-door-bfa0991961be/result.json) proposes an
assembly, QA, removal and replacement sequence for **one research door child**
`907da3680bcbd01ffe1223652443e4e34a9f581e201385917a99edf4150bd90a`.
Its 74 part types and 694 pieces/opening include 445 mechanical and 249
electrical pieces, ten bearings, 134 bolt/nut pairs, 268 washers, two drag
chains and three looms. The 2.9 m guide minus 1.4 m opening and two 0.72 m
nominal leaf travels leaves only **60 mm arithmetic stock**, not verified stop,
seal or service clearance. The $2,093.78/opening base figure is a provisional
direct component allowance for this child, not the selected reference's
installed cost. It cannot be multiplied into the reference fleet.

Release one full-size opening only after controlled mating datums and
tolerances, finite motion/tool/removal envelopes, installed mass/CG, electrical
ratings and thermal duty, approved obstruction/release/interlock tests, and a
timed local replacement with post-repair QA. The make/buy counts (97 proposed
local-fabricate, 568 buy-standard and 29 buy-qualified pieces) are **not** a
domestic value fraction. Material-only value, fabrication/QA hours, tooling,
supplier origin and maintenance intervals remain unknown.

## Decision and next evidence

No family is physically selected. Keep station-powered passive wheels as the
reference, preserve powered-wheel and ferrite Pareto research, and rank the
next experiments by their ability to close whole-railway feasibility:

1. Survey the actual Samawah and pilot station gaps, grades, access and soil.
   Keep its city edit and source epoch distinct from this synthetic benchmark.
2. Instrument one full-scale launch group and loaded passive-wheel bogie for
   force, position, current, voltage, losses, braking and hot 120 s repeated
   duty, including a failed group and rescue. Independently review calibrated
   data. This determines whether the reference can cross the actual worst leg.
3. Mock up and test the segmented joint, erection support and foundation on
   measured ground before assigning the civil cost and schedule.
4. Assemble, cycle, fault-test and replace one complete door in a real car
   opening; record installed mass, tooling, hours, origin and replacement cost.
5. Reprice all three architectures on one service, rate and scope only after
   their installed mass, civil/energy consequences and recovery are accounted.

The selected reference, synthetic price control and four research packages
remain separate. All execution packages retain input, result and logs with
SHA-256 receipts. The copied station-power receipt names its original private
`build/v07-ethos/line30-current-20261117-a` source; the identical result and
manifest bytes are published at `docs/design-engine/line30-current-20261117`.
No work here establishes physical, manufacturing, procurement or operating
acceptance.
