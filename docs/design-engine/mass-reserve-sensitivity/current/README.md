# Selected vehicle mass reserve sensitivity

Candidate `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3` and selection `8e5905bc7c81d6177bbaafde81ab3a5f8cc54947c4923eb4493949566ac85cdc` retain the source ledger's accounted tare of **19,221.998 kg/car**. Candidate geometry represents **9,131.799 kg/car**. The existing positive accounting residual is **10,090.200 kg/car** across 10 accounts.

Each low/base/high case replaces that existing residual reserve with a declared 0.8×/1.0×/1.2× sensitivity. The reserve is not added again on top of the accounted tare.

| Case | Reserve sensitivity (kg/car) | Scenario tare (kg/car) | Six-car scenario tare (kg) | Change from existing tare (kg/car) |
|---|---:|---:|---:|---:|
| low (0.8×) | 8,072.160 | 17,203.958 | 103,223.749 | -2,018.040 |
| base (1.0×) | 10,090.200 | 19,221.998 | 115,331.989 | +0.000 |
| high (1.2×) | 12,108.240 | 21,240.038 | 127,440.228 | +2,018.040 |

## Account-level reserves

| Account | Existing residual (kg/car) | Low (kg/car) | Base (kg/car) | High (kg/car) |
|---|---:|---:|---:|---:|
| attachments | 180.000 | 144.000 | 180.000 | 216.000 |
| passive-bogie-pair | 1,764.182 | 1,411.345 | 1,764.182 | 2,117.018 |
| retained-comfort/HVAC | 960.000 | 768.000 | 960.000 | 1,152.000 |
| retained-comfort/body | 4,873.077 | 3,898.461 | 4,873.077 | 5,847.692 |
| retained-comfort/doors | 98.767 | 79.013 | 98.767 | 118.520 |
| retained-comfort/frame-joints | 202.739 | 162.191 | 202.739 | 243.287 |
| retained-comfort/glazing | 20.482 | 16.385 | 20.482 | 24.578 |
| retained-comfort/seating | 598.144 | 478.515 | 598.144 | 717.773 |
| roof-thermal | 47.809 | 38.247 | 47.809 | 57.371 |
| services | 1,345.000 | 1,076.000 | 1,345.000 | 1,614.000 |

## Scope and evidence

This is a provisional sensitivity of the existing selected-candidate mass account. The low/base/high factors are declared scenarios, not probability bounds. Positive residuals are replaced within each scenario; they are not added twice. Equipment, joint, fastener, cooling, wiring, and installation identities/locations remain open where the source worksheet has no physical component evidence.

The two accounts with no accounting residual reconcile to represented geometry mass; this still does not prove installation or exclude additional physical joints, fasteners, and interfaces. No reserve has been declared for those unknowns, so installed mass is not complete.

The 0.8×/1.0×/1.2× factors are sensitivity assumptions only. They are not statistical confidence limits or supplier-confirmed ranges. Replace them with component-specific calculated mass or measured procurement/installation evidence when available.

The selected reference, CAD, and release states are unchanged. Centre of gravity, inertia, axle reactions, and complete installed mass remain unknown.

Reproduce with `python3 -m engineering.mass_reserve_sensitivity build` and `python3 -m engineering.mass_reserve_sensitivity verify`.

[Exact result](result.json) · [Manifest](manifest.json)
