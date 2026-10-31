# Executed continuing-cell results — 28 October 2026

These are numerical research records. No authenticated prototype measurements, accepted operating maps, qualified structural margins, installed whole-life price or operating approval have been established.

## Reproduction and integrity

Final regression coverage: **210 tests passed**, including the existing cost-contract checks and new inactive-export checks:

```bash
.venv/bin/python -m pytest -q --import-mode=importlib engineering/railway_progress/tests
./osr design progress verify-publication
./osr design progress verify-methods
```

Source development used an isolated Git worktree. Numerical jobs used private persistent directories, immutable source/input snapshots, explicit budgets and retained logs. Three moving-field workers were limited to 1,200 seconds and 3 GiB each; two structural workers to 240 seconds and 3 GiB each. These are actual worker resource controls, not a claim that a human or agent verifier was operating-system isolated.

| Package | Identity |
|---|---|
| Ten-cell run | `6490e412fd4c678bf2813b71942aee24c019052988f716ab239fe1e6b6212e30` |
| Cell publication | `8f4d97ba36799922760c8efd5e218f0c5dfc7af455f3652b3ed995dfcdd8de82` |
| Five native packages | `7306491795f7aa6ca893e3528ccbddf2700370a2cb39b0f36ae431e5ac42dfc3` |
| Matched motor comparison | `1c0a219e3a012b2fdf7169f160399fa57deeb0a638df9370c2037a32854b55c8` |

The publication carries source snapshots and exact owned payload inventories. Cell verification reconstructs vehicle, launch, civil, manufacturing and trajectory results. Native verification checks recorded tool/source/payload identities and saved-state arithmetic; it does not claim a new independent field solve or physical correlation. Current-tool reuse and recorded-execution integrity remain separate.

## Conditional journeys and physical redesign

Ten physical cells combine V1–V5 with 1.5/2 km spacing. All **130 main contexts executed**, with **90 conditional numerical arrivals and 80 service-screen results**, zero admitted operating maps and zero qualified journeys. A further thirteen cable-launch contexts are retained for comparison.

The V1/2 km normal upper-mass roller case stops at **2,000.02314 m in 152.34026 s**. Peak conditional traction is **45.230 kN**, peak shaft power **902.553 kW**, and the discrete work–kinetic residual is **2.85e−7 J**. These depend on industrial shaft ratings, explicit unverified clamp/contact/control assumptions, bounded proposed vehicle masses and an unqualified brake law. They are not measured railway performance.

Every cell retains adverse results: a 2% uphill coast stalls before the destination, power loss strands the train, low adhesion overruns the target, and downhill running exceeds the speed cap even though the corrected terminal controller stops and holds under its unqualified pressure/adhesion hypotheses. Emergency braking stops short of the destination as expected, without an accepted stopping envelope or protected headway. Failure records are neither dropped nor converted to arrivals. Downhill speed regulation and its thermal duty remain controller/model tasks; terminal stopping alone is not an accepted operating policy.

The roller sweep evaluates twelve layouts: the retained baseline plus eleven physical count/location revisions. Ten fail the sampled lower-cap force screen. The five-bank/four-pair baseline and seven-bank/four-pair alternative survive that necessary screen; the smaller experiment frontier retains the baseline. It installs forty catalogue motors, **80.4 tonnes of published motor mass alone**, before other plant. No simplicity, installed-cost or economic victory is demonstrated. All unsupported prices and missing plant masses stay open.

Cable launch reduces that particular catalogue motor count but its declared launch/attach/reset lower cycle is **140.71 s**, longer than the 120 s service target. Grip, detachment, return route, thermal duty and passenger protection remain unverified. The model is retained as a separate architecture, not silently substituted into v0.6.

The same trajectories transfer loads through 24 actual axle offsets. V1/2 km maximum sampled vertical balance residual is **5.82e−10 N**. The two stations use forty 5.5 m platform cassettes and forty-four station supports. Declared platform dead loads balance exactly; guideway/plant assignment residuals are below **1.1e−8 N** for that cell. These balance checks do not establish stiffness, capacity, ground suitability, continuous dynamic envelopes or construction acceptance.

