# v0.6 vehicle mass reconciliation

Physical candidate `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`; body `9489e4f2666fd3b3c73232c86df3f12adf42a5531eb27373834cf3fecb1a3117`; selection `8e5905bc7c81d6177bbaafde81ab3a5f8cc54947c4923eb4493949566ac85cdc`.

This report preserves every retained source-account occurrence in its system account, then assigns each candidate geometry occurrence to one parent account using explicit component-family rules. Inherited source occurrences and current geometry do not have a row-to-row identity join, so the report does not claim one. Newly modelled underframe, bogie, and passive-secondary geometry is assigned once. This is an accounting reconciliation, not a complete installed-mass claim.

| Ledger result | Value |
|---|---:|
| Accounted tare | 19,221.998 kg/car |
| Candidate located geometry | 9,131.799 kg/car |
| Reference or unlocated account residual | 10,090.200 kg/car |
| Account rows | 12 |
| Located geometry occurrences assigned once | 2,482 |
| Complete installed mass, CG, inertia, axle reactions | Unknown |

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

Source occurrences keep their source IDs and occurrence-definition IDs in [mass-ledger.json.gz](mass-ledger.json.gz). The report is bound by [manifest.json](manifest.json). Regenerate with `python3 -m engineering.mass_ledger_audit build` and verify with `python3 -m engineering.mass_ledger_audit verify`.

No physical acceptance, manufacturing release, or operating release is asserted.
