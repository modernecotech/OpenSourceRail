# Counted side-sill revision and coupled reference cell

[Project introduction](../../README.md) · [Current engineering](../../docs/design-engine/current/README.md)

`model.revision(parent)` accepts the exact V4 bolster experiment and creates a
separately identified physical candidate. Two fabricated closed side-sills,
net-trimmed transverse/bolster stock, finite bearing spreaders, M8 ties and bounded
joining accounts add approximately 480 kg/car to its counted upper mass bound.
The source preserves purchased components, poses and fixed requirements; it
records ancestry, manufacturing and access assumptions and recalculates mass,
centre-of-gravity and inertia accounts. Installed measured quantities stay unknown.

The necessary section bound is checked before the full worker. Static COTS and
retained-stock/gauge checks precede the finite-contact solve. They do not establish
dynamic gauge, brake motion or approved maintenance access. Weld/HAZ, fatigue,
buckling, material allowables and physical qualification remain open.

The [executed dossier](../../docs/design-engine/frame-refinement/README.md) includes
the actual native worker and the same candidate propagated through source-limited
propulsion, nine 2 km journey contexts, braking, civil loads, manufacturing drafts,
price coverage and a reopened full-train IFC.

```sh
python -m pip install -r engineering/sourced_case/requirements.txt
export OPENBLAS_CORETYPE=NEHALEM OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
export NPY_DISABLE_CPU_FEATURES=AVX512F,AVX512CD,AVX512_KNL,AVX512_KNM,AVX512_SKX,AVX512_CLX,AVX512_CNL,AVX512_ICL,AVX512_SPR
git fetch --no-tags --depth=1 origin b37988a750690d85939e5cbe7b2223b96c02980e
tools/automation/osr-python tools/automation/replay-retained-frame.py docs/design-engine/frame-refinement/packet --git-root . --output build/retained-frame-replay
```

This x86-64 runtime profile preserves exact diagnostic arithmetic across runners;
see the dossier's retained CPU-dispatch failure. All source and payload checks
remain exact, and the frozen model/native packet is unchanged.

Current revision tests generate fresh parents and retain the strict source checks.
The recorded experiment replays its authenticated producer epoch in a separate
import root. Missing imports are recovered from the same pinned Git tree and
indexed separately. Python import/process guards and an address-space limit apply;
there is no OS filesystem or network sandbox. Native experiments are not rerun,
and retained replay grants no current evaluator admission or physical acceptance.
Each attempt uses a fresh output folder and preserves the original packet.
