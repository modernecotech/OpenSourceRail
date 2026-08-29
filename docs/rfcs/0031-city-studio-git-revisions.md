# RFC 0031 — OSR City Studio and Git-Based Design Revisions

**Status:** accepted, initial vertical slice implemented · 2026-08-26  
**Authors:** OSR project  
**Complements:** RFC 0018 operator GUIs, RFC 0028 construction QA,
RFC 0029 maintenance schedules, RFC 0030 manufacturing schedules

## 1. Decision

OpenSourceRail will provide **OSR City Studio**, a browser-accessible design
and service-planning environment over the existing deterministic generator,
GIS sidecars, simulator, engineering toolchain, CAD generators, and operations
packages.

Git is the authoritative revision and approval history. The Studio edits
small, reviewable project-intent files. It never treats its working database,
browser state, or generated build directory as the source of truth.

The generated city design.toml remains a compiler output. Interactive edits
are recorded as intent overrides, constraints, geometry locks, and service
plans. This prevents the next catalogue regeneration from silently replacing
an accepted station movement.

## 2. Goals

- Reproduce a city revision from versioned inputs without hidden GUI state.
- Edit station intent and service levels by line, day type, and time window.
- Preserve stable object ids through manual review and regeneration.
- Preview changes before accepting a candidate.
- Pin source data, tool versions, parameters, and generated artifact hashes.
- Review revisions through ordinary GitHub branches and pull requests.
- Publish approved revisions as signed or protected tags/releases.
- Keep planning changes outside the live safety-critical OCC command path.

## 3. Non-goals of the initial slice

- Reimplement FreeCAD, QGIS, or detailed B-rep editing in the browser.
- Send route grants or other safety-critical commands to a live railway.
- Automatically push branches, open pull requests, or create remote tags with
  a user's GitHub credentials.
- Commit every pointer movement or autosave.
- Store raw imagery, solver scratch directories, or large simulation traces in
  ordinary Git history.

## 4. Project package

Each city has a committed package under projects/<slug>/:

    projects/<slug>/
    ├── project.osr.toml
    ├── sources.lock.json
    ├── network/
    │   └── overrides.toml
    ├── services/
    │   └── service-plan.toml
    ├── coordination/
    │   └── issues.toml
    ├── demand/
    │   └── od-matrix.toml
    ├── approvals/
    │   └── reviews.toml
    └── revisions/
        ├── README.md
        └── osr-<content-hash>.json

project.osr.toml declares identity, paths, planning assumptions, the default
branch, revision policy, and approved tag prefix. Paths are resolved relative
to the project package so a checkout remains portable.

sources.lock.json records a SHA-256 for every authoritative generated or
external input. Compilation fails validation if the bytes differ. Updating a
source is therefore an explicit project change that must update its lock.

network/overrides.toml records stable station ids and one of:

- generated: the generator may replace it;
- preferred: regeneration should penalize movement but may propose it;
- locked: regeneration must preserve the accepted location;
- manual: created by a designer rather than the generator;
- retired: retained in history but excluded from the candidate.

The compiler supports generated, preferred, locked, and retired states for
source stations, plus manual and retired states for designer-created stations.
Moving a station deterministically warps its affected
corridor inside the project regeneration radius, holds accepted locked
stations as zero-displacement anchors, recalculates the affected route length
and simulator inter-station distances, and preserves unaffected line geometry.
The map also supports stable, click-to-create alignment control points. A
designer can drag a point, choose its regeneration influence radius, and mark
it preferred or locked; the same deterministic corridor and simulator
regeneration then applies. Manual station insertion or retirement rebuilds the
effective simulator station catalogue and ordered per-line topology as well as
the GIS network. A two-endpoint manual-line workflow creates a stable line id,
deterministically sampled initial corridor, two terminal platforms, a service
plan for every day type, and simulator line/fleet/dispatch records. Local
alignment controls can then shape the corridor. Manual lines can use either an
explicit direct chord or a deterministic least-cost route over SHA-256-locked
demand/buildability planning surfaces; the revision records the method,
source IDs, and demand weight.

services/service-plan.toml contains a seven-day calendar mapped to named day
types and a plan for every line/day-type pair. Each plan has a service span and
contiguous headway windows. The compiler calculates cycle time, indicative
peak fleet, capacity per hour per direction, daily service kilometres, and
weekly service kilometres.

