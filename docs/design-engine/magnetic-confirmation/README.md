# Finite 3D magnetic continuation confirmation

This separate numerical study uses the unchanged finite 1 m N35UH Halbach coupon at 80°C and zero current. It preserves the physical source and isotropic 50 Hz steel proxy while correcting the low-field Newton tangent and ramping the PM source through ten warm-started load stages. The historical failed Newton and Picard attempts remain unchanged.

**No complete force map, stable hover, integrated candidate selection or physical material acceptance is established.** Complete λ = 1 convergence is necessary for sampled force credit; mesh, domain, air-contour and local demagnetisation uncertainty remain separate.

[Retained results](study.json) · [Independent read-back checks](verification.json) · [Exact inputs, mesh and logs](artifacts.tar.gz)

| Case | Numerical disposition | Full-source converged | Fz contours 1 / 2, N | Demag proxy margin, A/m |
|---|---|---|---|---|
| coarse | completed | True | 14403.2 / 14832.4 | 418477 |
| fine | completed | True | 16253.5 / 14942.6 | 380000 |
| expanded | completed | True | 16433.6 / 14986 | 396703 |

## Numerical and physical scope

Each case has a 300-second complete worker deadline. Cases execute sequentially. The fine mesh changes the near/gap sizes at the same air boundary; the expanded case changes the air boundary with the fine local sizes. Domain refinement also changes the realised mesh and cannot isolate boundary error exactly. Two nested air contours integrate the Maxwell traction and moments about the source origin. The result JSON retains full vector/moment changes and symmetry residuals; no arbitrary acceptance threshold converts these diagnostics into a qualified map.

The low-field branch keeps exactly the original B(H) regularisation: below 1e-6 A/m its permeability is constant mu0 + 0.0025, so its derivative is that scalar times the identity. Componentwise central differences check the new tangent. This verifies differentiation, not the retained digitised 50 Hz steel curve as a measured DC/reversible law.

The PM demagnetisation screen uses element-centroid Hparallel and 80% of the temperature-adjusted minimum Hcj. It is neither a measured knee nor an irreversible-demagnetisation model; local peak convergence, steel temperature effects, finite guideway ends, real magnet joints, currents, motion/losses and repeated thermal duty remain unresolved.

Vehicle source identity: `de9e5f82391fe1c7aa6dd4a9321711f3972e580f1f9345933860e73367f27e4f`. Magnetic component identity: `ff677ea60334a09828e70df8e89f8a9a8726e38da171cfc0f73c5f60221d2c0e`. Source request: `6994c865157a0364c792ebf871fc52016c1f0e307a63270de967ce53ef904ede`.

Reproduce with `python -m engineering.magnetic_confirmation run --root <repository> --output <fresh-directory> --getdp <getdp-executable> --reuse-mesh-root <verified-original-mesh-directory>`. Verify with `python -m engineering.magnetic_confirmation verify --root <repository> --output <run-directory>`. Mesh reuse is optional and grants no previous solve credit.
