# Known limitations for v0.6.0

- The passive-wheel development reference remains a design reference, not a
  physically accepted installation. The installed propulsion architecture is
  not selected.
- Vehicle mass, equipment fit, fasteners, joints, cooling, wiring, clearances,
  fatigue and removal access have unresolved bounds or holds.
- Propulsion force, current, heat, braking and rescue evidence is candidate- and
  model-domain-specific. Numerical convergence does not establish feasibility.
- City demand, route geometry, gradients, ground, utilities, land and access may
  be generic or unsurveyed. Cost ranges are not vendor quotations or approved
  finance.
- The 266-city catalogue is a planning portfolio. It is not 266 independently
  surveyed and engineered railway designs.
- The integrated current engineering dossier currently has a source-binding
  hold. The Workbench shows the selected reference and city geography, but
  keeps global engineering cost and portfolio views held and does not treat the
  stale dossier as current evidence. The dossier is excluded from supported
  v0.6 results and release evidence until its exact provenance is resolved.
  At this source commit, the portfolio hold identifies
  `.github/workflows/development-baseline.yml` as changed from the dossier's
  recorded source hash. The Workbench therefore hides its candidate-portfolio
  selector; use the source-pinned archive described in the demonstrations
  document for read-only research comparison.
  The Samawah software journey binds and verifies its own city inputs and
  calculation.
- The city atlas currently refuses native RustGIS ZIP export because the
  published GIS and outline epochs differ. The source-bound Baghdad result and
  its read-only atlas view remain available; a native GIS export/import round
  trip is not included in v0.6.
- CAD/IFC stock agreement and structural screens do not establish complete
  installed mass, manufacturability, fatigue life or construction approval.
- ERPNext, Frappe HR, FUXA and gateway workflows are configurable software
  examples. Real transactions and live railway commands are not authorized by
  generated drafts.
- Full native CAD/FEM/GIS workflows are optional and limited to declared solver
  versions, resource requests, inputs and model domains.
- Large historical studies remain in the repository history. Sparse checkout
  and optional local cleanup reduce active workspace use, but no repository
  history rewrite or complete artifact migration has been performed.
- Physical prototype validation, independent safety assessment and any
  manufacturing, movement or operating approval remain separate future work.
