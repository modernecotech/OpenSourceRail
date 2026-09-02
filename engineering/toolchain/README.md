# Engineering Toolchain

This directory records reproducible inputs for the open-source design and
simulation tools selected in
[`../../docs/engineering-design-simulation-plan.md`](../../docs/engineering-design-simulation-plan.md).

The installed environments are intentionally not stored in Git:

- FreeCAD, Blender/Bonsai, QGIS, CloudCompare, and SUMO are user Flatpaks;
- Python solvers and APIs use the repository `.venv`;
- EnergyPlus and FDS use versioned user-local directories beneath
  `${XDG_DATA_HOME:-$HOME/.local/share}/opensource-rail/native/`;
- generated checks and analysis scratch belong under `build/engineering/`.

[`tool-manifest.toml`](tool-manifest.toml) records the adopted releases,
distribution channel, license identifier/source, Flatpak commit or binary
checksum, and deliberately deferred tools.

RTKLIB is installed user-locally with the optional engineering applications,
but remains unused until surveyed-pilot mobilisation because the public
repository contains no raw observations. The deterministic
[`survey_control.py`](../analysis/survey_control.py) gate validates controlled
receipts and runs `rnx2rtkp` when the frozen deployment binary and real RINEX
inputs are present; its automated quality result never records survey approval.

Use the root [one-command setup](../../README.md#one-command-linux-setup) and
accept the optional engineering applications when prompted.

Run engineering workflows through the common launcher:

```bash
./osr engineering --check
./osr engineering --smoke
./osr engineering --benchmarks
./osr engineering --station-ifc
./osr engineering --station-analysis
./osr engineering --flesh-out
./osr engineering --cities --city samawah,songea --jobs 2
./osr engineering --cities --all --generate-only --allow-input-gaps --jobs 8
./osr engineering --cities --all --allow-input-gaps --jobs 2 --resume
```

`python-requirements.txt` pins direct engineering packages and includes the
smaller `ifc-python-requirements.txt` used by IFC CI and GUI jobs. The installer
also writes a full transitive `pip-freeze.txt` manifest under
`build/engineering/toolchain/` so evidence captures the exact environment
that ran it.

The Flatpak applications remain independently versioned because they are GUI
and desktop toolchains rather than Python library dependencies. The check
command captures their installed commits and versions.
The one-command installer selects these locations; users do not need to set
paths or environment variables.

The smoke check performs calculations rather than import-only checks for IFC
creation, an analytical axial bar in OpenSees, a two-bus pandapower load flow,
pvlib plane-of-array irradiance, and a short PyBaMM single-particle battery
model. It also runs a short SWMM rainfall/runoff fixture and rejects excessive
continuity error. `--benchmarks` runs a deterministic JuPedSim normal/constrained
station corridor, the all-variant station structure/flow/drainage screens, and
a SUMO timetable directly from the 13 Samawah Line 1 station chainages.
`--station-ifc` exports all seven positive-volume station product structures
and checks that every BOM/traveler ID round-trips through IFC. The station
analysis executes EnergyPlus and FDS when installed, preserving adverse results
as open findings until project-specific climate/fire inputs and mitigations are
independently reviewed.

[`../analysis/analysis-register.toml`](../analysis/analysis-register.toml) distinguishes planned,
screening, calibrated, independently checked, and accepted analyses. Its
validator requires review metadata at higher maturity and refuses image-only
result artifacts.

## Catalogue-wide city packages

[`../../tools/automation/generate-city-engineering.py`](../../tools/automation/generate-city-engineering.py)
discovers `cities/catalogue/*/*/*/design.toml`; it does not maintain a second city list.
For every selected city it writes:

- a QGIS/GDAL GeoPackage plus GeoJSON review layers for corridors, stations,
  civil segments, energy sites, depots and input issues;
- a SUMO node, edge and route deck containing every declared line and station,
  with edge shapes taken from the canonical corridor GeoJSON;
- pandapower grid-only and coordinated-daylight networks and a pvlib PV-yield
  envelope, with electrical overload/voltage findings retained in the result;
- a machine-readable result with source hash, tool version, service arrivals,
  per-line journey times and explicit input-quality findings;
- a station occurrence map resolving every city station to its shared station
  variant, product-item count, assembly count, open-release count and IFC
  template; and
- per-city logs plus an aggregate `batch-summary.json` under
  `build/engineering/cities/batch-summary.json`.

The generator creates and checks the seven shared station-archetype IFC files
once per batch. It also runs the shared station systems package once; identical
archetype models and results are referenced by city station occurrences rather
than copied thousands of times.

`--generate-only` creates reviewable SUMO decks without launching SUMO; GIS
generation and energy screening still run. Use `--skip-gis` or `--skip-energy`
to omit those package families. Use
`--allow-input-gaps` only for catalogue auditing: findings remain in the
summary and `passed` remains false even though generation is allowed to
continue. Omitting that flag makes input gaps fail the command. A full solver
batch is selected by omitting `--generate-only`.
Use `--resume` after an interrupted or partially successful solver batch; it
reuses only summaries whose design, corridor, scenario and station-manifest
hashes still match and whose simulation, GIS generation, energy solvers and
station-product map passed. Transient launcher failures are retried
automatically at reduced concurrency.

Samawah is the acceptance example; Songea exercises the same code path as a
second city. The generator discovers all 263 canonical designs, and every one
currently has the required `<slug>.corridor.geojson` and `<slug>.toml`
companions. GIS layers use EPSG:4326. SUMO uses a city-local metric projection
for visual geometry while retaining canonical chainage as edge length.
Electrical results are planning screens: the transformer model assumes each
declared site grid-import limit defines its transformer rating, and pvlib
clear-sky output is an envelope rather than measured weather.

These are screening packages. Surveyed geometry, city demand and dwell
calibration, connected interchange/junction topology, road interactions,
local climate/fire inputs and competent review cannot be generated from the
current catalogue and therefore remain explicitly pending.

Each checked-in city deliverable uses only two generated subfolders:
`engineering/` contains alignment, solver results, simulation, screenshots,
and finance validation; `operations/` contains asset, manufacturing,
maintenance, QA, and acceptance evidence. Retry logs and scratch results stay
under `build/engineering/`.

The same command runs EnergyPlus's `1ZoneUncontrolled` design-day example and
the tracked FDS empty-box fixture, then requires each solver's explicit
successful-completion marker.
