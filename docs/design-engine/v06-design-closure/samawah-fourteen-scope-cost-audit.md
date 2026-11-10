# Samawah candidate cost scope audit

**Review date:** 10 November 2026  
**Current physical candidate:** `9f37c5d864a34b56009030b07659abe0cc92d5dc97c5c1872384cc7b93a6b176`  
**Current body:** `75075df9247dfff7082a78eadc273d3a99f37e5486450621536c43b1bfa2f797` / evaluation `c6c5efe577bd302c507756af53238a8f162c6e2cbeaefd2aa11fecd343b93fb3`  
**Current city evaluation:** `eaa84ee07efbff5763ec11e490142f88d2701c1196d09c63b7bfc9b18ce61a16`

This audit joins the current-source Samawah city quantities to the partial rate bridge. The historical fourteen-scope cost packet is useful as a rate-method reference, but it belongs to different city service quantities, a different body and a different support design. Its project totals and NPV are not transferred.

## What has a current-candidate estimate

The corrected source-bound bridge is [`samawah-candidate-cost-bridge-current-source-attempt-03`](samawah-candidate-cost-bridge-current-source-attempt-03/README.md). It prices the current body’s counted parts/processes and five dimensionally matched guideway fragments, then reports two separate annual operating sensitivities.

| Measure | Low | Base | High | Scope |
| --- | ---: | ---: | ---: | --- |
| Counted body BOM/process, active trains plus spare trains | $29.152m | $88.679m | $297.136m | Incomplete train factory cost |
| Five matched guideway rate fragments | $41.223m | $84.859m | $306.680m | Rails, fastening sets, repeat beams, bearing pads and joint/drain/lifting allowance |
| **Partial capital fragments** | **$70.376m** | **$173.538m** | **$603.816m** | Excludes many project accounts; not installed CAPEX |
| Vehicle auxiliary electricity | $3.347m/y | $12.022m/y | $51.370m/y | Conditional auxiliary demand only; transferred tariff sensitivity |
| Corrective/disruption reserve | $0.151m/y | $1.133m/y | $8.368m/y | Transferred rate per train-km; not measured reliability |

The annual values are not added to capital, and they are not a whole-life NPV. Tariffs and reserve rates are Class-C transferred assumptions with `local_rates_verified=false`. The energy estimate excludes traction, station, depot and drive-cooling demand; physical grid demand is unverified. The reliability reserve does not imply measured availability. No additional China volume discount is supported for the five matched infrastructure lines, whose retained China-bulk and project make/buy rates are identical.

## Fourteen-scope coverage

Current route quantities are 57.873 km on five lines. The 26 map markers and 52 boarding faces are planning records, not a validated count of operational stations or powered zones. Fleet requests are 42/59/88 total trains (low/base/high), comprising 34/49/75 active and 8/10/13 spare trains. These remain conditional outline quantities.

| Cost scope | Current quantity or evidence | Priced now | Remaining to make a complete scope |
| --- | --- | --- | --- |
| Rolling stock | 34/49/75 active trains; counted body BOM/process subtotal | $23.599m / $73.648m / $253.241m active-fleet fragment | Purchased equipment, complete installed mass, assembly, test, delivery and unresolved body components |
| Guideway | 231,493 running-rail m; 385,825 fastening sets; 5,794 reference 20 m beams; new load check required | Five rate fragments; see totals above | Candidate-matched beam section/reinforcement, detailed load and support design, foundations, transitions, construction and installation |
| Stations and power | 26 markers, 52 boarding faces, one shared protection-system allowance; installed charger/grid capacity unknown | None | Operational station layouts, platform areas, powered zones, equipment ratings, protection, installation and station power |
| Factory and tooling | One shared campaign; two production shifts assumed; capacity unknown | Body direct process subtotal only | Product-specific plant, moulds, fixtures, setup, capacity and allocation without double counting |
| Construction | 5,794 beam erection units and 2,902 shared-bent requests | None beyond the guideway rate fragments | Route civil-class lengths, foundations, station spreads, temporary works, crane/haul access, erection sequence and local rates |
| Land, utilities and depot | One shared depot provision; land area and utility quantities unknown | None | Corridor right-of-way, parcels, utility diversions/connections, depot layout and sites |
| Fleet | 8/10/13 spare trains | Counted spare-train BOM/process fragment: $5.553m / $15.030m / $43.895m | Active/reserve policy, commissioning, depot capacity and complete spares package |
| Energy | 50.541m / 72.616m / 110.812m conditional vehicle-auxiliary grid kWh/y; traction, station and cooling kWh unknown | Auxiliary-only annual tariff sensitivity above | Force-driven traction energy, station/depot/cooling demand, charging capacity/losses and tariff validation |
| Operations | 9.125m / 13.688m / 21.059m annual train-km; staff roster null | None | Timetable, staff roles/hours/shifts, wage validation, supervision and operating arrangements |
| Maintenance | 42/59/88 total trainsets | None | Component maintenance plans, access, labour, spares, service intervals and field evidence |
| Renewals | 30-year accounting horizon | None | Candidate asset lives, replacement quantities, renewal labour/tooling and residual values |
| Recovery | Five lines require protected recovery | None | Rescue equipment, interfaces, route coverage, response plan and recovery staffing |
| Reliability | 0.99 planning hypothesis; measured availability null | Annual corrective/disruption reserve sensitivity above | Failure/delay observations, availability model, redundancy and service-recovery evidence |
| Disposal | 30-year horizon; complete installed material inventory absent | None | Removal process, material recovery, hazardous-material treatment, disposal rates and residual value basis |

## Provenance correction

The earlier [`samawah-candidate-cost-bridge-current-source`](samawah-candidate-cost-bridge-current-source/README.md) packet is retained, but its source map points at a historical body file even though the calculation reads the current replay body. Its arithmetic reproduced, but its BOM provenance was incomplete. Do not use it as the current source-bound cost result.

Attempt 02 corrected the body hash but retained an incorrect reproduction path in its generated README. Attempt 03 is the current packet: it binds the actual `compact-737-h100/body.json.gz` source (SHA-256 `f38cc7fc64836d913d2909bb27075ae7926846baf4908aab51007c508df53af7`) and includes the auxiliary-energy and corrective/disruption sensitivities. Earlier packets remain unchanged for auditability.

The current installed CAPEX and whole-life NPV remain **unknown**, not zero. This audit does not select propulsion, validate city demand or sites, approve engineering, or close the release gate.