demand/od-matrix.toml contains source-controlled planning periods and optional
origin–destination flows in passengers/hour. Periods refer to service day
types and time intervals; flows refer only to active stable station IDs. A
content-derived ID preserves flow identity while the passenger rate is edited.
The compiler screens each record against the lower scheduled
passengers/hour/direction capacity across all service windows overlapping the
period and records direct/cross-line status and indicative utilization. This
early screen is deliberately not a passenger assignment, ridership forecast,
platform-flow model, or interchange/egress analysis.

coordination/issues.toml stores review decisions for deterministic civil BCF
topics. Status, assignee, resolution, and reviewer are project intent rather
than edits to a generated job artifact. Resolving or closing an issue requires
a substantive resolution and reviewer. The compiler validates the issue set,
includes it in the project hash and immutable revision snapshot, and reports
semantic issue-state changes in revision comparison. A new civil BIM job then
emits a new BCF reflecting that revision; earlier BCF files remain immutable
evidence.

Designers may seed a new issue from a selected IFC asset. City Studio validates
the title, description, and one-to-fifty stable OSR asset IDs and derives a
deterministic `custom-<content-hash>` identifier. The civil adapter rejects
unknown assets, then derives stable BCF topic and viewpoint UUIDs from that
identifier. Re-entering identical content is rejected as a duplicate rather
than silently creating parallel issues.

## 5. Revision lifecycle

    working draft
        │ save intent/service files
        ▼
    Git-visible working tree
        │ compile and validate
        ▼
    candidate snapshot in build/
        │ materialize revision
        ▼
    projects/<slug>/revisions/osr-<hash>.json
        │ branch + commit + pull request
        ▼
    projects/<slug>/approvals/reviews.toml
        │ append reviewer decision + review reference
        ▼
    reviewed merge
        │ protected/signed tag
        ▼
    approved design baseline

Autosaves do not create commits. **Materialize revision** writes an immutable,
content-addressed JSON record only when validation has no errors. It includes:

- project identity and schema version;
- source locks and their observed hashes;
- effective lines and stations;
- complete weekly service plans and fleet/capacity metrics;
- planning periods, OD flows, and conservative scheduled-capacity metrics;
- civil coordination issue status, assignment, resolution, and reviewer;
- semantic station movements;
- validation findings;
- exact project-input SHA-256, compiler version, and embedded compiler/UI
  source SHA-256;
- content SHA-256;
- parent Git commit.

The content hash excludes wall-clock time and Git branch state. Recompiling
the same project bytes produces the same content hash and revision id. The
revision record separately pins the Git commit from which the candidate was
created.

The Studio suggests a branch and tag; users or CI perform remote GitHub
operations. This avoids embedding personal tokens or silently rewriting
repository history.

Approval decisions are append-only records referring to an existing immutable
revision. Each records approved or changes-requested status, reviewer and role,
decision date, rationale, and a pull-request or evidence reference. A stable
content-derived `approval-…` id makes identical submissions idempotent.
Approval metadata is intentionally excluded from the design content hash:
otherwise approving a revision would create a different revision requiring a
new approval. The TOML approval history remains Git-reviewed alongside the
revision and can survive migration away from GitHub.

## 6. Determinism contract

OSR uses three determinism classes:

1. **Byte deterministic:** project files, JSON/TOML/GeoJSON/CSV outputs,
   revision manifests, and schedules.
2. **Geometry deterministic:** CAD/GIS exports may contain tool metadata or
   archive timestamps but must be geometrically equivalent within a declared
   tolerance.
3. **Analysis deterministic:** numerical solvers must reproduce accepted
   results within a declared tolerance using pinned inputs and tool versions.

Remote OSM, population, building, terrain, imagery, and survey inputs must be
captured or checksum-locked. Running against an unpinned live endpoint is an
exploration, not a releasable design revision.

## 7. Architecture

The initial implementation is crates/osr-city-studio:

- a Rust project compiler and validator;
- deterministic source hashing and revision ids;
- semantic station movement detection;
- manual station authoring and simulator-topology regeneration;
- manual line authoring with terminal, service, GIS, and simulator synthesis;
- semantic comparison between materialized revisions and the working candidate;
- weekly service metrics;
- deterministic OD demand intent, validation, scheduled-capacity screening,
  and semantic flow comparison;
- a local HTTP API;
- an embedded browser UI with an editable, layered local SVG/GIS view whose
  source catalogue, feature counts and SHA-256 digests are served with the
  project;
- artifact visibility for current design, GIS, simulation, engineering,
  operations, and release outputs.

The server binds to localhost by default. It reloads committed project files
for each request so external Git changes are visible. Writes are serialized
and published atomically.

The longer-term tool adapter boundary is:

    declared inputs + parameters + tool version
                       │
                       ▼
                 allowlisted adapter
                       │
                       ▼
    artifact + logs + findings + content hashes

