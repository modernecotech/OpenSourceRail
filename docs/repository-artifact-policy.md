# Repository Artifact Policy

Git contains the smallest useful set needed to understand, inspect, build,
test, and change OpenSourceRail. Reproducible working output belongs in
`build/`; a small named public-review set may be tracked when GitHub users
otherwise cannot inspect the system without installing specialist software.

## Tracked

- Rust, Python, shell, HTML, CAD-generator, and configuration source.
- RFCs, engineering requirements, safety evidence authored by people, and
  stable schemas.
- Small test fixtures with a named consumer.
- The compact machine-readable city core for every entry in
  `lib/city-batches/world-sample.toml`: `design.toml`, simulator scenario,
  quality result, corridor GeoJSON, and station JSON. Routed designs are
  retained because regeneration can depend on changing external OSM and
  population data.
- Catalogue-wide ring/interchange and station-cluster validation reports.
  These reports are allowed to record inherited planning failures, but their
  source and validator hashes must remain current; reviewed references must
  pass both validators.
- One generated `NATIONAL-BRIEF.md` per country, aggregating city CAPEX,
  imported/external capital, local funding, and the single shared trainset factory.
- Two complete end-to-end acceptance references, Samawah
  (`light-metro-3car`) and Mosul (`metro-4car`), including map, README,
  alignment, simulation, energy, finance, QA, maintenance, manufacturing,
  acceptance evidence, and a fail-closed package manifest. Their simulation
  evidence includes nominal operation plus end-of-life battery, maximum
  planning-climate load, reduced charging-contact availability, all-site grid
  outage, and single-pad outage cases.
- One compact high-throughput architecture reference, Basra (`metro-6car`),
  adding a map and README without duplicating the complete acceptance bundles.
- The Samawah OSR-ALN fixture used by converter tests.
- Compact FreeCAD and Blender review assemblies, the named IFC4.3/IDS/BCF
  federation under `engineering/models/bim/reference/`, stable documentation
  images, and the root `OpenSourceRail-Book.pdf` reader edition. These are
  published review aids generated from authoritative sources, not parallel
  inputs.

## Not tracked

- Rust/Python build products, logs, caches, temporary data, and screenshots
  that are not part of the stable documentation review set.
- Complete generated city engineering and operations packages except the
  named Mosul and Samawah acceptance references.
- Generated BOM exports, simulation traces, release-only brochures, videos,
  repeated CAD/BIM job outputs, and other release binaries.
- Files that only preserve an obsolete schema, chemistry, voltage, or API name.

## Output locations

| Output | Location |
|---|---|
| Full city package | `cities/catalogue/` |
| Repeated simulation and engineering job output | `build/engineering/` |
| Public CAD review set | `design/component-catalogue/models/cad/` |
| Public BIM coordination review set | `engineering/models/bim/reference/` |
| BOM exports | `build/bom/` |
| Published reader book | `OpenSourceRail-Book.pdf` |
| Release-only media | `build/releases/` before tagged release storage |
| Tagged deliverables | Release storage with version and checksum |

Use `tools/automation/regenerate-city.sh <slug>` for a full city package in the
canonical `cities/catalogue/` tree. Catalogue changes must include the corresponding
current-generator scenario and pass the catalogue-completeness health check;
generated engineering and operations directories remain tied to the city
folder that produced them.

## Rules

1. Change canonical source before regenerating output.
2. Do not hand-edit generated output.
3. Every retained fixture must name its generator and test consumer.
4. CI compares compact fixtures and regenerates larger evidence when required.
5. Never commit credentials, caches, absolute local paths, or live operational
   databases.
6. A complete generated city package is not release-ready merely because its
   manifest passes: survey, calibrated demand, local ground/fire/utility data,
   supplier freeze, and independent safety/construction release remain external
   project gates.
7. The root reader PDF is generated, never hand-edited. Its Markdown and city
   model sources remain authoritative and are printed in the book.

## Documentation ownership

- The root `README.md` is the only human-facing navigation page and owns the
  common setup instructions and source-of-truth map.
- A discipline or folder README contains only material local to that subject;
  it links to common guidance instead of copying it.
- City and country pages contain only local values and evidence. Shared planning
  interpretation lives in `docs/deployment-planning-reference.md`.
- `docs/INDEX.md` is a generated inventory for search and CI, not a competing
  guide or technical authority.
- When a claim can be derived, generate it from the authoritative source and
  test for drift rather than maintaining a second prose value.
