# Unified Deployment Model

OpenSourceRail has one deployment model. A city such as Samawah,
Baghdad, Karachi, or Lyon is an **instance** of the same pipeline, not a
fork of the architecture.

## Rule

No deployment gets a special OSR stack. City-specific information is
limited to inputs and generated artifacts:

- city record in `lib/city-batches/world-sample.toml`;
- country, cost, finance, climate, regulatory, and workforce templates
  under `lib/templates/`;
- optional recipe adjustments in `lib/recipes/`;
- generated design outputs under `designs/<region>/<country>/<city>/`;
- deployment-specific survey, asset, operator, and assessor evidence.

Everything else stays shared: train families, track geometry presets,
station archetypes, hardware host classes, operations rules, safety
requirements, certification evidence structure, and regeneration tools.

## Pipeline

1. Add or update the city record and country assumptions.
2. Run `scripts/regenerate-city.sh <slug>`.
3. Review the generated network, scenario, cost, energy, fleet, station,
   depot, and quality outputs.
4. Export civil alignment from the generated design through OSR-ALN.
5. Build the pilot hardware through the RFC 0019 COTS/SBC integration
   track, or choose the RFC 0007 custom-board track when volume or
   deployment constraints justify it.
6. Fill the deployment evidence gaps: survey, supplier quotes, workshop
   audit, bench logs, first-article tests, operator review, independent
   assessor review, and regulator submission.

## Samawah's Role

Samawah is the worked Iraq instance because it combines a generated
city network with a plausible brownfield rail-yard/workshop asset base.
It is not a special architecture, special train, special hardware path,
or special certification path.

When a city-specific document disagrees with the generated city design,
the generated design wins. Superseded worked examples should be removed
rather than kept as parallel plans.

| Artifact | Role |
|---|---|
| `designs/west-asia/Iraq/Samawah/` | Authoritative generated city model and public planning numbers |
| `docs/rfcs/0003-samawah-reference-deployment.md` | Context, pilot rationale, risks, and next steps |
| `docs/stations/standard-archetype/` | Shared station-archetype worked example; city-specific station lists come from generated designs |

## Outputs To Keep Unified

| Area | Shared source | City-specific output |
|---|---|---|
| City design | `osr-design`, `design-py`, `lib/templates/` | `designs/<region>/<country>/<city>/design.toml` and generated README |
| Civil alignment | RFC 0009 + OSR-ALN tools | per-line `.aln.toml`, survey replacement, civil-class summary |
| Rolling stock | RFC 0008 families + rolling-stock packages | selected family and fleet count |
| Stations | RFC 0010 archetypes | station archetype assignments and site adaptations |
| Energy | RFC 0002/0021/0024/0026 | station/depot/solar plant sizing and utility study |
| Hardware | RFC 0019 integration or RFC 0007 custom boards | SKU freeze, wiring, enclosures, bench records |
| Certification | `docs/certification/` | assessor report, field evidence, national submission |

## Anti-Patterns

- Creating a city-specific train family when an existing family fits.
- Hard-coding Samawah, Baghdad, or any other city into shared tools.
- Treating a worked civil package as the source of truth after the
  generated design changes.
- Publishing cost, fleet, or energy figures outside generated outputs
  without a regeneration path.
- Forking safety requirements or operations rules by city instead of
  parameterising deployment evidence.
