# line-8 — foundation and assembly construction plan

Line-specific design-development package; survey, ground, supplier and staged-load releases are still required.

Route length 48.137 km. 844 unique proposed support packets; 743 identified catalogue bay assemblies and 43 special packages. Each ordinary bay has two named beam components and both foundation parents. The 25 m average is a sizing basis; actual Pi20/Pi25/closure geometry controls installation.

| Front | Launcher | Previous asset assignment | Direction | Initial assembly chainage m | Bay assemblies |
|---|---|---|---:|---:|---:|
| line-8-front-1 | launcher-15 | initial mobilisation | 1 | 1198.0 | 371 |
| line-8-front-2 | launcher-16 | initial mobilisation | -1 | 47771.4 | 372 |

## Foundation workface plan

Filter [the foundation register](foundation-register.csv.gz) by `line-8`. For every support, verify the proposed coordinate/chainage, rights, utilities and the referenced desktop sample; commission field ground, groundwater, durability and load investigations. Review shallow footing, bored shaft, driven bent and pile-group alternatives against actual ground, axial/lateral/settlement/scour and construction loads. Desktop topsoil does not select a pile depth, count or allowable bearing pressure.

Release trial and working-platform design (F1), install the selected foundation with actual geometry/material/installation records (F2), then verify integrity/load/settlement/dimensions and close the foundation packet (F3). Construct/erect column and cap with independently checked connections/temporary restraint (P0). Survey and inspect bearings, strength and the next launcher/beam/delivery stage before support release (B0). Keep 10–15 consecutive bays of accepted supports and beam stock ahead only where the run and storage permit.

## Directed assembly and logistics sequence

Before mobilisation, release the predecessor asset assignment and its dismantle/transport/recommission package. The positive front installs toward increasing chainage; the negative front starts at its high-chainage end and installs backward. Factory/dispatch plans must follow this directed sequence, not the ascending raw span register. A foundation used by two bays is one packet; it is not built or priced twice.

For each front, identify the first complete run, permitted delivery/assembly site, temporary support/ground platform, configured plant and authorised shift/crew. Reserve both beam travellers, transport/receiving equipment, an operator, required riggers, lift supervision and inspection. Verify source strength, complete mass/CG, lifting points, rigging, bearings, weather limits and contingency landing/recovery before any lift.

Both support B0 packets and beam receiving H1 records precede E0. Place and restrain beam 1 (E1); then place/securing beam 2 (E2). Survey and accept connection/strength/bearings/NCRs (E3), release advance loads and the next supports before moving the launcher (E4), then complete walkways/barriers/waterproofing/drainage/track interface and following-trade handover (E5). The next bay depends on the preceding advance release. Following trades may overlap only with protected, agreed load/access boundaries.

Run boundaries, stations and specials require a passage or dismantle/transport/reassembly/recommission package. No discontinuity becomes an assumed launchable gap. Junction-affected orders remain on a design hold until J2 freezes the profile, clearance, support/cap geometry and staged-load/utility/access design. A physical crossing does not create a rail switch.

## Initial bay packages

| Front | Sequence | Span | Product | Foundation A | Foundation B | Prior span |
|---|---:|---|---|---|---|---|
| line-8-front-1 | 1 | line-8-run-0001-span-0001 | OSR-Pi25 | FND:line-8-support-000001198000 | FND:line-8-support-000001223000 | mobilisation |
| line-8-front-1 | 2 | line-8-run-0001-span-0002 | OSR-Pi25 | FND:line-8-support-000001223000 | FND:line-8-support-000001248000 | line-8-run-0001-span-0001 |
| line-8-front-1 | 3 | line-8-run-0001-span-0003 | OSR-Pi25 | FND:line-8-support-000001248000 | FND:line-8-support-000001273000 | line-8-run-0001-span-0002 |
| line-8-front-1 | 4 | line-8-run-0001-span-0004 | OSR-Pi25 | FND:line-8-support-000001273000 | FND:line-8-support-000001298000 | line-8-run-0001-span-0003 |
| line-8-front-1 | 5 | line-8-run-0002-span-0001 | OSR-Pi20 | FND:line-8-support-000002661700 | FND:line-8-support-000002681700 | line-8-run-0001-span-0004 |
| line-8-front-1 | 6 | line-8-run-0002-span-0002 | OSR-Pi20 | FND:line-8-support-000002681700 | FND:line-8-support-000002701700 | line-8-run-0002-span-0001 |
| line-8-front-2 | 1 | line-8-run-0057-span-0015 | OSR-Pi20 | FND:line-8-support-000047751400 | FND:line-8-support-000047771400 | mobilisation |
| line-8-front-2 | 2 | line-8-run-0057-span-0014 | OSR-Pi25 | FND:line-8-support-000047726400 | FND:line-8-support-000047751400 | line-8-run-0057-span-0015 |
| line-8-front-2 | 3 | line-8-run-0057-span-0013 | OSR-Pi25 | FND:line-8-support-000047701400 | FND:line-8-support-000047726400 | line-8-run-0057-span-0014 |
| line-8-front-2 | 4 | line-8-run-0057-span-0012 | OSR-Pi25 | FND:line-8-support-000047676400 | FND:line-8-support-000047701400 | line-8-run-0057-span-0013 |
| line-8-front-2 | 5 | line-8-run-0057-span-0011 | OSR-Pi25 | FND:line-8-support-000047651400 | FND:line-8-support-000047676400 | line-8-run-0057-span-0012 |
| line-8-front-2 | 6 | line-8-run-0057-span-0010 | OSR-Pi25 | FND:line-8-support-000047626400 | FND:line-8-support-000047651400 | line-8-run-0057-span-0011 |

The compressed [span register](span-assembly-register.csv.gz) provides the full sequence, individual beam IDs, predecessors and junction holds. [Stage library](assembly-stage-library.json) supplies the method dependencies. [Front package](launcher-fronts.json) lists every assigned span and actual disconnected working interval.

## Junctions, stations and residential interfaces

Coordinated structural interface IDs on this line: crossing-0fac546553f2, crossing-2fc24ae4cc22, crossing-3ba74f14bd23, crossing-5d5aa03bacda, crossing-66746bfdc84f, crossing-7d2e9a90071d, crossing-8431d2567c58, crossing-a29b35b7b219, crossing-dfea62d5d545, crossing-ec8cd65ba79b, crossing-efa108fc0f05, crossing-fb619596d7f8, shared-corridor-481ca8ac8acb.

Evaluate grade-separated crossings, shared four-track civil footprints or separate deck levels, and bounded platform/concourse/access complexes with the station authority. Freeze actual vertical profiles and gradients before selecting supports and ordinary spans. Preserve rail/PSD/egress/waterproofing/earthing interfaces. Proposed residential infill sites on this line require station/approach structures and revised service, fleet, power and full installed prices; they are not existing paid journeys.

Candidate infill IDs: infill-line-8-040000.

## Inspection, handover and programme

Use the foundation/production/lift/connection/concealed-work hold points from the master ITP. Capture installed component IDs, geometry, tests, personnel/equipment authority, NCR disposition and signed stage release. Update actual shift cycles, losses, stocks and resource reservations; do not infer an opening date from bay throughput. Station/special/track/energy/depot/fleet/testing/approval releases close the whole line. Unknown ground quantities, installed costs and dates stay unknown.

[Integrated master package](README.md) · [Interactive support/junction inspection](network-foundation-viewer.html).
