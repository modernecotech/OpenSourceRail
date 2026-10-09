# line-1 — foundation and assembly construction plan

Line-specific design-development package; survey, ground, supplier and staged-load releases are still required.

Route length 49.068 km. 748 unique proposed support packets; 613 identified catalogue bay assemblies and 35 special packages. Each ordinary bay has two named beam components and both foundation parents. The 25 m average is a sizing basis; actual Pi20/Pi25/closure geometry controls installation.

| Front | Launcher | Previous asset assignment | Direction | Initial assembly chainage m | Bay assemblies |
|---|---|---|---:|---:|---:|
| line-1-front-1 | launcher-01 | initial mobilisation | 1 | 388.3 | 306 |
| line-1-front-2 | launcher-02 | initial mobilisation | -1 | 44150.1 | 307 |

## Foundation workface plan

Filter [the foundation register](foundation-register.csv.gz) by `line-1`. For every support, verify the proposed coordinate/chainage, rights, utilities and the referenced desktop sample; commission field ground, groundwater, durability and load investigations. Review shallow footing, bored shaft, driven bent and pile-group alternatives against actual ground, axial/lateral/settlement/scour and construction loads. Desktop topsoil does not select a pile depth, count or allowable bearing pressure.

Release trial and working-platform design (F1), install the selected foundation with actual geometry/material/installation records (F2), then verify integrity/load/settlement/dimensions and close the foundation packet (F3). Construct/erect column and cap with independently checked connections/temporary restraint (P0). Survey and inspect bearings, strength and the next launcher/beam/delivery stage before support release (B0). Keep 10–15 consecutive bays of accepted supports and beam stock ahead only where the run and storage permit.

## Directed assembly and logistics sequence

Before mobilisation, release the predecessor asset assignment and its dismantle/transport/recommission package. The positive front installs toward increasing chainage; the negative front starts at its high-chainage end and installs backward. Factory/dispatch plans must follow this directed sequence, not the ascending raw span register. A foundation used by two bays is one packet; it is not built or priced twice.

For each front, identify the first complete run, permitted delivery/assembly site, temporary support/ground platform, configured plant and authorised shift/crew. Reserve both beam travellers, transport/receiving equipment, an operator, required riggers, lift supervision and inspection. Verify source strength, complete mass/CG, lifting points, rigging, bearings, weather limits and contingency landing/recovery before any lift.

Both support B0 packets and beam receiving H1 records precede E0. Place and restrain beam 1 (E1); then place/securing beam 2 (E2). Survey and accept connection/strength/bearings/NCRs (E3), release advance loads and the next supports before moving the launcher (E4), then complete walkways/barriers/waterproofing/drainage/track interface and following-trade handover (E5). The next bay depends on the preceding advance release. Following trades may overlap only with protected, agreed load/access boundaries.

Run boundaries, stations and specials require a passage or dismantle/transport/reassembly/recommission package. No discontinuity becomes an assumed launchable gap. Junction-affected orders remain on a design hold until J2 freezes the profile, clearance, support/cap geometry and staged-load/utility/access design. A physical crossing does not create a rail switch.

## Initial bay packages

