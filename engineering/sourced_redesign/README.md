# Physical revisions diagnosed from actual evaluations

[Project introduction](../../README.md) · [Current engineering](../../docs/design-engine/current/README.md)

These revisions preserve the five reference-cell research families and the
selected wheel/LIM baseline. They change physical geometry and component
identities where an actual definition or numerical evaluation exposes a problem.

`family_interfaces.py` moves roof transverse ribs for the two thicker cassette
families, retaining their complete sections and counting the resulting bond/cap
stack through the existing layered generator. Interference does not become a
negative or zero-mass support. All positions, mass properties, CAD and subsequent
analyses follow the revised occurrence registry.

`bolster.py` is a separate next-experiment V4 candidate. It replaces local pad
doublers and obsolete splices with full-depth transverse bolsters, two-sided
rail-web spreaders, diaphragms, M8 retention and explicit bounded weld deposition.
It counts the actual mass, net cope geometry, assembly and removal envelopes.
Its small static suspension clearance does not establish dynamic clearance or
approved installation access. It does not silently replace any campaign vehicle.

The recorded whole-body experiment uses the same finite-contact evaluator and
load cases as its ancestor. Source/payload checks, algebraic residuals, mesh
change, model domain, material/joint allowables and physical acceptance remain
separate. See the [executed research publication](../../docs/design-engine/sourced-case/README.md).
