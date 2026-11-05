# Bamako — city planning geography

This page provides geographic and service-planning inputs for Bamako, ML. Open the planning workspace to review the mapped corridors and edit route, stop, service and origin-destination proposals.

The planning handoff is bound to the selected v0.6 candidate and contains proposals only. A separate calculated city outline prices the mapped network, service, fleet, civil quantities, production and lifecycle using explicit estimates. That outline does not release a physical design or grant movement authority.

[Inspect the priced city outline](../../../../../docs/workbench/current/index.html?outlineCity=bamako) · [Outline methods and coverage](../../../../../docs/design-engine/outline-completion/README.md)

Compile and verify a proposal from the repository root:

```bash
./osr plan compile edits.json --output build/my-plan
./osr plan verify build/my-plan
```

[Bamako route geometry](bamako.corridor.geojson) · [Geographic context](map-context.json.gz) · [Current v0.6 city hold](../../../../../engineering/current/README.md) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=bamako)

Selected candidate `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3` · selection `8e5905bc7c81d6177bbaafde81ab3a5f8cc54947c4923eb4493949566ac85cdc` · evaluation `1b30f82b538bf30511692b20e4b207eaf3dd7b581cc0e6ad3fa8357d1a1d200e`
