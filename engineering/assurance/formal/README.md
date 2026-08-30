# Formal Models

The `engineering/assurance/formal/` tree holds machine-checkable specifications that support
the safety case. The current model set is focused on the signalling
consensus layer.

## Contents

| Folder | Purpose |
|---|---|
| [`tla/`](tla/) | TLA+ `SMRaft` model and TLC configurations for the restricted consensus protocol |
| [`consensus-refinement.md`](consensus-refinement.md) | State/action abstraction map, assumptions and the remaining proof obligation |

See [`tla/README.md`](tla/README.md) for model-checking commands and
the connection to `osr-consensus`.
