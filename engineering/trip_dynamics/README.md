# Six-car trip dynamics

OpenSourceRail aims for simple construction, low whole-life cost and high passenger throughput. Trains carry all permanent magnets, support/guidance coils and passenger services; ordinary concrete guidebeams carry passive steel facings. Stations provide launch and receiving propulsion. This programme connects those interfaces while preserving GFRP, aluminium-extrusion and named neodymium alternatives as separate physical candidates.

The first campaign keeps six 17 m cars, 120 normal passengers per car and the 14,400 passengers/hour/direction comparison at 180-second headway. It declares straight 1.5 km and 2 km legs, two 350 m station zones, a 20 m/s speed target and 0.8 m/s² nominal acceleration. Those targets do not establish available magnetic force or electrical power.

There are three distinct activities:

- **Evidence attempts** inspect the actual candidate's inventory, magnetic maps, structural applicability, station plant, thermal duty and fault interfaces. Missing or failed inputs refuse dynamic execution. A completed preflight is not a hover or a journey.
- **Chrono benchmarks** execute actual six-body mechanics and couplers with ideal straight support and prescribed mechanical forces. They check the method, common finite station zones and time-step sensitivity. Their force allocation has no current/voltage/thrust qualification and does not become train performance.
- **Design exploration** uses the source-bound alternatives and bounded digital tasks. A smaller mass allocation, a synthetic map or a useful next experiment does not become an integrated selection.

The historical 9.49 t native-material subtotal, canonical 25.619/37.619 t empty/AW3 allocation comparison and newer component-replacement ledgers have different scopes. They are never added together. Complete equipped mass, CG, inertia, flexible-body properties and installation hardware remain unresolved. No full GFRP redesign or accepted aluminium chassis is inferred from a coupon.

## Run and verify

`./osr trip` shows the published packet and private solver status. `./osr workbench` opens the local Workbench; choose **Trip simulations and research tools** to compare the retained vehicle, magnet and equipment options, submit a selected case, inspect logs/results and cancel an owned job. The page also exposes the digital task plan, numerical fixtures and bounded JSON magnetic/modal imports. Imported data is checked numerically without reading client-supplied file paths or granting physical acceptance.

```bash
./osr trip catalogue
./osr trip simulate --mode evidence --distance-m 2000 --load-case AW3 \
  --temperature 50 --output build/trip-dynamics/selected-evidence
./osr trip simulate --mode benchmark --distance-m 1500 --load-case empty \
  --output build/trip-dynamics/selected-method-test
```

Choose a fresh output directory for each CLI experiment. Browser jobs receive private server-owned directories, bounded concurrency and deadlines; closing the server cancels its active jobs and retains their inputs and logs. Reopening the server recovers the job inventory. The solver setup action downloads pinned tools and creates the isolated locked Chrono environment; it does not install Code_Aster. Vehicle/equipment inspection does not silently compose a new physical candidate.

Opening the Workbench checks source and payload integrity without repeating every engineering calculation. Status reports distinguish those checks from numerical reproduction. `tools/automation/osr-python tools/automation/maglev-workbench.py --verify-full` retains the full existing startup verification; trip packet verification is also an explicit action on the page.

Use the existing engineering environment, or install `requirements.txt` in a separate virtual environment. PyChrono must be the **Project Chrono conda package**; the similarly named PyPI package is unrelated. The separately retained Linux runtime lock pins the actual executed conda packages. Do not install its dependencies over the main engineering environment.

```bash
./osr trip setup-tools --output build/trip-dynamics/tool-setup

OPENBLAS_NUM_THREADS=1 .venv/bin/python -m engineering.trip_dynamics run \
  --output build/trip-dynamics/new-campaign \
  --chrono-python "$PWD/build/trip-dynamics/environment/chrono/bin/python" \
  --getdp "$PWD/build/trip-dynamics/tools/getdp-3.5.0-Linux64/bin/getdp" \
  --finite-coupon-archive docs/design-engine/trip-dynamics/finite-coupon-artifacts.tar.gz
.venv/bin/python -m engineering.trip_dynamics verify \
  --output build/trip-dynamics/new-campaign
.venv/bin/python -m pytest -q engineering/trip_dynamics/tests
build/trip-dynamics/environment/chrono/bin/python -m pytest -q \
  engineering/trip_dynamics/tests/test_chrono_runner.py
```

Use a fresh output directory after a source, solver, scenario or candidate change. Inputs and completed outputs are immutable. Verification checks live source/payload identities and rebuilds the evidence gates; it does not rerun FEM or manufacture physical acceptance. Native solver fixtures have separate inputs, logs and numerical dispositions. A missing Chrono installation fails explicitly.

`python -m engineering.trip_dynamics plan` emits bounded specialist task contracts. `evaluate --candidate candidate.json --scenario scenario.json --registry state --output result.json` writes a typed evaluation into the existing immutable design-search registry. Its request binds the candidate, requirements, implementation, scenario and supplied model content. This adapter performs readiness evaluation; it cannot select an integrated train with unknown models.

## Model boundaries

The common right-handed frame is x along travel, y left and z up. Magnetic maps retain forces and moments, origin, axes, units, current ports, temperature and speed domains. Queries outside the complete sampled envelope are refused. A static 2D lift scalar does not supply missing moments, moving drag or electrical loss. Missing flux/energy/loss ports remain unknown.

Reduced structural models retain equipped mass and inertia congruence, equilibrium, boundary/load/fault applicability, mass-normalised modes and attachment virtual work. Imported numerical checks and checked source files have distinct dispositions. Immutable modal snapshots prevent later data mutation from silently changing the attachment model. The synthetic laminate/beam coupon is independent of the vehicle and does not count as a Code_Aster execution.

The first modal exchange accepts three translational DOFs per node. Reconstruction of module orientation and general moment transfer still needs a verified interface. Likewise, available magnetic energy/flux ports do not by themselves establish energy reciprocity or closed-loop stability; joint confirmation remains required.

The existing Rust current-loop ABI executes at 50 µs inside a declared mechanical clock. Its electrical fixture retains current, voltage, copper heat, field energy and sensor-loss refusal. It does not invent a current-to-force law. Full moving station-drive, field-energy, battery, HVAC and repeated thermal coupling remains gated until matched component data exists.

Expensive magnetic and structural solves belong offline. Their reduced models may enter the moving simulation only after domain and convergence checks. The current first campaign explicitly refuses all unevaluated criteria instead of manufacturing a successful launch-to-arrival trace.

## Tool references

- [Project Chrono modal analysis and reduction](https://api.projectchrono.org/manual_modal.html) and [Python installation](https://api.projectchrono.org/pychrono_installation.html).
- [GetDP formulations and tutorials](https://getdp.info/doc/texinfo/getdp.html), with [Gmsh geometry and meshing](https://gmsh.info/doc/texinfo/gmsh.html).
- [Code_Aster source and verification cases](https://gitlab.com/codeaster/src). The retained shell template is explicitly unexecuted on this host.

[Project introduction](../../README.md) · [Current journey report](../../docs/design-engine/trip-dynamics/README.md) · [Existing candidate design method](../design_search/README.md)
