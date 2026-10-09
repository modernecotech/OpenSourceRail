# line-4 — foundation and assembly construction plan

Line-specific design-development package; survey, ground, supplier and staged-load releases are still required.

Route length 41.932 km. 946 unique proposed support packets; 847 identified catalogue bay assemblies and 43 special packages. Each ordinary bay has two named beam components and both foundation parents. The 25 m average is a sizing basis; actual Pi20/Pi25/closure geometry controls installation.

| Front | Launcher | Previous asset assignment | Direction | Initial assembly chainage m | Bay assemblies |
|---|---|---|---:|---:|---:|
| line-4-front-1 | launcher-07 | initial mobilisation | 1 | 220.0 | 423 |
| line-4-front-2 | launcher-08 | initial mobilisation | -1 | 41503.5 | 424 |

## Foundation workface plan

Filter [the foundation register](foundation-register.csv.gz) by `line-4`. For every support, verify the proposed coordinate/chainage, rights, utilities and the referenced desktop sample; commission field ground, groundwater, durability and load investigations. Review shallow footing, bored shaft, driven bent and pile-group alternatives against actual ground, axial/lateral/settlement/scour and construction loads. Desktop topsoil does not select a pile depth, count or allowable bearing pressure.

Release trial and working-platform design (F1), install the selected foundation with actual geometry/material/installation records (F2), then verify integrity/load/settlement/dimensions and close the foundation packet (F3). Construct/erect column and cap with independently checked connections/temporary restraint (P0). Survey and inspect bearings, strength and the next launcher/beam/delivery stage before support release (B0). Keep 10–15 consecutive bays of accepted supports and beam stock ahead only where the run and storage permit.

## Directed assembly and logistics sequence

Before mobilisation, release the predecessor asset assignment and its dismantle/transport/recommission package. The positive front installs toward increasing chainage; the negative front starts at its high-chainage end and installs backward. Factory/dispatch plans must follow this directed sequence, not the ascending raw span register. A foundation used by two bays is one packet; it is not built or priced twice.

For each front, identify the first complete run, permitted delivery/assembly site, temporary support/ground platform, configured plant and authorised shift/crew. Reserve both beam travellers, transport/receiving equipment, an operator, required riggers, lift supervision and inspection. Verify source strength, complete mass/CG, lifting points, rigging, bearings, weather limits and contingency landing/recovery before any lift.

Both support B0 packets and beam receiving H1 records precede E0. Place and restrain beam 1 (E1); then place/securing beam 2 (E2). Survey and accept connection/strength/bearings/NCRs (E3), release advance loads and the next supports before moving the launcher (E4), then complete walkways/barriers/waterproofing/drainage/track interface and following-trade handover (E5). The next bay depends on the preceding advance release. Following trades may overlap only with protected, agreed load/access boundaries.

Run boundaries, stations and specials require a passage or dismantle/transport/reassembly/recommission package. No discontinuity becomes an assumed launchable gap. Junction-affected orders remain on a design hold until J2 freezes the profile, clearance, support/cap geometry and staged-load/utility/access design. A physical crossing does not create a rail switch.

## Initial bay packages

