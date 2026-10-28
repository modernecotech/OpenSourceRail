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
tools/automation/osr-python tools/automation/frame-cell.py verify-publication docs/design-engine/frame-refinement/packet
```

Native source/current-input checks and replay use the tracked implementation.
Archived source files remain evidence; the verifier does not execute them.
Publication must use a fresh output folder and never rewrites an earlier packet.
