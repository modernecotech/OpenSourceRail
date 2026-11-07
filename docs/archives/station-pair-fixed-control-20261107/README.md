# Retained fixed-brake station-pair comparison

The first station-pair experiment is retained at Git commit `8ed8bf7fa69d8fb76b0f8d370596a7d4765e10d7` with its
original source-bound publication and declared source files. It uses an offline
fitted nominal brake point and replays faults without fitting each fault result.
Its berth misses, downhill overruns and hill-start limitations remain evidence.

This is historical conditional research, with no physical or operating acceptance.
The [current comparison](../../design-engine/station-pair/README.md) explores a
separate feedback-control evaluation without changing the physical reference.

[Download exact packet and declared sources](packet-and-declared-sources.tar.gz).
The archive is for inspection; use the complete pinned Git checkout for replay:

```bash
git worktree add --detach /path/to/fixed-control-source 8ed8bf7fa69d8fb76b0f8d370596a7d4765e10d7
cd /path/to/fixed-control-source
./osr design station-pair verify --replay --state /path/to/private/replay
```

No current source is substituted into this historical evaluation. Retention ID
`65cb8ee9822cd12544eb12183b294e352bce1490f5f90e7b1c742e1423d99747`; study `cc1ba1bf47f188657d334e7f14ed0adb1ebc8da9176f4880b2b276aa7a8f9061`.
