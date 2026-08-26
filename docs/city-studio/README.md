# OSR City Studio

OSR City Studio is the Git-backed design and service-planning interface for
OpenSourceRail. The initial vertical slice loads Samawah, displays its
geographic corridors and stations, records station locks or movements,
configures service by line/day/time, calculates fleet and capacity screens,
compiles a deterministic candidate, and materializes a revision for GitHub
review.

The controlling design decision is
[RFC 0031](../rfcs/0031-city-studio-git-revisions.md).

## Run

From the repository root:

    cargo run -p osr-city-studio -- serve

Open http://127.0.0.1:8090/.

Use another project or port with:

    cargo run -p osr-city-studio -- \
      --project projects/samawah serve --port 8091

The server binds only to localhost by default. The initial interface has no
authentication and must not be exposed as a shared or public service.

## Command line

Validate source locks, station intent, calendars, and all line/day plans:

    cargo run -p osr-city-studio -- validate

Write a deterministic working snapshot under build/city-studio/samawah/:

    cargo run -p osr-city-studio -- compile

Write projects/samawah/revisions/osr-<hash>.json:

    cargo run -p osr-city-studio -- revision

Inspect the branch, parent commit, and uncommitted paths:

    cargo run -p osr-city-studio -- git-status

List immutable project revisions or compare one with the working candidate:

    cargo run -p osr-city-studio -- revisions
    cargo run -p osr-city-studio -- compare osr-1f41358e43a86600

Validate every committed city project:

    python3 scripts/validate-city-projects.py

## Revision workflow

1. Create a branch.
2. Use the Studio to edit station intent and service plans.
3. Compile and resolve every validation error.
4. Materialize a revision.
5. Review the Git diff, including semantic changes in the revision JSON.
6. Commit the project inputs and revision together.
7. Push and open a GitHub pull request.
8. After approval and merge, create the suggested protected or signed tag.

Materializing a revision does not run git add, commit, push, or contact GitHub.
Remote repository changes always remain an explicit user action.

## Current editing scope

Implemented:

- source hash locks;
- stable station ids;
- generated/preferred/locked/retired station intent;
- drag-to-move stations;
- click-to-create manual stations with stable content-derived ids;
- manual station naming, archetypes, movement, and retirement;
- locked-anchor-aware local corridor regeneration after station movement;
- click-to-create and drag-to-edit alignment control points;
- weekly day-type calendars;
- per-line contiguous time windows and headways;
- indicative cycle, fleet, capacity, daily and weekly service metrics;
- validation findings;
- deterministic candidate and revision hashes;
- in-GUI semantic comparison of station, line, service, and summary changes;
- day-type-specific simulator scenarios and a hash-addressed artifact manifest;
- visibility of existing GIS, engineering, simulation, operations, and release
  artifacts.

Next:

- manual line creation and source-locked demand-aware route search;
- simulator and engineering job adapters with progress/log capture;
- CAD/IFC and richer GIS viewers;
- demand/OD matrices and platform/interchange capacity;
- project approval records and object-aware Git merge assistance.

## Map authoring

The map has three explicit tools. **Select** inspects and drags existing
objects. **Add station** inserts a manual station where a line is clicked,
assigns a stable id, and opens its name/archetype inspector. **Edit alignment**
adds a local corridor control point. Manual station additions and retirements
rebuild both the candidate GeoJSON and the station definitions and ordered
line references in every generated simulator scenario.

The revision comparison panel compares any committed revision JSON with the
current working candidate. It reports object additions, removals, movements,
line length/station-count changes, and service/fleet/capacity deltas before a
new revision is materialized.
