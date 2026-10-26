# Current development selection adapters

These adapters expose the [v0.6 wheel/LIM research selection](../development-baseline.toml) through the CLI, Workbench, reference evaluations, delivery drafts and reader. Vehicle, body, support and propulsion identities must match. All physical, manufacturing and operating release flags remain false.

The implementation lives in [station_rail](../station_rail/README.md). The selector supports an explicit family registry with retained v0.5 maglev evidence and an unbuilt LSM comparison; unsupported or mixed physical candidates fail closed. City numerical regeneration is held pending reference propulsion, braking, route and economic evidence.

Use `./osr status`, `./osr build`, `./osr verify`, `./osr test` and `./osr workbench`. [Current dossier](../../docs/design-engine/current/README.md) · [Historical v0.5](../../docs/archives/v0.5-maglev/README.md) · [Project introduction](../../README.md).
