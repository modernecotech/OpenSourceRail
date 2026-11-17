# Proposed 1.5–2 km demonstrator propulsion screen

**Decision state:** analytical demand only. The selected six-car passive-wheel
vehicle remains physical candidate
`756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`.
The three railway layouts in [comparison.json](comparison.json) have separate
research configuration IDs. None is an installed propulsion selection or an
accepted stopping system. Evaluation
`2bd76c62dcb510678a1366b685a4843077cb0fadaa6bc07c3cbb3f28797e52a0`
is bound to the [explicit input](input.json) and five producer/source hashes.

The local leg uses the same **accounted, incomplete** 22,672 kg/car normal load
and 1,770 kg/car rotating-equivalent inertia for all three comparisons. It
retains six 17 m cars, 276 normal places, 72 km/h cap, 0.4 m/s² commanded
acceleration, 0.6 m/s² independent stopping target, 35 s dwell hypothesis and
120 s nominal headway. The synthetic constant-grade sensitivities do **not**
define a surveyed route or demonstrate 8,280 places/hour/direction. A 120 s
headway does not require every interstation journey to take less than 120 s;
separation, dwell, fleet and turnback still need a timetable and control design.

| 2 km uphill grade | Station 500 m only | Station 500 m + 250 m mid-route booster | 24-axle powered-wheel demand |
|---:|---:|---:|---:|
| Level | Reaches, 147.4 s | Reaches, 143.3 s | Reaches, 141.7 s |
| 1% | Reaches, 186.6 s | Reaches, 147.8 s | Reaches, 141.7 s |
| 2% | Stalls at 1,405 m | Reaches, 160.6 s | Reaches, 141.7 s |

The same 250 m booster reaches the analytical target on the 1.5 km, 2% leg;
station-only stalls there. At 2 km and 2%, the demanded train peaks are
93.3 kN and 1.87 MW mechanical under the common acceleration command. These
are **required**, not measured available force or electrical ratings. The
booster layout declares 750 m of full-engagement powered windows in total;
actual stator length, train overlap, supports and feeders need separate
geometry. Energy fields for stalled cases stop at the stall and are not
whole-trip energy comparisons.

All layouts fail the inherited independent-brake adhesion hypothesis as a
*necessary-bound screen*: optimistic uniform-axle minima for 0.6 m/s² are
μ=0.0632 on level and μ=0.0832 on a 2% downgrade, above the inherited μ=0.05.
This does not reject a rail/track brake or a measured higher-adhesion design.
It prevents a physical selection until full-load, faulted and hot stops,
parking and protected tow are demonstrated. The powered-wheel 24-axle traction
floor is μ=0.0633 at +2% with ideal equal axle loading; added motors, bogies,
power supply and load transfer are still unknown.

**Next experiment:** advance the station-plus-booster concept to a full-scale
moving-force and receiving-brake test, while retaining powered wheels as an
alternative. Measure entry/centre/exit thrust and ripple with phase registration,
winding R/L/flux, converter current/voltage, feeder/return losses, 120 s repeated
hot duty, lost group and cooling faults, independent brake and parking, energy
sink and protected tow. Count every installed power/protection/cooling item and
its mass, cost, origin and repair method. A surveyed alignment and its two-way
grade profile are needed before choosing the 1.5–2 km installation. No capital
or lifecycle cost ranking is made while these quantities are unknown.

## One station equipment quotation request

The [station launch/brake module schedule](station-module.json) binds one
directional departure berth, its 500 m commanded launch, one 250 m mid-route
booster extension and a 350 m receiving reservation to booster research
configuration `d1fec49310ae06beca16dd4fe4138b075f3b1c81476faae18c9df0877bdb7033`.
It copies selected vehicle fin dimensions and nominal rail/primary clearances,
lists eight equipment groups and gives a staged assembly, inspection and test
sequence. Actual stator length and count, converter ratings, brake hardware,
mounting tolerances, supplier masses and the **single installed price** remain
null until supplier and site inputs exist. The schedule is a request for a
budgetary quotation, not a price or manufacturing release. Its evaluation ID is
`b67652f13daf7f2e2f9b42153e7ca29ddf9414004858a8d8807a039b95d0b691`.

The stop interface needs immediate revision: from 20 m/s a 0.6 m/s² net
deceleration requires 333.3 m before reaction distance. An illustrative,
unapproved 1 s reaction adds 20 m. If station-mounted receiving force is
available only once the entire 104.5 m train has entered, the geometric
minimum under an optimistic immediately available brake becomes **457.8 m**,
before berth tolerance, position uncertainty, brake build-up, grade variation
or civil clearance.

| Research receiving reservation | Nose-stop margin | Full-train-engagement margin |
|---:|---:|---:|
| 350 m retained | −3.3 m | −107.8 m |
| 400 m revision | +46.7 m | −57.8 m |
| 450 m revision | +96.7 m | −7.8 m |
| 550 m revision | +196.7 m | +92.2 m |

Each receiving revision has a distinct research configuration ID in the JSON.
None is selected. The 400/450 m alternatives resolve the original nose-stop
shortfall but not the full-train engagement requirement. The 550 m research
window is the first evaluated one above the 457.8 m geometric minimum, with
92.2 m **unallocated** for uncertainty and station interfaces. It is not an
approved safety margin. The receiving/berth boundary and train-tail clearance
remain undefined. The length arithmetic presumes the target brake force exists;
inherited μ=0.05 remains below the optimistic μ≈0.0832 bound on a 2% downgrade.
No station/civil quantity or price has been inherited or recalculated for the
longer reservations.

Reproduce from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m engineering.design_search.demonstrator_propulsion \
  --input docs/design-engine/v07-demonstrator-propulsion/input.json \
  --output docs/design-engine/v07-demonstrator-propulsion/comparison.json --check
PYTHONDONTWRITEBYTECODE=1 python3 -m engineering.design_search.station_module_schedule \
  --output docs/design-engine/v07-demonstrator-propulsion/station-module.json --check
```

The calculator calls the existing event-resolved
`engineering.design_search.architecture_demand.demand` for every row. It performs
no native solve and makes no physical acceptance, manufacturing release or
passenger-operation claim.
