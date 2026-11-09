# Compact-drive split-lane support family

This is an unselected child-family screen of the `9f6d2230` vehicle research
candidate. It does not change the six-car passive-wheel development reference.
The physical candidates remain distinct, and neither inherited results from
the other.

## Reproduction and retained evidence

- The first attempt is retained in [run-01](run-01/). Its support pass labels
  were vacuous: the support continuous-envelope and ground-pose row counts were
  both zero. Treat those checks as **HOLD**. Its root manifest SHA256 is
  `6fd62ccfb2a85d6aa87f98a85e2bd4b94d6fffb90a1cc59824ea42a707e9bb6f`.
- The corrected evaluator is source commit
  [`1c41f0b63874f533cb7dbe29133f7672c2fbf31c`](https://github.com/modernecotech/OpenSourceRail/commit/1c41f0b63874f533cb7dbe29133f7672c2fbf31c).
  The two same-configuration trials are retained in [run-02](run-02/); the
  independent read-only integrity review is in
  [independent-review-run-02](independent-review-run-02/).
- The corrected source runs use the repository's normal Python process, with
  explicit per-trial CPU, address-space and wall-time limits. Those limits are
  resource controls, **not an OS filesystem sandbox**. No CAD, FEM, supplier
  fit or physical test was run.

The reviewer checked 2,118 hashes, seals, source links, identities, row counts
and receipts with zero integrity errors. The corrected packet root manifest
SHA256 is `0062e6ef5b59ea9a7617d18374c663f5cd34ab8438ec077b289939a36b4b4fad`;
its root manifest ID is
`cf9d26da443f3ee4ec5fc97e6bffd008e357db38287e48f866904fdaf838d981`.
The independent review packet manifest SHA256 is
`8f4f765f6c48cd01709430877eb1989d2256ecf1abb52e88f0424c2d60a2979a`.

## Result

Both split-lane variants have two distinct physical candidate IDs. Each has:

- 288 support occurrences across 12 bogies and nine part types;
- 2,040 nominal support-clearance findings, which remain unresolved;
- 312 support continuous-envelope findings, all correctly **HOLD**;
- 288 ground-pose rows across 20 sampled poses, passing only the declared
  geometric threshold;
- 3,942 total continuous/interface holds and 5,964 nominal findings;
- `known_geometry_screen_pass=false`, `selected_or_promoted=false` and
  `physical_accepted=false`.

The ground sample does not assess the continuous envelope, support loads,
fastener/joint strength, stiffness, fatigue, retention, finished geometry,
supplier dimensions or removal access. The run-02 physical candidate IDs match
run-01; their evaluation IDs change with the corrected evaluator, as expected.
Run-01 remains unmodified.

| Variant | Physical candidate | Run-02 result evaluation | Elapsed | Maximum RSS |
| --- | --- | --- | ---: | ---: |
| offset-380mm | `ca4dc10cd0379ba0698b9a791acdf76e6c04991f85b4c8b4db911e304aff3569` | `eed58b562e5d23ae251039563f48fb6df86c6be5e8839ac5d32e2097d073c1b2` | 36.98 s | 429,676 KiB |
| offset-420mm | `dbca7a47c6cf654869c3111f7ef79ca2170bd2796183557dacc4bcd87504d4b2` | `235d279ea524cbe4672a52631631ccfee0e3bd4b87a8b6a36491d5f654fb5d18` | 36.74 s | 429,744 KiB |

The per-trial limits were 60/62 CPU seconds, 1 GiB address space and 90 seconds
wall time. The source receipts and current code establish the declared request
and recorded resource results; they cannot prove historical kernel-level
enforcement or bytecode-cache custody.

## Closure effect

This corrects a missing-row-coverage defect and adds two more research geometry
children. It does not resolve the parent vehicle's complete installed mass or
measured/verified installed inertia,
motor/gearbox fit, shaft and bearing arrangement, finite joint strength,
fatigue, protection, service access or removal path. The installed-vehicle
gate therefore remains **open**; no candidate is selected or released.