| Front | Sequence | Span | Product | Foundation A | Foundation B | Prior span |
|---|---:|---|---|---|---|---|
| line-4-front-1 | 1 | line-4-run-0001-span-0001 | OSR-Pi25 | FND:line-4-support-000000220000 | FND:line-4-support-000000245000 | mobilisation |
| line-4-front-1 | 2 | line-4-run-0001-span-0002 | OSR-Pi25 | FND:line-4-support-000000245000 | FND:line-4-support-000000270000 | line-4-run-0001-span-0001 |
| line-4-front-1 | 3 | line-4-run-0002-span-0001 | OSR-Pi25 | FND:line-4-support-000000421400 | FND:line-4-support-000000446400 | line-4-run-0001-span-0002 |
| line-4-front-1 | 4 | line-4-run-0002-span-0002 | OSR-Pi20 | FND:line-4-support-000000446400 | FND:line-4-support-000000466400 | line-4-run-0002-span-0001 |
| line-4-front-1 | 5 | line-4-run-0003-span-0001 | OSR-Pi25 | FND:line-4-support-000000546300 | FND:line-4-support-000000571300 | line-4-run-0002-span-0002 |
| line-4-front-1 | 6 | line-4-run-0003-span-0002 | OSR-Pi25 | FND:line-4-support-000000571300 | FND:line-4-support-000000596300 | line-4-run-0003-span-0001 |
| line-4-front-2 | 1 | line-4-run-0056-span-0001 | OSR-Pi20 | FND:line-4-support-000041483500 | FND:line-4-support-000041503500 | mobilisation |
| line-4-front-2 | 2 | line-4-run-0055-span-0001 | OSR-Pi20 | FND:line-4-support-000041129000 | FND:line-4-support-000041149000 | line-4-run-0056-span-0001 |
| line-4-front-2 | 3 | line-4-run-0054-span-0001 | OSR-Pi20 | FND:line-4-support-000040884100 | FND:line-4-support-000040904100 | line-4-run-0055-span-0001 |
| line-4-front-2 | 4 | line-4-run-0053-span-0001 | OSR-Pi20 | FND:line-4-support-000040416400 | FND:line-4-support-000040436400 | line-4-run-0054-span-0001 |
| line-4-front-2 | 5 | line-4-run-0052-span-0071 | OSR-Pi20 | FND:line-4-support-000039573600 | FND:line-4-support-000039593600 | line-4-run-0053-span-0001 |
| line-4-front-2 | 6 | line-4-run-0052-span-0070 | OSR-Pi25 | FND:line-4-support-000039548600 | FND:line-4-support-000039573600 | line-4-run-0052-span-0071 |

The compressed [span register](span-assembly-register.csv.gz) provides the full sequence, individual beam IDs, predecessors and junction holds. [Stage library](assembly-stage-library.json) supplies the method dependencies. [Front package](launcher-fronts.json) lists every assigned span and actual disconnected working interval.

## Junctions, stations and residential interfaces

Coordinated structural interface IDs on this line: crossing-27b707b08a14, crossing-29f65146d943, crossing-2cd78af36d86, crossing-38043ef346b7, crossing-42edbb5cfef1, crossing-4761735b935e, crossing-533fe4b534c7, crossing-5ce92b061b8f, crossing-6aafe581d54d, crossing-6f9463d5811f, crossing-954a77cefa6e, crossing-a79096d48aef, crossing-b47e01760ef9, crossing-b75f3098835f, crossing-dff9d62fd115, crossing-ef8e24702d34, shared-corridor-00a69a0771f9, shared-corridor-778011491f44, shared-corridor-dfe22d17b401.

Evaluate grade-separated crossings, shared four-track civil footprints or separate deck levels, and bounded platform/concourse/access complexes with the station authority. Freeze actual vertical profiles and gradients before selecting supports and ordinary spans. Preserve rail/PSD/egress/waterproofing/earthing interfaces. Proposed residential infill sites on this line require station/approach structures and revised service, fleet, power and full installed prices; they are not existing paid journeys.

Candidate infill IDs: infill-line-4-023500, infill-line-4-003500.

## Inspection, handover and programme

Use the foundation/production/lift/connection/concealed-work hold points from the master ITP. Capture installed component IDs, geometry, tests, personnel/equipment authority, NCR disposition and signed stage release. Update actual shift cycles, losses, stocks and resource reservations; do not infer an opening date from bay throughput. Station/special/track/energy/depot/fleet/testing/approval releases close the whole line. Unknown ground quantities, installed costs and dates stay unknown.

[Integrated master package](README.md) · [Interactive support/junction inspection](network-foundation-viewer.html).
