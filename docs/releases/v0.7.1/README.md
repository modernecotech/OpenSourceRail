# OpenSourceRail v0.7.1 — Baghdad and control update

This patch release retains the [v0.7.0 digital railway reference](../v0.7.0/README.md) and adds the [Baghdad proposal](../../../cities/Baghdad/PROPOSAL.md) as two independent planning alternatives. The 148.2 km seven-corridor concept is estimated at **US$7.866bn**; the separate 605.652 km citywide concept is estimated at **US$31.018bn**. Both use zero tunnels, elevated revenue alignments and a protected trackside conductor as the selected offwire supply case. The maps, route tables, train and station quantities, fourteen capital scopes, 30-year costs, construction cash schedules and local production assumptions are in the Baghdad city folder.

The Baghdad train's installed control schedule now counts 299 kg and 3.68 kW per six-car train within its stated 350 kg and 6 kW reserves. Powered-wheel ATP and protected-conductor TCMS adapters distinguish the selected traction supply from the essential service battery and inhibit traction when contact, section or inverter proofs are absent. The public Workbench exposes each network's service groups and locally addressable contract value.

The [release record](../../RELEASE-v0.7.md) states the digital evidence and its boundaries. The v0.7.0 tag remains the historical first release; v0.7.1 is the source-bound update. Neither release grants manufacturing or passenger-operation approval.

## Reproduce

```sh
git clone --filter=blob:none --branch v0.7.1 https://github.com/modernecotech/OpenSourceRail.git
cd OpenSourceRail
./osr reference v07
python3 -m engineering.outline.baghdad_system --check-results
./osr book --check
```

The reference command reproduces the selected synthetic 30 km digital railway. The Baghdad command checks the separately selected city cost and equipment cases.
