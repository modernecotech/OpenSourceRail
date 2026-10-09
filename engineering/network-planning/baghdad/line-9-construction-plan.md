# line-9 — foundation and assembly construction plan

Line-specific design-development package; survey, ground, supplier and staged-load releases are still required.

Route length 97.684 km. 2,229 unique proposed support packets; 2,087 identified catalogue bay assemblies and 65 special packages. Each ordinary bay has two named beam components and both foundation parents. The 25 m average is a sizing basis; actual Pi20/Pi25/closure geometry controls installation.

| Front | Launcher | Direction | Initial assembly chainage m | Bay assemblies |
|---|---|---:|---:|---:|
| line-9-front-1 | launcher-17 | 1 | 0.0 | 1043 |
| line-9-front-2 | launcher-18 | -1 | 97660.1 | 1044 |

## Foundation workface plan

Filter [the foundation register](foundation-register.csv.gz) by `line-9`. For every support, verify the proposed coordinate/chainage, rights, utilities and the referenced desktop sample; commission field ground, groundwater, durability and load investigations. Review shallow footing, bored shaft, driven bent and pile-group alternatives against actual ground, axial/lateral/settlement/scour and construction loads. Desktop topsoil does not select a pile depth, count or allowable bearing pressure.

Release trial and working-platform design (F1), install the selected foundation with actual geometry/material/installation records (F2), then verify integrity/load/settlement/dimensions and close the foundation packet (F3). Construct/erect column and cap with independently checked connections/temporary restraint (P0). Survey and inspect bearings, strength and the next launcher/beam/delivery stage before support release (B0). Keep 10–15 consecutive bays of accepted supports and beam stock ahead only where the run and storage permit.

## Directed assembly and logistics sequence

The positive front installs toward increasing chainage; the negative front starts at its high-chainage end and installs backward. Factory/dispatch plans must follow this directed sequence, not the ascending raw span register. A foundation used by two bays is one packet; it is not built or priced twice.

For each front, identify the first complete run, permitted delivery/assembly site, temporary support/ground platform, configured plant and authorised shift/crew. Reserve both beam travellers, transport/receiving equipment, an operator, required riggers, lift supervision and inspection. Verify source strength, complete mass/CG, lifting points, rigging, bearings, weather limits and contingency landing/recovery before any lift.

Both support B0 packets and beam receiving H1 records precede E0. Place and restrain beam 1 (E1); then place/securing beam 2 (E2). Survey and accept connection/strength/bearings/NCRs (E3), release advance loads and the next supports before moving the launcher (E4), then complete walkways/barriers/waterproofing/drainage/track interface and following-trade handover (E5). The next bay depends on the preceding advance release. Following trades may overlap only with protected, agreed load/access boundaries.

Run boundaries, stations and specials require a passage or dismantle/transport/reassembly/recommission package. No discontinuity becomes an assumed launchable gap. Junction-affected orders remain on a design hold until J2 freezes the profile, clearance, support/cap geometry and staged-load/utility/access design. A physical crossing does not create a rail switch.

## Initial bay packages

