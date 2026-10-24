# Conditional service specification tradeoffs

This study compares speed, station spacing, formations and dwell at the counted
37.619 t AW3 mass per car. It extends the separate 1,349 A propulsion coupon into
an explicitly unvalidated longitudinal service model. **No operating specification
is adopted. Every candidate retains failed support, electrical, thermal and
physical acceptance gates.** Additional mass sensitivities must stay bound to
their own counted support proposal; the canonical mass cannot be substituted
into a heavier revised design.

## What was executed

[service_envelope.py](../../../../engineering/maglev_research/service_envelope.py)
reuses the repository's jerk-limited launch/coast/receiving solver, replacing the
older 26.2 t/car mass and 0.8–1.0 m/s² acceleration assumptions. Its inputs are:

- Actual canonical comparison mass and the conditional 10.092 kN/car field result.
- Six-car spacing comparisons at 0.75, 1, 1.5, 2, 3 and 5 km; speed caps of
  8, 10, 12, 15 and 20 m/s; net acceleration of 0.15 or 0.2 m/s².
- Eight-, ten- and twelve-car repeated-car sensitivities at 0.75/1 km, plus
  twelve cars at 1.5/2 km. The car, coupler pitch, passenger count, train mass,
  powered extent, platform length and clearance time increase together.
- Dwell of 30, 45 or 60 s and charging input of 240, 400 or 600 kW/car.
- A 60–600 s runtime grid in 10 s steps. The first feasible runtime satisfying
  the declared maximum 50% powered-length comparison is retained for each profile.

The canonical-mass sweep executes **3,028 runtime attempts, 116 retained motion
profiles and 1,044 dwell/charging variants**. There are **352 conditional
longitudinal/services passes**, and 107 reach the reference capacity floor.
These counts exclude the separate higher-mass sensitivity.

The existing six-car normal reference is 720 AW2 passengers at 180 s headway:
**14,400 passengers/hour/direction**. It is the comparison floor, not an accepted
operating capacity. AW3 counts remain separate. No 20,000-passenger normal-service
requirement is invented.

## Capacity and simplicity comparison

Each row below passes the limited longitudinal, recharge and services-reserve
screens at canonical comparison mass. None passes complete engineering gates.
The twelve-car row is a research target for fewer station sites and installed
platform metres; the ten-car row is the least formation reaching the capacity
floor. Supplier prices and route/site evidence are insufficient to select a
total-cost optimum.

| Comparison | Six cars, 1 km | Ten cars, 1 km | Twelve cars, 1.5 km |
|---|---:|---:|---:|
| Train envelope | 104.5 m | 174.5 m | 209.5 m |
| AW2 passengers/train | 720 | 1,200 | 1,440 |
| Speed cap | 10 m/s | 10 m/s | 12 m/s |
| Run / dwell | 160 / 30 s | 170 / 30 s | 200 / 45 s |
| Exclusive-block headway lower bound | 262.96 s | 279.45 s | 333.73 s |
| Conditional AW2 passengers/hour/direction | 9,857 | 15,459 | 15,533 |
| Station sites/route-km | 1.00 | 1.00 | 0.667 |
| Platforms, both directions/route-km | 209 m | 349 m | 279 m |
| Winding length/direction/station | 480 m | 470 m | 725 m |
| Powered direction-metres/route-km | 480 m | 470 m | 483 m |
| Charging input per connected train | 3.6 MW | 6.0 MW | 7.2 MW |
| Installed charging input, both directions/route-km | 7.2 MW | 12.0 MW | 9.6 MW |
| Commercial speed including dwell | 18.95 km/h | 18.00 km/h | 22.04 km/h |

Higher instantaneous charging power is required when dwell is shortened. This
comparison assumes charging is connected for 75% of dwell with 90% conversion,
and subtracts the live hotel load before replenishing the battery. The original
30 kWh/car battery's end-of-life normal SOC window must cover the complete
unconnected journey plus the retained ten-minute hot-services reserve. A short
dwell without sufficient charging fails rather than receiving free energy.

The extra cars are not free capacity. They require longer platforms, longer
tail clearance, more charging equipment, more vehicle mass and longer local
winding exposure. Their six-car structural, dynamics and protection evidence
is not inherited.

## Powered length and local duty

The geometry calculation rounds to whole 5 m groups and contains the complete
formation throughout both powered phases. It is a sufficient full-engagement
construction bound, not an optimised minimum winding length. All selected
station-only cases retain an unpowered interval and use zero midpoint boosters.
The older 200/350 m winding cases and suburban booster calculations do not supply
current-candidate force credit.

The selected rows require roughly **47–48% of each direction's route length to
be powered**, far above the visual impression of a short station-only launch
strip. This is a material cost/simplicity concern. The disclosed stator target
is a quantity sensitivity at the old unquoted rate; it excludes complete
converters, phase routing, cooling, civil work, access, grid and fleet costs.

