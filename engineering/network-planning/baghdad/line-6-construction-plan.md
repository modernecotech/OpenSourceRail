# line-6 — foundation and assembly construction plan

Line-specific design-development package; survey, ground, supplier and staged-load releases are still required.

Route length 52.503 km. 787 unique proposed support packets; 689 identified catalogue bay assemblies and 47 special packages. Each ordinary bay has two named beam components and both foundation parents. The 25 m average is a sizing basis; actual Pi20/Pi25/closure geometry controls installation.

| Front | Launcher | Previous asset assignment | Direction | Initial assembly chainage m | Bay assemblies |
|---|---|---|---:|---:|---:|
| line-6-front-1 | launcher-11 | initial mobilisation | 1 | 664.3 | 344 |
| line-6-front-2 | launcher-12 | initial mobilisation | -1 | 46297.2 | 345 |

## Foundation workface plan

Filter [the foundation register](foundation-register.csv.gz) by `line-6`. For every support, verify the proposed coordinate/chainage, rights, utilities and the referenced desktop sample; commission field ground, groundwater, durability and load investigations. Review shallow footing, bored shaft, driven bent and pile-group alternatives against actual ground, axial/lateral/settlement/scour and construction loads. Desktop topsoil does not select a pile depth, count or allowable bearing pressure.

Release trial and working-platform design (F1), install the selected foundation with actual geometry/material/installation records (F2), then verify integrity/load/settlement/dimensions and close the foundation packet (F3). Construct/erect column and cap with independently checked connections/temporary restraint (P0). Survey and inspect bearings, strength and the next launcher/beam/delivery stage before support release (B0). Keep 10–15 consecutive bays of accepted supports and beam stock ahead only where the run and storage permit.

## Directed assembly and logistics sequence

Before mobilisation, release the predecessor asset assignment and its dismantle/transport/recommission package. The positive front installs toward increasing chainage; the negative front starts at its high-chainage end and installs backward. Factory/dispatch plans must follow this directed sequence, not the ascending raw span register. A foundation used by two bays is one packet; it is not built or priced twice.

For each front, identify the first complete run, permitted delivery/assembly site, temporary support/ground platform, configured plant and authorised shift/crew. Reserve both beam travellers, transport/receiving equipment, an operator, required riggers, lift supervision and inspection. Verify source strength, complete mass/CG, lifting points, rigging, bearings, weather limits and contingency landing/recovery before any lift.

Both support B0 packets and beam receiving H1 records precede E0. Place and restrain beam 1 (E1); then place/securing beam 2 (E2). Survey and accept connection/strength/bearings/NCRs (E3), release advance loads and the next supports before moving the launcher (E4), then complete walkways/barriers/waterproofing/drainage/track interface and following-trade handover (E5). The next bay depends on the preceding advance release. Following trades may overlap only with protected, agreed load/access boundaries.

Run boundaries, stations and specials require a passage or dismantle/transport/reassembly/recommission package. No discontinuity becomes an assumed launchable gap. Junction-affected orders remain on a design hold until J2 freezes the profile, clearance, support/cap geometry and staged-load/utility/access design. A physical crossing does not create a rail switch.

## Initial bay packages

| Front | Sequence | Span | Product | Foundation A | Foundation B | Prior span |
|---|---:|---|---|---|---|---|
| line-6-front-1 | 1 | line-6-run-0001-span-0001 | OSR-Pi20 | FND:line-6-support-000000664300 | FND:line-6-support-000000684300 | mobilisation |
| line-6-front-1 | 2 | line-6-run-0001-span-0002 | OSR-Pi20 | FND:line-6-support-000000684300 | FND:line-6-support-000000704300 | line-6-run-0001-span-0001 |
| line-6-front-1 | 3 | line-6-run-0001-span-0003 | OSR-Pi20 | FND:line-6-support-000000704300 | FND:line-6-support-000000724300 | line-6-run-0001-span-0002 |
| line-6-front-1 | 4 | line-6-run-0014-span-0001 | OSR-Pi20 | FND:line-6-support-000015820100 | FND:line-6-support-000015840100 | line-6-run-0001-span-0003 |
| line-6-front-1 | 5 | line-6-run-0015-span-0001 | OSR-Pi20 | FND:line-6-support-000015888400 | FND:line-6-support-000015908400 | line-6-run-0014-span-0001 |
| line-6-front-1 | 6 | line-6-run-0017-span-0001 | OSR-Pi25 | FND:line-6-support-000018353500 | FND:line-6-support-000018378500 | line-6-run-0015-span-0001 |
| line-6-front-2 | 1 | line-6-run-0051-span-0001 | OSR-Pi20 | FND:line-6-support-000046277200 | FND:line-6-support-000046297200 | mobilisation |
| line-6-front-2 | 2 | line-6-run-0050-span-0012 | OSR-Pi25 | FND:line-6-support-000046088100 | FND:line-6-support-000046113100 | line-6-run-0051-span-0001 |
| line-6-front-2 | 3 | line-6-run-0050-span-0011 | OSR-Pi25 | FND:line-6-support-000046063100 | FND:line-6-support-000046088100 | line-6-run-0050-span-0012 |
| line-6-front-2 | 4 | line-6-run-0050-span-0010 | OSR-Pi25 | FND:line-6-support-000046038100 | FND:line-6-support-000046063100 | line-6-run-0050-span-0011 |
| line-6-front-2 | 5 | line-6-run-0050-span-0009 | OSR-Pi25 | FND:line-6-support-000046013100 | FND:line-6-support-000046038100 | line-6-run-0050-span-0010 |
| line-6-front-2 | 6 | line-6-run-0050-span-0008 | OSR-Pi25 | FND:line-6-support-000045988100 | FND:line-6-support-000046013100 | line-6-run-0050-span-0009 |

The compressed [span register](span-assembly-register.csv.gz) provides the full sequence, individual beam IDs, predecessors and junction holds. [Stage library](assembly-stage-library.json) supplies the method dependencies. [Front package](launcher-fronts.json) lists every assigned span and actual disconnected working interval.

## Junctions, stations and residential interfaces

Coordinated structural interface IDs on this line: crossing-0fd1fe9469f2, crossing-1c303c088c01, crossing-27b707b08a14, crossing-3f8b9bf48884, crossing-526dbc821706, crossing-658b4261f614, crossing-7bba02156870, crossing-8431d2567c58, crossing-9090e87568d6, crossing-9eea764fde61, crossing-a59a364fd0fe, crossing-c15126eb0d40, crossing-e3df605a478e, crossing-e8041dcb3180, crossing-eefddafa9ea5, shared-corridor-cbefc58a6746.

Evaluate grade-separated crossings, shared four-track civil footprints or separate deck levels, and bounded platform/concourse/access complexes with the station authority. Freeze actual vertical profiles and gradients before selecting supports and ordinary spans. Preserve rail/PSD/egress/waterproofing/earthing interfaces. Proposed residential infill sites on this line require station/approach structures and revised service, fleet, power and full installed prices; they are not existing paid journeys.

Candidate infill IDs: infill-line-6-035500.

## Inspection, handover and programme

Use the foundation/production/lift/connection/concealed-work hold points from the master ITP. Capture installed component IDs, geometry, tests, personnel/equipment authority, NCR disposition and signed stage release. Update actual shift cycles, losses, stocks and resource reservations; do not infer an opening date from bay throughput. Station/special/track/energy/depot/fleet/testing/approval releases close the whole line. Unknown ground quantities, installed costs and dates stay unknown.

[Integrated master package](README.md) · [Interactive support/junction inspection](network-foundation-viewer.html).
