# v0.6 vehicle mass reconciliation

Physical candidate `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`; body `9489e4f2666fd3b3c73232c86df3f12adf42a5531eb27373834cf3fecb1a3117`; selection `8e5905bc7c81d6177bbaafde81ab3a5f8cc54947c4923eb4493949566ac85cdc`.

This report preserves every retained source-account occurrence in its system account, then assigns each candidate geometry occurrence to one parent account using explicit component-family rules. For comfort-shell geometry, it records either an exact retained source-occurrence ID and mass match or an exact nested source-geometry-part ID and mass match. The two provenance link types are disjoint. They trace model origin only; they do not establish physical installation, assembly completeness, or measured mass. Newly modelled underframe, bogie, and passive-secondary geometry is assigned once. This is an accounting reconciliation, not a complete installed-mass claim.

| Ledger result | Value |
|---|---:|
| Accounted tare | 19,221.998 kg/car |
| Candidate located geometry | 9,131.799 kg/car |
| Reference or unlocated account residual | 10,090.200 kg/car |
| Account rows | 12 |
| Located geometry occurrences assigned once | 2,482 |
| Exact retained source-occurrence ID links (geometry occurrences / source occurrences) | 750 / 750 |
| Mass under those exact source-occurrence ID links | 1,324.307 kg/car |
| Exact inherited source-geometry links (geometry parts / source occurrences) | 1,516 / 28 |
| Mass under those exact source-geometry links | 1,162.040 kg/car |
| Combined exact source identity links (disjoint geometry occurrences / mass) | 2,266 / 2,486.346 kg/car |
| Candidate geometry without either exact source identity link | 216 occurrences / 6,645.452 kg/car |
| Closure worksheet rows (source / geometry / account) | 5,418 (2,924 / 2,482 / 12) |
| Separate non-additive analytical estimates | 1 (47.809 kg/car already represented in the scalar account) |
| Complete installed mass, CG, inertia, axle reactions | Unknown |

## Provisional roof-finish distribution estimate

The separate analytical estimate links the existing `white-roof-finish` account to 24 modelled roof upper-skin surfaces. Their combined plan area is 45.050 m²; the declared 0.800 mm thickness and 1326.56 kg/m³ density give 47.809 kg/car.
The estimated candidate-frame material centroid is (0.0000, 0.0000, 3.8058) m. It is derived from the roof-surface areas and the 1 m floor translation, with half the assumed coating thickness added vertically. This is not a verified installed position.
The coating mass is already included in the scalar roof-thermal account. This estimate adds 0 kg to accounted tare, adds no candidate CAD occurrence, and changes neither located geometry mass nor the account residual. Uniform coverage, material density, thickness, seams, openings, and solar-panel overlap require confirmation.

## Account groups

| Account group | Accounted kg | Geometry kg | Residual kg | Source occurrences | Geometry occurrences |
|---|---:|---:|---:|---:|---:|
| attachments | 180.000 | 0.000 | 180.000 | 1 | 0 |
| passive-bogie-pair | 6,730.000 | 4,965.818 | 1,764.182 | 0 | 60 |
| passive-secondary | 275.343 | 275.343 | 0.000 | 0 | 52 |
| retained-comfort/HVAC | 960.000 | 0.000 | 960.000 | 5 | 0 |
| retained-comfort/body | 7,196.087 | 2,323.011 | 4,873.077 | 754 | 1,482 |
| retained-comfort/doors | 127.867 | 29.100 | 98.767 | 4 | 48 |
| retained-comfort/frame-joints | 202.739 | 0.000 | 202.739 | 2,128 | 0 |
| retained-comfort/glazing | 431.625 | 411.143 | 20.482 | 5 | 36 |
| retained-comfort/seating | 800.000 | 201.856 | 598.144 | 25 | 744 |
| roof-thermal | 47.809 | 0.000 | 47.809 | 1 | 0 |
| services | 1,345.000 | 0.000 | 1,345.000 | 1 | 0 |
| wheel-underframe | 925.528 | 925.528 | 0.000 | 0 | 60 |

The located-material centre of gravity is calculated from the represented geometry subset only. It excludes all residual accounts, including the service pack, HVAC, unlocated bogie balance, roof coating takeoff, attachment allowance, and source-account mass without candidate geometry. It is not the installed vehicle CG. Average axle masses are not axle reactions; longitudinal balance and dynamic wheel loads remain unresolved.

Exact retained source-occurrence IDs link 750 candidate geometry occurrences (1,324.307 kg/car) to 750 source occurrences, with each linked mass checked equal. Separately, exact nested source-geometry IDs link 1,516 occurrences (1,162.040 kg/car); those nested links are also mass-checked and have distinct candidate geometry IDs. Together the links identify 2,266 of 2,482 candidate geometry occurrences and 2,486.346 kg/car of modeled geometry. The remaining 216 geometry occurrences (6,645.452 kg/car) have no exact source-occurrence or nested-subgeometry link. These provenance links do not establish that a part was manufactured or installed as modeled.
The [mass closure worksheet](mass-closure-worksheet.json.gz) has one row for every retained source-account occurrence, candidate geometry occurrence, and account closure. It keeps source-accounted mass, CAD-derived mass, and account residuals in separate fields. Every row's physically installed mass and installed position remain null; a candidate geometry centroid is not an installed position, and a positive accounting residual is not a physical part.

Source occurrences keep their source IDs and occurrence-definition IDs in [mass-ledger.json.gz](mass-ledger.json.gz). The report is bound by [manifest.json](manifest.json). Regenerate with `python3 -m engineering.mass_ledger_audit build` and verify with `python3 -m engineering.mass_ledger_audit verify`.

No physical acceptance, manufacturing release, or operating release is asserted.
