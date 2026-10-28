# Source-defined side-sill candidate — executed reference cell

This is a numerical research revision of the V4 bolster body. It is **not a
selected or qualified railway**. The selected six-car wheel/LIM reference and the
[five-family campaign](../sourced-case/README.md) retain their original identities.

| Definition | Identity |
|---|---|
| Physical body | `6fd30b694342266d60698018f14c492b90c25ac048c3ebfd7157a7031d3cef62` |
| Native package | `d2ec6dcdbf46d0e2c256415528f83fdffee4cfe88abd39913278a35f10244f9a` |
| Integrated 2 km cell | `1b3ae3f4de24f7302827e61047aa4ddb1f087c46ec84f47ec6bb2607b5a1e084` |
| [Full cell publication](packet/manifest.json) | `61637c84c46f015921722138b5857d88d81af3d18c9872587c70e43845232e38` |

Two counted closed side-sills and their actual supports/joins add **480.04 kg/car**
to the upper mass bound. The resulting accounted upper bound is **14,445.52
kg/car**, including the existing equipped-vehicle accounts; it is not certified
weighed tare or a claim that installed supplier details are complete.

## Whole-body calculation

All **18 case/mesh responses pass algebraic checks and remain inside the
unchanged declared linear-kinematic domain**. The worker completed in 132 seconds,
with 3 GiB address-space and 240-second CPU/wall limits. It was an ordinary
subprocess, without a filesystem or network sandbox.

| Fine-mesh response | Bolster ancestor | Side-sill revision |
|---|---:|---:|
| Normal maximum translation | 177.53 mm | 40.37 mm |
| Crowd maximum translation | 322.15 mm | 73.14 mm |
| Normal maximum rotation | 44.92 mrad | 14.66 mrad |
| Crowd maximum rotation | 81.88 mrad | 24.57 mrad |

Displacement mesh-change indicators are 1.41% normal and 0.66% crowd. Energy
changes remain approximately 7.2% and 5.3% relative to the coarse mesh. Local
stress/contact convergence therefore remains in the refinement frontier.
Reported member-stress and contact-traction proxies are not approved ply,
von-Mises, weld/HAZ, fatigue or buckling margins.

An independent saved-state software check rebuilt actions and energy without
factorization or a fresh solve. It confirmed exact native definition/ancestry,
17,844 unchanged non-body occurrences, model geometry and load conservation.
Maximum independently accumulated free residual was 6.87×10⁻¹⁰. This checks the
implemented model, not independent physical correlation or professional acceptance.

The [sealed audit](independent-audit.json), produced by the
[read-only audit tool](../../../tools/automation/audit-frame-states.py), retains
all 18 checks, source/tool identities and before/after input hashes. Its own
resource limits were inherited and unlimited; the numerical worker's 3 GiB/
240-second limits are recorded separately. The audit has no enforced filesystem
read-only sandbox and is not a human engineering review.

## Propagation through the same candidate

The [sealed packet](packet/manifest.json) contains the actual parent and revised
native inputs, source snapshot and results; a new equipment/power wrapper with
old evidence retained as ancestry; fresh nine-context force-driven journeys;
braking and civil load transfer; manufacturing and disabled business drafts;
scoped price records; and an actually exported/reopened **40,488-occurrence IFC**.
Its publication repeats the journeys and IFC verification using current tracked
code. Historical installation/clearance/thermal outcomes are invalidated.

Six scenarios arrive conditionally. The uphill stall, power-interruption stall and
intentional emergency stop remain separate outcomes. A nominal arrival driven by
catalogue caps and contact assumptions is not an admitted operating force map.
The charging proposal has its own physical identity; it is not silently included
in the body or complete installed economics. No integrated cost winner is selected.

## Work required before acceptance

The stock fits its declared 2.8 m nominal body envelope, with 14 mm nominal joining
margin and 10 mm static brake-envelope gap. Dynamic movement, tolerances,
maintenance sweeps and functional door/glazing limits remain unverified.
Local cassette/bracket traction proxies reach 175.9 MPa under crowd loading;
approved joint margins remain unknown. Actual joint load paths, manufactured
weld/HAZ properties, buckling, fatigue, fire and load-test correlation are required.

Motor/inverter/contact performance, repeated cooling duty, actual brake curves,
hot-site charging/interlocks, surveyed civil/site conditions, complete quotations,
HIL and independent prototype/pilot approval remain open. The [closure matrix](../sourced-case/closure-summary.json)
provides the test-input categories. Public component specifications do not supply
measurements of this assembled railway.

Exact x86-64 replay uses NumPy 2.3.5, one thread, the non-FMA OpenBLAS NEHALEM
kernel and disabled AVX-512 dispatch. An unpinned [CI run](https://github.com/modernecotech/OpenSourceRail/actions/runs/40776068695)
changed four diagnostic clearance values by one floating-point bit and therefore
changed the evaluation hash. The [actual diagnostic](cpu-dispatch-diagnostic.json)
and [origin receipt](cpu-dispatch-origin.json) retain that failure. Physical
registry, geometry, mass, source identities and the remaining payload matched.
The runtime profile uses the documented [OpenBLAS controls](https://www.openmathlib.org/OpenBLAS/docs/runtime_variables/)
and [NumPy controls](https://numpy.org/doc/2.3/reference/simd/build-options.html#runtime-dispatch).
The production verifier continues to require exact bytes; no diagnostic fields or
engineering criteria are omitted from its comparison.

```sh
export OPENBLAS_CORETYPE=NEHALEM OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
export NPY_DISABLE_CPU_FEATURES=AVX512F,AVX512CD,AVX512_KNL,AVX512_KNM,AVX512_SKX,AVX512_CLX,AVX512_CNL,AVX512_ICL,AVX512_SPR
tools/automation/osr-python tools/automation/frame-cell.py verify-publication docs/design-engine/frame-refinement/packet
```

[Source and reproduction](../../../engineering/frame_refinement/README.md) ·
[project introduction](../../../README.md)
