# line-46 — foundation and assembly construction plan

Line-specific design-development package; survey, ground, supplier and staged-load releases are still required.

Route length 7.287 km. 215 unique proposed support packets; 203 identified catalogue bay assemblies and 5 special packages. Each ordinary bay has two named beam components and both foundation parents. The 25 m average is a sizing basis; actual Pi20/Pi25/closure geometry controls installation.

| Front | Launcher | Previous asset assignment | Direction | Initial assembly chainage m | Bay assemblies |
|---|---|---|---:|---:|---:|
| line-46-front-1 | launcher-01 | line-37-front-1 | 1 | 210.5 | 101 |
| line-46-front-2 | launcher-02 | line-37-front-2 | -1 | 7052.5 | 102 |

## Foundation workface plan

Filter [the foundation register](foundation-register.csv.gz) by `line-46`. For every support, verify the proposed coordinate/chainage, rights, utilities and the referenced desktop sample; commission field ground, groundwater, durability and load investigations. Review shallow footing, bored shaft, driven bent and pile-group alternatives against actual ground, axial/lateral/settlement/scour and construction loads. Desktop topsoil does not select a pile depth, count or allowable bearing pressure.

Release trial and working-platform design (F1), install the selected foundation with actual geometry/material/installation records (F2), then verify integrity/load/settlement/dimensions and close the foundation packet (F3). Construct/erect column and cap with independently checked connections/temporary restraint (P0). Survey and inspect bearings, strength and the next launcher/beam/delivery stage before support release (B0). Keep 10–15 consecutive bays of accepted supports and beam stock ahead only where the run and storage permit.

## Directed assembly and logistics sequence

Before mobilisation, release the predecessor asset assignment and its dismantle/transport/recommission package. The positive front installs toward increasing chainage; the negative front starts at its high-chainage end and installs backward. Factory/dispatch plans must follow this directed sequence, not the ascending raw span register. A foundation used by two bays is one packet; it is not built or priced twice.

For each front, identify the first complete run, permitted delivery/assembly site, temporary support/ground platform, configured plant and authorised shift/crew. Reserve both beam travellers, transport/receiving equipment, an operator, required riggers, lift supervision and inspection. Verify source strength, complete mass/CG, lifting points, rigging, bearings, weather limits and contingency landing/recovery before any lift.

Both support B0 packets and beam receiving H1 records precede E0. Place and restrain beam 1 (E1); then place/securing beam 2 (E2). Survey and accept connection/strength/bearings/NCRs (E3), release advance loads and the next supports before moving the launcher (E4), then complete walkways/barriers/waterproofing/drainage/track interface and following-trade handover (E5). The next bay depends on the preceding advance release. Following trades may overlap only with protected, agreed load/access boundaries.

Run boundaries, stations and specials require a passage or dismantle/transport/reassembly/recommission package. No discontinuity becomes an assumed launchable gap. Junction-affected orders remain on a design hold until J2 freezes the profile, clearance, support/cap geometry and staged-load/utility/access design. A physical crossing does not create a rail switch.

## Initial bay packages

| Front | Sequence | Span | Product | Foundation A | Foundation B | Prior span |
|---|---:|---|---|---|---|---|
| line-46-front-1 | 1 | line-46-run-0001-span-0001 | OSR-Pi25 | FND:line-46-support-000000210500 | FND:line-46-support-000000235500 | mobilisation |
| line-46-front-1 | 2 | line-46-run-0001-span-0002 | OSR-Pi25 | FND:line-46-support-000000235500 | FND:line-46-support-000000260500 | line-46-run-0001-span-0001 |
| line-46-front-1 | 3 | line-46-run-0001-span-0003 | OSR-Pi25 | FND:line-46-support-000000260500 | FND:line-46-support-000000285500 | line-46-run-0001-span-0002 |
| line-46-front-1 | 4 | line-46-run-0001-span-0004 | OSR-Pi25 | FND:line-46-support-000000285500 | FND:line-46-support-000000310500 | line-46-run-0001-span-0003 |
| line-46-front-1 | 5 | line-46-run-0001-span-0005 | OSR-Pi25 | FND:line-46-support-000000310500 | FND:line-46-support-000000335500 | line-46-run-0001-span-0004 |
| line-46-front-1 | 6 | line-46-run-0001-span-0006 | OSR-Pi25 | FND:line-46-support-000000335500 | FND:line-46-support-000000360500 | line-46-run-0001-span-0005 |
| line-46-front-2 | 1 | line-46-run-0007-span-0041 | OSR-Pi20 | FND:line-46-support-000007032500 | FND:line-46-support-000007052500 | mobilisation |
| line-46-front-2 | 2 | line-46-run-0007-span-0040 | OSR-Pi20 | FND:line-46-support-000007012500 | FND:line-46-support-000007032500 | line-46-run-0007-span-0041 |
| line-46-front-2 | 3 | line-46-run-0007-span-0039 | OSR-Pi20 | FND:line-46-support-000006992500 | FND:line-46-support-000007012500 | line-46-run-0007-span-0040 |
| line-46-front-2 | 4 | line-46-run-0007-span-0038 | OSR-Pi20 | FND:line-46-support-000006972500 | FND:line-46-support-000006992500 | line-46-run-0007-span-0039 |
| line-46-front-2 | 5 | line-46-run-0007-span-0037 | OSR-Pi25 | FND:line-46-support-000006947500 | FND:line-46-support-000006972500 | line-46-run-0007-span-0038 |
| line-46-front-2 | 6 | line-46-run-0007-span-0036 | OSR-Pi25 | FND:line-46-support-000006922500 | FND:line-46-support-000006947500 | line-46-run-0007-span-0037 |

The compressed [span register](span-assembly-register.csv.gz) provides the full sequence, individual beam IDs, predecessors and junction holds. [Stage library](assembly-stage-library.json) supplies the method dependencies. [Front package](launcher-fronts.json) lists every assigned span and actual disconnected working interval.

## Junctions, stations and residential interfaces

Coordinated structural interface IDs on this line: crossing-25b49b2a306f, crossing-2fc24ae4cc22, crossing-33f2a480fa97, crossing-637dbe02d6ea, crossing-9f7462dc27fd, crossing-d1a402d881cd, crossing-d5de9d7a53bc, shared-corridor-1ac72abd9fa1, shared-corridor-2e08739e65b5, shared-corridor-47c7ed879b84, shared-corridor-abc9b4f0e145.

Evaluate grade-separated crossings, shared four-track civil footprints or separate deck levels, and bounded platform/concourse/access complexes with the station authority. Freeze actual vertical profiles and gradients before selecting supports and ordinary spans. Preserve rail/PSD/egress/waterproofing/earthing interfaces. Proposed residential infill sites on this line require station/approach structures and revised service, fleet, power and full installed prices; they are not existing paid journeys.

Candidate infill IDs: no qualifying candidate under this screen.

## Inspection, handover and programme

Use the foundation/production/lift/connection/concealed-work hold points from the master ITP. Capture installed component IDs, geometry, tests, personnel/equipment authority, NCR disposition and signed stage release. Update actual shift cycles, losses, stocks and resource reservations; do not infer an opening date from bay throughput. Station/special/track/energy/depot/fleet/testing/approval releases close the whole line. Unknown ground quantities, installed costs and dates stay unknown.

[Integrated master package](README.md) · [Interactive support/junction inspection](network-foundation-viewer.html).
