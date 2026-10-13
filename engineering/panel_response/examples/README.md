# Retained panel response study

[Summary](summary.json) compares five physical arrangements. [Manifest](manifest.json) binds their definitions, complete meshes, pressure responses, all single-clip-loss envelopes, pressure holdouts, combined loss/pressure cases and softer-joint sensitivities.

[Comparison figure](deflection-comparison.png) displays nominal dry deflection and the actual attachment locations. [Native CAD](cad/README.md) verifies all five arrangements; [native formulation verification](native-benchmark/README.md) checks the numerical plate element independently.

The filename prefix identifies the arrangement: `baseline`, `closer-supports`, `dense-supports`, `tight-supports` or `deeper-rails`. The suffix identifies the scenario. Core properties, manufacturing definitions and every response remain unqualified research inputs/results. Follow the [parent documentation](../README.md) to reproduce or interpret them.

[Manufacturing rejection](manufacturing-rejection.json) retains the invalid 0.35 m arrangement's [contract](rejected-035-contract.json). Its potting/core overlap prevents ranking or physical release.
