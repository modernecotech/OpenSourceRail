# Retained source epoch for service-energy migration

This record preserves the original source bytes used by 15 independently
pinned publications affected by a proposed service-battery charging correction.
The archive contains 413 source files. The original manifest identities were
independently taken from Git revision `dad8c4bedb2361d3e621e9def312273167279027`.
The metadata also inventories the original packet files and records any files
not declared in their original manifests.

```bash
python -m engineering.design_search.retained_source_epoch verify \
  --root . \
  --archive-directory docs/design-engine/retained-battery-source-epoch/archive \
  --pins docs/design-engine/retained-battery-source-epoch/pins.json \
  --expected-archive-id 478479a93642c464cc2be318bbc5b45b9c5c3fec2e9cecb02318d53bd4fb568e
```

Verification requires the exact original packet trees at the supplied root;
the source archive does not duplicate those packet payloads. A full Git checkout
can reconstruct them into a fresh private directory (about 483 MiB):

```bash
git fetch --no-tags --depth=1 origin dad8c4bedb2361d3e621e9def312273167279027
retained_parent=$(mktemp -d)
python -m engineering.design_search.retained_packet_materialize \
  --git-repo . --output "$retained_parent/packets" \
  --archive-directory docs/design-engine/retained-battery-source-epoch/archive \
  --pins docs/design-engine/retained-battery-source-epoch/pins.json \
  --expected-commit dad8c4bedb2361d3e621e9def312273167279027 \
  --expected-archive-id 478479a93642c464cc2be318bbc5b45b9c5c3fec2e9cecb02318d53bd4fb568e
```

The command authenticates the Git blobs and checks the reconstructed packet
trees against the retained archive. To independently recheck them later, use
the verification command above with `--root "$retained_parent/packets/root"`.
The materializer does not fetch missing Git objects itself. A process memory
limit is needed for a strict bound on buffered Git tree listings.

The catalog covers these
15 packets only: other source-bound records, including the conditional journey,
reference-cell, digital-twin and engineering-closure packages, require their
own migration. The retained bytes do not rerun numerical solvers, grant current
evaluator admission, establish physical equivalence, or release any design.

The archive and packet inventories were checked in separate processes with
resource limits. No filesystem or network sandbox was enforced, and integrity
checks do not exclude a concurrent process that swaps and restores bytes.
