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

The additional packet materializer has a recorded streaming audit of all 365
tracked Git blobs and the five sourced-cell chunks, without a full local tree.
Its full reconstruction and verification passed on an ephemeral runner in
[the required CI job](https://github.com/modernecotech/OpenSourceRail/actions/runs/41515140831).
This verifies historical bytes, not a current evaluator replay. To run it
manually, fetch the pinned commit and choose a fresh private output path with
at least 1.3 GiB free:

```bash
git fetch --no-tags --depth=1 origin 5cd6b8ff9b2fdf3c705f0d68073543c58e6dec76
retained_extra_parent=$(mktemp -d)
python -m engineering.design_search.retained_service_energy_materialize materialize \
  --git-repo . --output "$retained_extra_parent/packets" \
  --archive-directory docs/design-engine/retained-service-energy-extra/original/worker-v7/archive \
  --pins docs/design-engine/retained-service-energy-extra/original/worker-v7/pins.json \
  --expected-commit 5cd6b8ff9b2fdf3c705f0d68073543c58e6dec76 \
  --expected-pins-id 91d8be8f7893aea692e90683c214bbda0d35c4dbe1a652c7cb8908e3d3a4f050 \
  --expected-archive-id d2f4511f180592083945bb993658353218b9efcf91d0dd3f21d02e58399967b9
```

Verification uses process resource limits but no filesystem or network
sandbox. Pre- and post-checks cannot exclude a concurrent process that swaps
and restores bytes between checks.

The service-energy migration inventory compares the pinned historical source
archives with the proposed charging correction. It records direct-source
dependencies and separately identifies current publications outside its
coverage; transitive impacts remain to be evaluated. Run the real-data tests
with `OSR_MIGRATION_REQUIRE_REAL=1 python -m pytest -q --import-mode=importlib
engineering/design_search/tests/test_service_energy_migration_inventory.py`
after fetching the three pinned Git commits listed in the module. A successful
inventory does not replay packets, promote the correction, or qualify hardware.
