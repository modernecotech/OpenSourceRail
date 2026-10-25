# Structural exchange fixtures

These files do not qualify a car body. All physical and adoption flags remain false.

`analytical-laminate.json` records an executed classical laminate theory and
consistent-mass Euler–Bernoulli beam calculation for a synthetic [0/90/90/0]
coupon. It uses declared orthotropic constants, cylindrical bending, a clamped
root and a 0.1 N tip force. The independently calculated cantilever deflection
and first frequency check the beam assembly. It omits transverse shear,
laminate/joint failure, body torsion, support prestress and equipped inertia.

The Code_Aster shell template has **not executed**. No `code_aster`, `as_run`
or `run_aster` executable was found. The available Docker client could not
list images because its API socket denied access. No image was pulled and
no environment was installed. `tool-availability.json` records that bounded
probe; it does not assert that no installation exists anywhere on the host.

When a working Code_Aster environment is available, copy `laminate.comm`,
`laminate.mail` and `laminate.export` into a writable directory, change into it,
and run:

```sh
run_aster laminate.export
```

The export caps CPU time at 300 seconds, requests one CPU and 512 MB. The mesh
has 105 nodes and 160 triangles. Check the actual solver version and message
file, terminal status, tip displacement and mass-normalized modes before
retaining any results. The DKT shell template restrains transverse curvature
to match the analytical coupon's cylindrical-bending assumption; it is not a
free-width composite plate. No shell result, convergence or composite vehicle
acceptance is claimed. Results from this clamped coupon cannot be imported as
an equipped free-body rail vehicle model.

The reduced-modal exchange in `flexible_body.py` accepts only three physical
translational DOFs per node with explicitly stated SI units. An external shell
model's rotational DOFs must be deliberately condensed/exported with its full
mass operator; dropping rotations or guessing units is invalid. The importer
checks mass normalization, eigen residuals, equipped rigid mass/CG/inertia,
prestress/load/boundary applicability, source hashes and convex attachment
interpolation. All current vehicle publications lack complete equipped inertias,
so none can pass this actual-vehicle import contract.

Primary references consulted 25 October 2026:

- [Code_Aster composite plate/shell modeling](https://codeaster.gitlab.io/doc/docaster/manuals/man_u/u2/u2.02.01/M_canique.html)
- [Code_Aster `run_aster` and export files](https://codeaster.readthedocs.io/en/latest/devguide/run_aster/run_aster.html)
- [Code_Aster `NORM_MODE`](https://codeaster.gitlab.io/doc/docaster/manuals/man_u/u4/u4.52.11/index.html)

`publication-pins.json` pins the existing retained publication manifests. The
vehicle reader also verifies its selected payload files and every bound source.
This is a byte/identity check and never substitutes for engineering verification.
