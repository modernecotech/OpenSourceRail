# Additional retained service-energy source epoch

This record preserves source bytes and packet inventories for 14 additional
manifests affected by a proposed service-battery correction. It covers 442
current-context source files and separately authenticates the older 26-file
physical-followup producer epoch. Together with the [first retained archive](../retained-battery-source-epoch/README.md),
the two current-context source maps cover 517 unique source files without
mixing their recorded identities.

The original packet trees are required at verification time. A fresh checkout
must first reconstruct the sourced-cell archive from its five pinned chunks:

```bash
python tools/automation/sourced-archive.py ensure docs/design-engine/sourced-case
python -m engineering.design_search.retained_service_energy_epoch verify \
  --root . \
  --archive-directory docs/design-engine/retained-service-energy-extra/original/worker-v7/archive \
  --pins docs/design-engine/retained-service-energy-extra/original/worker-v7/pins.json \
  --expected-pins-id 91d8be8f7893aea692e90683c214bbda0d35c4dbe1a652c7cb8908e3d3a4f050 \
  --expected-archive-id d2f4511f180592083945bb993658353218b9efcf91d0dd3f21d02e58399967b9
```

The archived worker handoff retains its producer, tests, logs and v6 handoff.
Earlier draft captures remain in the originating local run directory; their
producer bytes were not all saved, so their numerical replay is not claimed. This record verifies
historical bytes only: it does not replay solvers, grant current-evaluator
admission, prove physical equivalence or approve a railway. Packet restoration
and the remaining current-source regeneration are still needed before the
charging correction can be merged.

Verification uses process resource limits but no filesystem or network
sandbox. Pre- and post-checks cannot exclude a concurrent process that swaps
and restores bytes between checks.
