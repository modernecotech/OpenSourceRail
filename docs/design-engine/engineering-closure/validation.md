# Current engineering closure — executed validation, 28 October 2026

The current software/evidence adapters and numerical packages execute. The physical railway remains incomplete: no complete installed vehicle, qualified available-force map, supported end-to-end journey, priced whole-life winner, manufacturing release or operating release is demonstrated.

## Retained identities and replay

- Current GFRP 2 km research candidate: `fb244a9e494d8a897a1763859a6caa711c02be0394a8cec64abd0d9fa078f5a4`.
- Current assessment: `4ab8d5d9e163e0fde778d131f65a1033adadbf875dc1a476f4b2e0cfe925dd81`; [immutable package](4ab8d5d9e163e0fde778d131f65a1033adadbf875dc1a476f4b2e0cfe925dd81.tar.gz), [manifest](manifest.json).
- Motor experiment: `2aa264997ada48d9be52d14e69dc95fa8223a172edac7ba9c856366d9d2c27fa`; [actual inputs, logs, meshes, results and partial traces](motor-experiments.tar.gz), [manifest](motor-manifest.json).
- Three full candidate propagations: [manifest](variant-design-manifest.json), [reference](reference.json.gz), [wider return](wide-return.json.gz), [rewound](rewound.json.gz).
- Sources, payload inventories and semantic replay verify. Motor archive checks use the recorded execution tool identity; they do not assert local native rerun. Exact native reuse requires the current Python binary, NumPy/SciPy/SuperLU and source/request/mesh/resource identities.

The current report has **0 authenticated records, 0 admitted operating maps, 0 numerical arrivals and 19 open tasks**: five engineering domains, four load-context journeys and ten physical protocols. Its four retained native component controls do not satisfy those missing records. Strict completion remains held (CLI exit 3). All physical, manufacturing and operating acceptance flags remain false. The selected reference and six earlier research-twin packages are preserved.

## Actual motor results

Every actual worker was limited to 175 seconds, 3 GiB address space, one BLAS thread and 180,000 mesh nodes. Six field workers were dispatched; four controls completed and two rated moving runs were interrupted. Two other rated requests were held by a cheap necessary electrical bound before any field worker. Eight matrix rows are not eight successful solves.

| Experiment | Execution | Final completed-trace thrust N | Evaluation |
|---|---|---:|---|
| zero | completed | -0 | `ba807565ededafff8b11a3bd65f5356f29f2fe26216c5d6d128bdc537e52fee9` |
| inside-forward | completed | 0.1089674826 | `32c790ffa66c183d980099b4ec083d723f09581b35534a11f9375bcf12cec61c` |
| inside-reverse | completed | -0.109566823 | `84fc465787c77ea9b1ccf55ac08869e7bb156c98db615b3c043330797a727e81` |
| moving-entry | completed | -1.907813446e-05 | `d21c83fe92ab912941a5feddb5c075132afc968c4501f348cbdae6e19519267f` |
| launch-reference-rated | held-necessary-bound | — | `5c3ea451a7951b3dc19a02f0d8055bdc8ee56942d3a030f945b6c5b0ebbca409` |
| launch-wide-return-rated | held-necessary-bound | — | `1499c0070d9e249b96f8a7383105a9ff3195d135e6823977d4236505152ee34d` |
| rewound-running | interrupted | — | `2f002d6f23a7c760c7f93d780baa38e623033a7379322f5fef66dea36c9c5091` |
| rewound-running-fine-time | interrupted | — | `a6980b6b5c05786dcecd74707dc694ba0c7727bb6f043f105563e5506e6d2e12` |

The low-voltage forward control was independently rerun in a separate private numerical directory and matched its complete result exactly: candidate/request/source/tool/mesh, sixteen steps and final thrust **0.1089674826 N**. Replay receipt: `52d0029107a2924f5a223461024a431a9d3d4bca3a074d826d504d7ed680ced3`. That separate execution used the same numerical method and is not independent physical correlation or spatial convergence.

The two 375 V peak, 50 Hz, 20 m/s rewound runs requested the same 0.128 s horizon, with 2 ms and 1 ms steps. They reached their runtime bounds at different times: the saved partial files contain **42 steps/0.084 s** and **46 steps/0.046 s**. Their last saved instantaneous thrusts are approximately **1,009.67 N** and **2,495.34 N**, respectively. Those values occur at different times and are not a converged comparison, average available force or an operating map. Partial current/power traces are retained; stabilization work is explicitly not physical heat. At the common saved time 0.046 s, coarse and fine instantaneous thrusts are 1,119.7863 N and 2,495.3390 N, a 55.12% difference relative to the fine value. Both force histories change sign. Small algebraic power residuals do not resolve this temporal discrepancy. Continue time/space refinement and model validation under a revised numerical resource request rather than promoting an interrupted result.