| Front | Sequence | Span | Product | Foundation A | Foundation B | Prior span |
|---|---:|---|---|---|---|---|
| line-9-front-1 | 1 | line-9-run-0001-span-0001 | OSR-Pi25 | FND:line-9-support-000000000000 | FND:line-9-support-000000025000 | mobilisation |
| line-9-front-1 | 2 | line-9-run-0001-span-0002 | OSR-Pi25 | FND:line-9-support-000000025000 | FND:line-9-support-000000050000 | line-9-run-0001-span-0001 |
| line-9-front-1 | 3 | line-9-run-0001-span-0003 | OSR-Pi25 | FND:line-9-support-000000050000 | FND:line-9-support-000000075000 | line-9-run-0001-span-0002 |
| line-9-front-1 | 4 | line-9-run-0001-span-0004 | OSR-Pi25 | FND:line-9-support-000000075000 | FND:line-9-support-000000100000 | line-9-run-0001-span-0003 |
| line-9-front-1 | 5 | line-9-run-0001-span-0005 | OSR-Pi25 | FND:line-9-support-000000100000 | FND:line-9-support-000000125000 | line-9-run-0001-span-0004 |
| line-9-front-1 | 6 | line-9-run-0001-span-0006 | OSR-Pi25 | FND:line-9-support-000000125000 | FND:line-9-support-000000150000 | line-9-run-0001-span-0005 |
| line-9-front-2 | 1 | line-9-run-0078-span-0006 | OSR-Pi20 | FND:line-9-support-000097640100 | FND:line-9-support-000097660100 | mobilisation |
| line-9-front-2 | 2 | line-9-run-0078-span-0005 | OSR-Pi20 | FND:line-9-support-000097620100 | FND:line-9-support-000097640100 | line-9-run-0078-span-0006 |
| line-9-front-2 | 3 | line-9-run-0078-span-0004 | OSR-Pi25 | FND:line-9-support-000097595100 | FND:line-9-support-000097620100 | line-9-run-0078-span-0005 |
| line-9-front-2 | 4 | line-9-run-0078-span-0003 | OSR-Pi25 | FND:line-9-support-000097570100 | FND:line-9-support-000097595100 | line-9-run-0078-span-0004 |
| line-9-front-2 | 5 | line-9-run-0078-span-0002 | OSR-Pi25 | FND:line-9-support-000097545100 | FND:line-9-support-000097570100 | line-9-run-0078-span-0003 |
| line-9-front-2 | 6 | line-9-run-0078-span-0001 | OSR-Pi25 | FND:line-9-support-000097520100 | FND:line-9-support-000097545100 | line-9-run-0078-span-0002 |

The compressed [span register](span-assembly-register.csv.gz) provides the full sequence, individual beam IDs, predecessors and junction holds. [Stage library](assembly-stage-library.json) supplies the method dependencies. [Front package](launcher-fronts.json) lists every assigned span and actual disconnected working interval.

## Junctions, stations and residential interfaces

Coordinated structural interface IDs on this line: crossing-1c3badfbb529, crossing-1fc40bbf9e02, crossing-3ba74f14bd23, crossing-4e4707f7a13b, crossing-526dbc821706, crossing-6644faf065db, crossing-80b4593a8386, crossing-86eb625bd399, crossing-92b255c18da1, crossing-954a77cefa6e, crossing-a79096d48aef, crossing-c15126eb0d40, crossing-c7d529a495dc, crossing-d02bcca1ecd2, shared-corridor-481ca8ac8acb, shared-corridor-5c1c3ab579e9.

Evaluate grade-separated crossings, shared four-track civil footprints or separate deck levels, and bounded platform/concourse/access complexes with the station authority. Freeze actual vertical profiles and gradients before selecting supports and ordinary spans. Preserve rail/PSD/egress/waterproofing/earthing interfaces. Proposed residential infill sites on this line require station/approach structures and revised service, fleet, power and full installed prices; they are not existing paid journeys.

Candidate infill IDs: infill-line-9-075000, infill-line-9-078000, infill-line-9-013500, infill-line-9-023500, infill-line-9-007500, infill-line-9-086500, infill-line-9-026500, infill-line-9-004500, infill-line-9-096000, infill-line-9-058000, infill-line-9-037500.

## Inspection, handover and programme

Use the foundation/production/lift/connection/concealed-work hold points from the master ITP. Capture installed component IDs, geometry, tests, personnel/equipment authority, NCR disposition and signed stage release. Update actual shift cycles, losses, stocks and resource reservations; do not infer an opening date from bay throughput. Station/special/track/energy/depot/fleet/testing/approval releases close the whole line. Unknown ground quantities, installed costs and dates stay unknown.

[Integrated master package](README.md) · [Interactive support/junction inspection](network-foundation-viewer.html).