| Front | Sequence | Span | Product | Foundation A | Foundation B | Prior span |
|---|---:|---|---|---|---|---|
| line-1-front-1 | 1 | line-1-run-0001-span-0001 | OSR-Pi20 | FND:line-1-support-000000388300 | FND:line-1-support-000000408300 | mobilisation |
| line-1-front-1 | 2 | line-1-run-0001-span-0002 | OSR-Pi20 | FND:line-1-support-000000408300 | FND:line-1-support-000000428300 | line-1-run-0001-span-0001 |
| line-1-front-1 | 3 | line-1-run-0002-span-0001 | OSR-Pi20 | FND:line-1-support-000000488300 | FND:line-1-support-000000508300 | line-1-run-0001-span-0002 |
| line-1-front-1 | 4 | line-1-run-0002-span-0002 | OSR-Pi20 | FND:line-1-support-000000508300 | FND:line-1-support-000000528300 | line-1-run-0002-span-0001 |
| line-1-front-1 | 5 | line-1-run-0003-span-0001 | OSR-Pi25 | FND:line-1-support-000000588300 | FND:line-1-support-000000613300 | line-1-run-0002-span-0002 |
| line-1-front-1 | 6 | line-1-run-0003-span-0002 | OSR-Pi20 | FND:line-1-support-000000613300 | FND:line-1-support-000000633300 | line-1-run-0003-span-0001 |
| line-1-front-2 | 1 | line-1-run-0100-span-0001 | OSR-Pi20 | FND:line-1-support-000044130100 | FND:line-1-support-000044150100 | mobilisation |
| line-1-front-2 | 2 | line-1-run-0099-span-0001 | OSR-Pi20 | FND:line-1-support-000043177000 | FND:line-1-support-000043197000 | line-1-run-0100-span-0001 |
| line-1-front-2 | 3 | line-1-run-0098-span-0001 | OSR-Pi20 | FND:line-1-support-000042948700 | FND:line-1-support-000042968700 | line-1-run-0099-span-0001 |
| line-1-front-2 | 4 | line-1-run-0097-span-0007 | OSR-Pi20 | FND:line-1-support-000042751000 | FND:line-1-support-000042771000 | line-1-run-0098-span-0001 |
| line-1-front-2 | 5 | line-1-run-0097-span-0006 | OSR-Pi20 | FND:line-1-support-000042731000 | FND:line-1-support-000042751000 | line-1-run-0097-span-0007 |
| line-1-front-2 | 6 | line-1-run-0097-span-0005 | OSR-Pi25 | FND:line-1-support-000042706000 | FND:line-1-support-000042731000 | line-1-run-0097-span-0006 |

The compressed [span register](span-assembly-register.csv.gz) provides the full sequence, individual beam IDs, predecessors and junction holds. [Stage library](assembly-stage-library.json) supplies the method dependencies. [Front package](launcher-fronts.json) lists every assigned span and actual disconnected working interval.

## Junctions, stations and residential interfaces

Coordinated structural interface IDs on this line: crossing-0e22533d0de5, crossing-1815352eca4f, crossing-407b60a66286, crossing-4761735b935e, crossing-596aa3d726d4, crossing-72821b527a76, crossing-871048252387, crossing-8b09cb5c624a, crossing-9090e87568d6, crossing-92b255c18da1, crossing-9df9935c73a6, crossing-ad1c2e226654, crossing-b0460cb8e5c1, crossing-bfde9d3d92c8, crossing-d02bcca1ecd2, crossing-d1a402d881cd, crossing-db86a48b74d8, crossing-e1b0b7941672, crossing-efa108fc0f05, crossing-f6b3b196bbdf, shared-corridor-bb8d80ba3322, shared-corridor-ea625bfc9e95.

Evaluate grade-separated crossings, shared four-track civil footprints or separate deck levels, and bounded platform/concourse/access complexes with the station authority. Freeze actual vertical profiles and gradients before selecting supports and ordinary spans. Preserve rail/PSD/egress/waterproofing/earthing interfaces. Proposed residential infill sites on this line require station/approach structures and revised service, fleet, power and full installed prices; they are not existing paid journeys.

Candidate infill IDs: infill-line-1-026000.

## Inspection, handover and programme

Use the foundation/production/lift/connection/concealed-work hold points from the master ITP. Capture installed component IDs, geometry, tests, personnel/equipment authority, NCR disposition and signed stage release. Update actual shift cycles, losses, stocks and resource reservations; do not infer an opening date from bay throughput. Station/special/track/energy/depot/fleet/testing/approval releases close the whole line. Unknown ground quantities, installed costs and dates stay unknown.

[Integrated master package](README.md) · [Interactive support/junction inspection](network-foundation-viewer.html).