## Physical rewrites and whole-system consequences

At the accounted GFRP normal-load mass **102,008.56 kg**, the launch calculation requires **1,043,465 W** at 20 m/s and 0.4 m/s², including the declared rotor/rolling/drag hypotheses. This mass is not a complete installed mass.

| Physical winding candidate | Bare primary stock, five banks kg | Optimistic sinusoidal shaft-power ceiling W | Necessary screen |
|---|---:|---:|---|
| Reference | 22,818.56 | 717,747 | Held |
| Wider return only | 41,658.56 | 717,747 | Held |
| Rewound | 52,407.55 | 1,189,160 | Passes necessary bound only |

The screen assumes one active bank, unity power factor and copper as its only counted loss. It is conditional on the declared sinusoidal voltage/current envelope; transient stored energy, other waveforms, additional losses and installed equipment need their own evidence. The rewound physical candidate retains the **4 A/mm² RMS** limit using 45 mm² conductor, deeper slots and 230 A peak. It adds **29,588.99 kg** of bare wayside stock over the reference. This is not a demonstrated saving or feasible motor.

Each of the three actual candidate propagations has five banks, 2,430 primary stock occurrences, full six-car/infrastructure scene and BOM, four motion contexts, braking identity, guideway dead-load overlay, disabled delivery/ERP drafts and unpriced economic scope. Onboard stock and mass accounting remain unchanged. New primary weight enters support reactions; piers/foundations and actual civil reinforcement are not silently treated as resized. No transactions or equipment activations are performed.

## Required physical programme

The report retains candidate-bound article, batch, procedure, calibrated-channel, uncertainty, sample/repetition, limit and independent-review requests. All ten protocols remain unexecuted. Approved limits must come from their actual interfaces and independent engineering approval; software examples are not approved test procedures.

| Protocol | Required subject | Present evidence |
|---|---|---|
| T01 | Installed article inventory, geometry, mass, CG and inertia | Open: no authenticated physical execution |
| T02 | Lot-specific structural material and conditioned coupon laws | Open: no authenticated physical execution |
| T03 | Actual joints, hardpoints and retained equipment attachments | Open: no authenticated physical execution |
| T04 | Whole-body structural and functional correlation | Open: no authenticated physical execution |
| T05 | Finite-position LIM force/electrical/circuit map | Open: no authenticated physical execution |
| T06 | Repeated motor/converter thermal and supply duty | Open: no authenticated physical execution |
| T07 | Independent braking, adhesion, static hold and rescue hardware | Open: no authenticated physical execution |
| T08 | Protected1.5/2km same-candidate journey and fault pilot | Open: no authenticated physical execution |
| T09 | Surveyed civil, track and erection qualification | Open: no authenticated physical execution |
| T10 | Priced manufacturing, installation and equal-service cost evidence | Open: no authenticated physical execution |

External authenticated equipment drawings/masses, structural and joint records, motor/brake/material tests, surveyed route/geotechnical data, supplier quotes and whole-life quantities remain necessary. Numerical and commercial records keep their provenance and cannot be relabelled as physical measurements. Trusted authentication and numerical replay callbacks come from the calling application, never imported input code or an approval string.

## Reproduction and checks

```bash
./osr-complete motor-run --state build/current-motors --max-new-runs 8
./osr-complete assess --output build/current-closure --motor-state build/current-motors
./osr-complete verify build/current-closure
./osr-complete verify build/current-closure --require-complete  # expected exit 3 without evidence
./osr-complete verify-publication
./osr-complete motor-verify-publication
./osr-complete variants-verify-publication
.venv/bin/python -m pytest -q --import-mode=importlib engineering/railway_completion/tests
```

The integration package above used the four explicit parent-candidate native package paths before the experiment index was complete; the completed `--motor-state` path selects the same four controls and excludes held non-native screens and other physical candidates. Private numerical directories stay outside the repository; only bounded source-bound packages are retained here.

The frozen current suite passed **241 tests** (208 evidence/domain/motor/motion/operating/experiment tests, 24 coordinator tests and nine variant tests). A further **58 retained moving-motor, motion, equipped-candidate and short-accelerator regressions** passed. An independent specialist reran the 24 coordinator cases and verified the retained actual closure read-only; this discipline was instructional, not an OS-enforced sandbox.
