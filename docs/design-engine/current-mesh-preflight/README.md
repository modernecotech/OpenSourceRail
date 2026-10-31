# Current mesh resource preflight

This exact preflight is bound to body `8db92b830fda54c81ec231c541f811b24f938f2471b559448d2ed2683754f78b`, definition `8eed09c97b93d3aa1988d8bdc99f11a45d6f64ca470eea10b28ecf664a34a842`, P1 bundle `1e8d1d7c394fc0bdbd47e34fb21d413ebc34a49576bad60b31b254bd635dfb68`, normal load (10818.661 kg sprung-mass hypothesis), and `C3D8I`.

It counts nested axis-plane refinements of the same disjoint-box stock. The operation does not generate a native deck or call CalculiX. It reports no memory or runtime estimate.

| Profile | x / y / z step (m) | Solid cells | Coordinate planes x / y / z | Nested from reference | Over reference | Prior 140,000-cell budget |
|---|---:|---:|---:|---|---:|---|
| reference-0.10625-isotropic | 0.106250 / 0.106250 / 0.106250 | 128,382 | 267 / 64 / 60 | yes | 0.0% | within |
| z-refined-only | 0.106250 / 0.106250 / 0.053125 | 152,344 | 267 / 64 / 90 | yes | 18.7% | exceeds |
| y-refined-only | 0.106250 / 0.053125 / 0.106250 | 168,612 | 267 / 89 / 60 | yes | 31.3% | exceeds |
| x-refined-only | 0.053125 / 0.106250 / 0.106250 | 190,742 | 427 / 64 / 60 | yes | 48.6% | exceeds |
| xy-refined | 0.053125 / 0.053125 / 0.106250 | 249,084 | 427 / 89 / 60 | yes | 94.0% | exceeds |
| xz-refined | 0.053125 / 0.106250 / 0.053125 | 223,728 | 427 / 64 / 90 | yes | 74.3% | exceeds |
| yz-refined | 0.106250 / 0.053125 / 0.053125 | 199,168 | 267 / 89 / 90 | yes | 55.1% | exceeds |
| uniform-0.053125 | 0.053125 / 0.053125 / 0.053125 | 290,660 | 427 / 89 / 90 | yes | 126.4% | exceeds |

The least-cell nested refinement is **z-refined-only** at 152,344 cells, 18.7% over the reference mesh. It still exceeds the prior 140,000-cell allowance. This is a mesh-count comparison, not a solver resource prediction or selection.

## Resource hold

Cell and coordinate-plane counts are exact for the retained disjoint-box conformal construction. They do not estimate factorization memory or runtime. No native deck or solver invocation was made. The uniform 0.053125 m case remains held on this host; any finer run needs an explicitly reviewed worker/process-tree resource boundary and observed peak memory.

The earlier 0.10625 m solve completed 128,382 cells with a requested 8 GiB solver-child address-space cap and 240 s timeout. A separate 5 GiB attempt failed during factorization. The saved tool receipt records the requested RLIMIT_AS, not observed peak RSS. The next full solve therefore needs a suitably provisioned worker, a process-tree memory boundary, and peak-RSS collection before resource settings are selected.

All engineering, numerical, and physical qualification obligations remain unchanged. No result from these counts establishes structural adequacy.

[Exact profile result](result.json) · [Manifest](manifest.json)
