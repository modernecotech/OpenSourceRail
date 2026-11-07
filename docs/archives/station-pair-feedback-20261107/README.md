# Retained station-pair feedback comparison

Exact source-bound publication at `b5212904e3f6c3af35a901b23d98a368fd2a8666`, before the stateful regenerative
cycle and extended lifecycle accounting. Original nominal/fault results remain
conditional research, with no physical acceptance or operating release.

[Download packet and declared sources](packet-and-declared-sources.tar.gz).
Use a full checkout at the pinned Git commit for independent native replay:

```bash
git worktree add --detach /path/to/prior-source b5212904e3f6c3af35a901b23d98a368fd2a8666
cd /path/to/prior-source
./osr design station-pair verify --replay --state /path/to/private/replay
```

Study `5914dc6d539a5757ec5c4027a52d8aeda9ef7c05496d0e46b424afe89890d1f7`; retention `e248dd7569571a00ac9878f9734b294ad09640cd0676c62dcc33ccc89d075db0`.
[Current cycle comparison](../../design-engine/station-cycle/README.md).
