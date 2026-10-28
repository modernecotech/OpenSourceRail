# Component, material and manufactured-form master

This research registry separates a reusable **part definition** from each physical
**occurrence**. It supplements the retained inventory/evidence contracts and does
not rewrite or approve them. Source: `registry.py`; schema: `data/schema.json`.

```python
from engineering.component_registry import make_part, make_occurrence, make_registry, summary
from engineering.component_registry.materials import lookup
m = lookup('AL-6082-T651-SHEET')
p = make_part('OSR-EXAMPLE-PLATE', 'A', ['attachment'],
    {'kind': 'box', 'dimensions_m': [1., .2, .01]}, m['material_id'],
    {'calculated_kg': 5.4, 'lower_bound_kg': 5.36, 'upper_bound_kg': 5.44,
     'evidence_state': 'calculated'}, {'method': 'cut-drill-deburr', 'scrap_fraction': .1})
r = make_registry('Example, not a released assembly', [p],
    [make_occurrence('plate/1', p)], ['attachment'])
print(summary(r))
```

`physical_definition_id` binds shape, material, interface, electrical/thermal
specification and physical manufacturing definition. `revision_id` also binds the
mass estimate, source evidence, costing and process/lifecycle records. Candidate
identity binds the physical definitions, occurrence poses and assembly graph.
A material `material_id` binds grade/composition/form/process state/layup; its
`material_evaluation_id` separately binds density, constitutive properties and
source provenance. Correcting a same-grade density or allowable changes the
evaluation and invalidates downstream numerical work without inventing new
hardware. Grade/form/layup substitutions change physical identity. Adding a quote,
renaming a review or refining a mass estimate changes the registry revision
without inventing a different geometry. A material/geometry substitution invalidates the
mass, structural, thermal, propulsion, braking, civil, manufacturing, cost and
control dependencies. Parent candidate ancestry is explicit.

Every occurrence has its own ID and rigid 4×4 transform from the centred local
part frame to the named registry frame (metres). Parent IDs record ownership;
transforms are global and are not applied a second time through the parent.
Declared virtual assemblies carry no extra mass. Duplicate occurrences, cycles,
unused definitions, stale part revisions, mixed candidates, non-rigid/reflected
poses, malformed intervals and residual accounts inserted as stock are refused.
The bounded contract permits 10,000 definitions, 200,000 occurrences and 64 levels.

Box, cylinder, annular tube and rectangular hollow-section primitives have net
volumes and uniform-density inertia tensors. A purchased equipment envelope is a
space claim with separate mass bounds, not a dense solid. Unknown mass, price,
origin, installed CG/inertia or supplier data remains unknown. The summary
separates count-based mass coverage, bound coverage, price coverage and validation
coverage. These are never combined into a percentage called design complete.
Calculated primitive CG/inertia is not installed measured CG/inertia.

`screen_sweep(registry, occurrence_id, end_transform, tool_radius_m=...)` checks a
conservative finite removal/tool volume against every other located occurrence.
Translation at a constant rotation has a swept AABB; rotation uses an enclosing
sphere swept between centres. Explicitly removed-before-motion occurrences are
recorded. Clear final-position geometry cannot erase an intermediate collision.
A clear AABB screen does not qualify retention, services, hoists, work sequence or
complete installation. Positive retention, fasteners, adhesive and flexible
services remain separately counted items/interfaces in the equipped generator.

## Material source status

`materials.catalogue()` carries twelve initial grade/form hypotheses across the
nine requested families plus adhesive, elastomer and fastener stock. Directional
laminate schedules, hot/wet laws, fatigue/creep, rail fire/smoke/toxicity, lot
properties, actual country of origin, qualified tolerances and prices stay empty
until supported. A supplier typical modulus is not a structural allowable.

- [Gurit Kerdyn TDS 14-0524](https://www.gurit.com/wp-content/uploads/bsk-pdf-manager/2024/12/TDS-Kerdyn-14-0524.pdf): nominal Kerdyn 80 density **80 kg/m³**, typical range **75–85 kg/m³**. Actual PDF bytes retrieved on 28 October 2026, SHA256 `37513540751a0b147706138283e34a8b362a03bc0a10501917390fcc273afb3b`. The published range is not delivered-lot acceptance.
- [Hulamin 6082 rolled-products sheet](https://www.hulamin.com/sites/default/files/downloads/6082%20Data%20Sheet.pdf): typical density **2,700 kg/m³**, modulus **70 GPa**, linear expansion **24×10⁻⁶/K** and stated electrical resistivity retained as numerical facts. PDF bytes retrieved on 28 October 2026, SHA256 `17526abe0e4a1b0778a05708d7e451a487947976cc21babcdcdd86118af082a0`. T651 sheet scope does not automatically qualify an extrusion or welded joint.
- Hydro 6082 extrusion and SABIC LEXAN 9030 records are **search-index leads**. Their direct URLs returned 404/DNS failure during this run; `retrieved=False`, no fabricated document hash. Their indexed typical facts need direct-source confirmation before design use.
- The other density intervals are the user's 28 October review ranges or named research hypotheses. Bounds on sourced nominal densities are explicit search assumptions unless the source actually provides the range. They are not statistical confidence intervals, qualified material substitutions or sourcing prices.

Raw copyrighted datasheets are not redistributed here. The master records include
source URLs, content hashes where actually obtained and exact provenance status.

## Checks

```bash
.venv/bin/python -m pytest -q --import-mode=importlib engineering/component_registry/tests
```

Tests cover multiplicity, net cavities, rigid transforms and parallel-axis
inertia, unknown equipment, material invalidation, commercial-only revisions,
forged identities, double accounting, cycles, bounds and intermediate sweep
collisions. All manufacturing and operating release flags remain false.
