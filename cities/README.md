# Cities

This domain keeps city inputs and outputs together without confusing them.

| Area | Purpose | Editing rule |
|---|---|---|
| [`workspaces/`](workspaces/README.md) | City Studio projects, GIS/source locks, manual network intent, services and immutable revisions | Edit and review in Git |
| [`catalogue/`](catalogue/README.md) | Generated routes, stations, maps, engineering, finance, simulation and operations evidence | Regenerate; do not hand-edit |

A workspace can produce a catalogue candidate, but a revision hash is not an
engineering or government approval.
