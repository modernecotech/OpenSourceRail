# Cities

Current city planning uses the [primary maglev compiler and index](../engineering/ferrite_maglev/city-index.md): `./osr city <slug>` or `./osr catalogue plan --city <slug>`. Each city’s `engineering/maglev/` package recomputes formation, duty, fleet, charging and partial cost allowances. Other city physical/finance packages retain their wheel/rail reference scope.

This domain keeps city inputs and outputs together without confusing them.

| Area | Purpose | Editing rule |
|---|---|---|
| [`workspaces/`](workspaces/README.md) | City Studio projects, GIS/source locks, manual network intent, services and immutable revisions | Edit and review in Git |
| [`catalogue/`](catalogue/README.md) | Generated routes, stations, maps, engineering, finance, simulation and operations evidence | Regenerate; do not hand-edit |

A workspace can produce a catalogue candidate, but a revision hash is not an
engineering or government approval.
