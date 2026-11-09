# Samawah acceleration sensitivity

This bounded study recalculates the Samawah five-line outline at 0.4, 0.6 and
0.8 m/s². The 0.4 m/s² result reproduces the retained outline evaluation;
0.6 and 0.8 are distinct evaluations of the same physical city/body candidate.
The reference configuration, mapped geometry, demand cases and headway inputs
are unchanged. This does not select an acceleration or drive architecture.

| Acceleration hypothesis | Conditional base trainsets | Normal-base translational inertia force | Power at 20 m/s |
| ---: | ---: | ---: | ---: |
| 0.4 m/s² | 59 | 60.13 kN | 1.203 MW |
| 0.6 m/s² | 59 | 90.19 kN | 1.804 MW |
| 0.8 m/s² | 56 | 120.25 kN | 2.405 MW |

Fleet counts sum per-line requests under the declared schedule model. They do
not establish a deliverable timetable. The force calculation is `F = m a`;
power is `P = F v` at a declared 20 m/s (72 km/h) speed cap. This speed is an
evaluation point, not an achieved speed on every leg. The values omit grade,
rolling and aerodynamic resistance, rotating inertia, jerk,
drivetrain/electrical losses, adhesion and thermal limits. They are not a full
traction requirement or a universal lower bound on actual traction under
signed grade and other forces.

The study does not provide an available-force map, braking map, installed train
mass, cost-complete estimate or physically validated service. It therefore
cannot show that the faster hypotheses are attainable or cheaper. The same
79.977 m station-marker conflict against a 120 m platform request remains in
all three evaluations. All engineering, service, cost, manufacturing, physical
and operating acceptance flags remain false.

The packet records a 6.51 s bounded run with 305,052 KiB peak child RSS, a
60 s CPU limit, 1 GiB address-space limit and 60 s wall timeout. No native CAD,
FEM or drive solver ran. The process had Linux child resource limits; the source
tree was writable, so no OS read-only isolation is claimed. The retained
0.4 m/s² source evaluation is `0b1715bb…`; the new study evaluation is
`7c45c16f…`. The producer commit recorded in the run was
`615f50fd6a6a73db32a0dffa4682a86d83920224`, cherry-picked into this closure
branch as `0363194241`; the source file contents are unchanged.

The sealed [run packet](samawah-acceleration-sensitivity/manifest.json)
preserves all exact inputs, outputs and logs. A regression test checks its
hashes, identities, nine mass cases per hypothesis, original control reference
and false acceptance flags. The original Samawah adapter packet remains
separate at [its recalculation record](samawah-city-recalculation.md).
