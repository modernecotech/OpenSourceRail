# Finite 3D magnetic confirmation

This bounded study checks a numerical continuation method for the retained `N35-H8-half-no-yoke` coupon: named Arnold N35UH stock, finite 1 m length, 12 mm reference gap, 80°C and zero current. It does not change the physical geometry, select a replacement train or establish a usable force map.

The new explicit GetDP formulation ramps the permanent-magnet source through ten warm-started stages, from λ = 0.1 to λ = 1. Every stage must converge before sampled force credit is possible. Below 1e-6 A/m, the retained steel regularisation has constant permeability; the new Newton tangent correctly uses that permeability times the identity. Independent central differences check this derivative. The digitised 50 Hz steel proxy is still not a validated DC or temperature-dependent material law.

The original [finite-coupon driver](../trip_dynamics/fixtures/magnetics/finite_coupon.py) and historical failed attempts remain unchanged. Its geometry, mesh and Maxwell-integration helpers are reused explicitly. The complete magnetic stock/material bundle is rebuilt and compared with the retained input; claimed candidate IDs alone are insufficient.

## Run, verify and publish

Use the existing engineering environment with NumPy, Gmsh and the private GetDP 3.5.0 executable. Each case has a 300-second process-group deadline. The three cases run sequentially: coarse, finer local mesh, then expanded air domain. Mesh reuse checks the exact source, settings and original file hashes and grants no previous solve credit.

From the repository root, choose fresh output directories:

```bash
.venv/bin/python -m engineering.magnetic_confirmation run \
  --root . --output build/magnetic-confirmation/example-run \
  --getdp build/trip-dynamics/tools/getdp-3.5.0-Linux64/bin/getdp \
  --reuse-mesh-root build/trip-dynamics/finite-coupon3d-v2 \
  --cases coarse fine expanded

.venv/bin/python -m engineering.magnetic_confirmation verify \
  --root . --output build/magnetic-confirmation/example-run

.venv/bin/python -m engineering.magnetic_confirmation publish \
  --root . --run-dir build/magnetic-confirmation/example-run \
  --output build/magnetic-confirmation/example-publication

.venv/bin/python -m pytest -q engineering/magnetic_confirmation/tests
```

The optional mesh-reuse argument can be omitted. Verification checks current implementation/data and tool hashes, then recomputes stage admission, mesh/material bounds, closed air-contour results, complete PM/steel element-centroid coverage and comparisons from retained artifacts. It does not rerun a field solve. Publishing writes a fresh packet with a source/payload manifest and exact input, mesh and log archive. Failed, nonconverged and interrupted cases retain their disposition and receive no force credit.

The importable API is:

```python
run(output, root, getdp, reuse_mesh_root=None,
    cases=('coarse', 'fine', 'expanded'))
verify(output, *, root=None)
publish(output, *, run_dir, root=None)
```

## Interpretation

Two nested air contours retain forces and moments about the source origin. Mesh/domain comparisons and symmetry residuals are diagnostics, with no automatic acceptance threshold. Changing the air domain also changes the realised mesh. The element-centroid demagnetisation proxy is not a measured knee, irreversible-demagnetisation calculation or converged local peak.

Finite guideway ends, real magnet joints, steel properties, nonzero-current control, guidance/roll domains, moving losses and repeated thermal duty remain unresolved. Numerical convergence does not establish hover, installed support capacity, a full magnetic map or physical acceptance.

[Vehicle/material comparison](../../docs/design-engine/vehicle-optimisation/README.md) · [Published confirmation](../../docs/design-engine/magnetic-confirmation/README.md) · [Project introduction](../../README.md)