## Moving-LIM experiments

The three runs share the historical rewound continuous-secondary component and 0.128 s horizon at 20 m/s, 375 V phase peak and 50 Hz. Their physical identity is `84c728673f67587bd7cfca462fdf95397360f10c1416e5a55b91f7f812d496f8`. **They do not validate the newer segmented-secondary vehicles.**

| Run | Time step / mesh input | Mean thrust, last two cycles | Numerical field-energy defect / terminal energy |
|---|---|---:|---:|
| BDF2 coarse | 0.001 s / 0.08 m | 2,631.28 N | 4.057% |
| BDF2 time refinement | 0.0005 s / 0.08 m | 3,064.57 N | 0.657% |
| BDF2 spatial refinement | 0.001 s / 0.04 m | 2,375.77 N | 4.282% |

Matched full-trace thrust RMS changes are **12.66% temporally** and **10.32% spatially**. Numerical damping is substantially lower than the retained backward-Euler studies, but convergence is unconfirmed. Actual per-path RMS currents were calculated from the waveforms rather than inferred from a sine-wave peak. Repeated thermal duty, end/entry/sectional overlap, the full speed/current/frequency/temperature domain, independent field correlation and physical tests remain open.

## Located-stock structural experiments

V1 and V4 each executed ten load cases on 1.2/0.6 m mesh inputs. Their original producer, inputs, worker outputs and logs remain unchanged. A separate pinned review corrects only the verifier's equal JSON-float/NumPy-scalar representation comparison and recomputes geometry, mass loads and matrix responses at the original tolerances, without another factorization or solve. The report persists immutable saved residual values only after checking recomputed values at those same tolerances, so BLAS reduction roundoff cannot change the review identity. Full V1 and V4 review JSON was byte-identical at one and two BLAS threads.

| Vehicle | Native run evaluation | Separate saved-state review |
|---|---|---|
| V1 | `39361110279c0c2cc0c84c13d9b2541d6672debaaa2d190dadaea0c5807f8936` | `06016adf69f13a3a52eab472efb7ce9018ebfa526e53181a5fbb5918d999ba5b` |
| V4 | `772d16967cc7edf16a17f3b83817da101cf3be2ca230d487616eba9643cab435` | `c6ae2b702bbb343ebb61ed486238bbd3f859bf07478aba9466fffe97ad582b2b` |

Free-equilibrium residuals are below 6e−9, but **all ten cases in both vehicles trigger the model's small-displacement warning**, and refinement is unresolved. The frame/grillage, provisional finite joints and generic material hypotheses cannot qualify or reject a real bonded shell. Better shell/joint/laminate models, converged interface responses, actual material allowables and physical correlation are required before selecting a body. Mathematical cantilever/torsion/Navier-plate controls are method evidence only.

## Platform and acceptance boundary

The real Chromium check loaded all ten candidates and five views, opened the part/occurrence ledger, switched scenarios without stale charts, reported zero page errors and rejected POST with HTTP 405. The engineering API is local and read-only. Manufacturing outputs retain dimensioned net/gross blanks, yield, operation/tooling hypotheses and unknown purchased-module internals. Prices are Class C assumptions; complete installed/whole-life cost remains unknown. The V1/2 km export includes 169 disabled part Items, three inactive BOMs, 169 Routings and unsent RFQ drafts. Its vehicle and added onboard launch occurrences reconcile exactly. No production order, RFQ, equipment activation or live train transaction was submitted.

The remaining programme includes numerical structural/model refinement, usable segmented moving-drive/contact maps, actual installed details and prices, site design, repeated duty, authenticated physical tests, sensing/HIL, independent safety assessment, manufacturing release, commissioning and an operating pilot. The original phase 8/9 objectives cannot be completed by software generation alone.

Published records: [cell manifest](manifest.json), [summary](summary.json), [native methods](native-methods.json), [cell source/payload archive](continuing-cell.tar.gz), [native source/payload archive](native-methods.tar.gz).