The first implemented adapters compile the candidate GIS package, run a fixed
one-hour `osr-sim` day-type scenario, and export a selected line through
`osr-alignment-export` to LandXML, railML, review JSON, and stakeout CSV. They
serialize through one job slot, persist records and full logs, expose progress
and bounded log tails, and hash every output. Adapter names, binaries, and
arguments are selected by Rust code; the browser cannot supply an executable
or unrestricted shell text. Future adapters may wrap osr-design,
osr-scenario, GDAL/QGIS, FreeCAD/IFC, SUMO, pandapower/pvlib, finance, and
operations generation under the same boundary.

Successful jobs copy their review evidence into the job-specific directory so
later candidate compilations cannot overwrite the recorded files. The browser
artifact endpoint canonicalizes the selected record path beneath the City
Studio build root, limits preview size, accepts only known JSON/XML/CSV/text
formats, and verifies the recorded SHA-256 before returning content. The GUI
plots GeoJSON, local alignment points, LandXML geometry, and stakeout data and
summarizes railML and simulator evidence. For civil review it joins the
verified object index and 4D sequence to provide deterministic envelope
rotation, native IFC presentation-layer visibility, construction-stage playback, task/QA context,
and stable BCF object picking. These previews are not an authoritative CAD or
safety-assurance tool; native IFC detail remains in Bonsai.

## 8. GitHub review policy

An approved city revision should use:

- protected default branches;
- pull requests rather than direct pushes;
- required City Studio validation;
- engineering and operator review appropriate to the changed objects;
- immutable release tags;
- signed tags where the deployment governance supports them;
- an in-repository approval record for decisions that must survive migration
  away from GitHub.

Text, compact geometry, summaries, manifests, and approval records belong in
Git. Large FreeCAD/Blender/IFC packages, imagery, rasters, videos, and raw
solver output belong in Git LFS, GitHub Releases, or deployment-controlled
artifact storage. Their hashes and generating inputs remain in the revision.

Geo and service files use stable ids, sorted records, and canonical
serialization. The Studio will add object-aware merge conflict reporting
before concurrent multi-user editing is promoted.

## 9. Safety boundary

City Studio produces planning candidates and approved configuration packages.
It cannot issue a movement authority, route grant, maintenance override, or
degraded-mode command.

The OCC may consume an approved, signed baseline. Live actions remain governed
by RFC 0013, RFC 0017, RFC 0018, deployment roles, and the deployment safety
case. Sharing a map renderer or object id does not merge those authorities.

## 10. Implemented acceptance fixture

The Samawah project is the first committed acceptance fixture. It:

- pins the current design, corridor, and simulator scenario;
- locks all three platforms in the accepted CBD interchange;
- defines weekday, Friday, and weekend service for all three lines;
- produces nine line/day-type service metric records;
- exposes 21 station platforms in the Studio map;
- regenerates affected GIS corridor geometry and simulator distances after a
  station movement while preserving locked station anchors;
- supports direct line edits through stable alignment control points with
  editable influence radii;
- creates, moves, renames, classifies, and retires manual stations while
  regenerating GIS and simulator topology;
- creates and retires complete manual lines, including terminal platforms,
  weekly services, fleet sizing, dispatch points, and candidate geometry;
- creates manual lines through either source-locked demand/buildability
  least-cost search or an explicitly identified direct planning chord;
- records routing method, demand weight, and every raster/provenance source id
  on the line and in candidate GIS output;
- compares old revision records with the working candidate using engineering
  tolerances for serialized floating-point values;
- persists civil coordination decisions as Git-reviewable intent, rejects
  unsupported or unevidenced closures, and carries accepted state into a newly
  generated BCF without mutating prior job evidence;
- creates deterministic custom BCF topics from selected IFC assets and rejects
  duplicate content, invalid asset IDs, and dangling selections;
- loads the hash-verified civil 4D sequence with discipline filters, rotation,
  task-stage playback, and stable object selection;
- appends deterministic approval decisions only for existing immutable
  revisions and proves that approval does not alter the design hash;
- emits separate weekday, Friday, and weekend simulator scenarios plus a
  SHA-256 artifact manifest;
- runs allowlisted GIS, simulator, and LandXML/railML alignment jobs with
  persistent status, captured logs, and SHA-256 output records;
- retains immutable per-job artifact copies and rejects altered evidence before
  browser preview;
- compiles without validation errors;
- produces an identical content hash across repeated compilations.

The next acceptance increment is native IFC geometry streaming plus demand/OD
and interchange-capacity inputs.