For thermal duty, the study samples each 5 m group as every car passes it during
arrival and departure. A declared uniform current follows the actual prescribed
force demand. This is a finite-overlap allocation hypothesis; it is not executed
harmonic field, inverter or Rust current control. Copper energy is summed from
each group's current-squared exposure. The older fixed station efficiency is
not reused as an electrical loss map.

The worst group's equivalent full-current pulse substantially exceeds the
earlier 5 s propulsion coupon. **Every retained service profile fails the
forty-cycle no-cooling copper screen.** For the ten-car and twelve-car examples,
the necessary mean heat-rejection lower bounds are approximately **59.0 and
54.1 W/K per worst group**, using minimum 40°C resistance and the largest
permitted 80 K cooling gradient. Separate mean-load design screens using 120°C
resistance require approximately **76.1 and 69.9 W/K**. These do not establish transient peak temperatures,
thermal equilibrium, measured cooling, insulation life or installed cooling mass.

The inherited 5% uphill grade case also fails the necessary zero-acceleration
force screen. Shorter spacing and lower speed cannot remove its gravity load.
The grade requirement is retained; no route is silently flattened to claim a pass.

## Protection and selection boundaries

The headway retains an exclusively reserved whole leg and receiving berth until
the complete formation tail clears the downstream winding plus 75 m, then adds
the 5 s release allowance. Travel, dwell and the next departure's actual
full-tail clearance time all contribute. The timing is a lower bound; it proves
neither train integrity nor detection.

Six and eight cars do not reach the 14,400 AW2 comparison floor in this bounded
station-only search. Repeated cars and longer platforms offer a simple
conditional alternative to reducing protected headway. Progressive release
could be a separate study after independent braking, integrity, detectors and
distributed authority are qualified; it supplies no capacity credit here.

The machine-readable report preserves a Pareto comparison of station sites,
powered length, platform length, installed charging input and hotel-plus-copper
energy per AW2 capacity-passenger-km. The research ranking first requires the
capacity floor, then favours fewer station sites and platform metres. It keeps
the least-formation alternative visible and sets `selection_is_total_cost_optimum`
to false. It cannot select a physical product while support and duty fail.

## Separately counted support-mass sensitivity

The [separate mass report](service-envelope-proposed-mass.json) uses exactly
**54,469.347469542154 kg AW3/car**, taken from the
[support architecture contract](support-architecture.json), case
`separate-guidance-03`. Its source-file and contract hashes are retained. This
is an optimistic material lower bound for thirty support modules and six
separate guidance units per car. The guidance field/MMF calculation is not a
validated steel/leakage map, and installed body carriers, controls, cooling and
interfaces remain incomplete. The service calculation does not turn it into
an integrated candidate.

The heavier sweep samples accelerations of 0.10, 0.125, 0.15 and 0.175 m/s².
It executes 8,289 runtime attempts, retains 190 motion profiles and compares
1,710 dwell/charging variants. There are 432 conditional longitudinal/services
passes and 45 capacity-floor passes; none closes the thermal/support gates.

Its station-site-priority research target changes to **twelve cars, 1 km
spacing, 8 m/s cap, 0.125 m/s² acceleration, 0.2 m/s² deceleration, 200 s run and
45 s dwell**. The full-tail headway lower bound is 350.365 s, yielding about
**14,796 AW2 passengers/hour/direction**. This requires a 209.5 m train envelope,
653.632 t of repeated AW3 comparison mass, 7.2 MW charging input per connected
train and 500 m of winding per direction per station. Half the direction's
route length is powered under this sufficient full-engagement construction.
This is not evidence of a compact, cheap or accepted installation.

The higher-mass proposal therefore cannot inherit the lighter 1.5 km/12 m/s
result. Its winding duty still fails the forty-cycle no-cooling screen. Its
worst group has a 51.77 s equivalent full-current pulse, a necessary 72.0 W/K
mean heat-rejection lower bound and a separate 93.0 W/K hot-load screen. None
is a completed cooling design. The 5% uphill comparison requires 27.717 kN/car
even before acceleration, against the conditional 10.092 kN/car. At the selected
acceleration and speed cap it requires 34.641 kN/car; the necessary maximum-grade
force bound is only about 0.406%. Any lower-grade
restriction would be an explicit product/site change; the report exposes the
maximum-grade necessary force bound at the selected acceleration and speed
rather than deleting the existing grade comparison.

## Reproduce

```bash
tools/automation/osr-python -m engineering.maglev_research.service_envelope
tools/automation/osr-python -m pytest -q engineering/maglev_research/tests/test_service_envelope.py
```

For an exact separately counted mass, use `--comparison-mass-kg` and
`--accelerations-m-s2 0.1 0.125 0.15 0.175`, writing to a separate output with
`--output`. The result explicitly labels caller-provided mass as an unadopted
sensitivity. It must be matched to the corresponding magnetic/support receipt;
it does not reconcile missing retention, controls, cooling or installed interfaces.
