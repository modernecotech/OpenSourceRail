# Edea — city planning geography

This page provides geographic and service-planning inputs for Edea, CM. Open the planning workspace to review the mapped corridors and edit route, stop, service and origin-destination proposals.

The planning handoff is bound to the selected v0.6 candidate and contains proposals only. A separate calculated city outline prices the mapped network, service, fleet, civil quantities, production and lifecycle using explicit estimates. That outline does not release a physical design or grant movement authority.

[Inspect the priced city outline](../../../../../docs/workbench/current/index.html?outlineCity=edea) · [Outline methods and coverage](../../../../../docs/design-engine/outline-completion/README.md)

Compile and verify a proposal from the repository root:

```bash
./osr plan compile edits.json --output build/my-plan
./osr plan verify build/my-plan
```

[Edea route geometry](edea.corridor.geojson) · [Geographic context](map-context.json.gz) · [Current v0.6 city hold](../../../../../engineering/current/README.md) · [Planning workspace](../../../../../docs/workbench/planning/index.html?city=edea)

Selected candidate `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3` · selection `8e5905bc7c81d6177bbaafde81ab3a5f8cc54947c4923eb4493949566ac85cdc` · evaluation `d5a6fe9ce12ce6a17e9f585e9f77165dcc3c321f0ba3faac2bacaff8d91969bb`
