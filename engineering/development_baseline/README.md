# Current development adapters

This package exposes the selected v0.6 wheel-supported, station-powered
candidate through the CLI, Workbench, planning handoff and candidate delivery
exports. Vehicle, body, support and propulsion identities must match across all
records. Development selection and successful calculations do not grant
engineering, manufacturing or operating acceptance.

The physical model and engineering evaluators live in
[`station_rail`](../station_rail/README.md). This package resolves the selected
candidate, validates source-bound publications, compiles and verifies planning
proposals, and serves the current read-only Workbench. Unsupported or mixed
candidate identities fail closed. City performance regeneration remains held
pending candidate-specific propulsion, braking, route and economic evidence.

The Workbench's Design Portfolio compares 54 body-stock alternatives and 18
20 m civil spans in separate views. Family filters retain all alternatives;
quantity and mechanics archive filters name their own evidence basis. Candidate
details show low/base/high scoped costs, declared shifts, assumptions, exact
quantity/mechanics identities and remaining engineering tasks. The read-only
`/api/portfolios/current` endpoint checks current source bindings and joins civil
mechanics through the parent portfolio and quantity evaluation. Browsing a
candidate changes neither the selected railway nor its qualification status.

Use `./osr status`, `./osr build`, `./osr verify`, `./osr workbench`,
`./osr plan --help` and `./osr twin export`. See the
[current dossier](../../docs/design-engine/current/README.md),
[candidate delivery index](../../docs/design-engine/coupled-railway/delivery-index.json)
and [project introduction](../../README.md).
