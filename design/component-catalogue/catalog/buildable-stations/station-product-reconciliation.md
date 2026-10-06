# Station product reconciliation

**Status:** PASS

This generated register proves stable identities in both directions across
the station manifest, BOM, traveler, compact variant definition/drawing
register, native FreeCAD installed/exploded states and IFC4.3 handoff.
It proves configuration consistency, not construction readiness.

| Variant | Products | Assemblies | Definition sheets | Connection controls | States | Result |
|---|---:|---:|---:|---:|---|---|
| `halt` | 26 | 8 | 26 | 8 | installed, exploded | PASS |
| `standard` | 29 | 8 | 29 | 10 | installed, exploded | PASS |
| `major` | 30 | 8 | 30 | 10 | installed, exploded | PASS |
| `interchange` | 30 | 8 | 30 | 10 | installed, exploded | PASS |
| `interchange-elevated` | 35 | 8 | 35 | 10 | installed, exploded | PASS |
| `terminal` | 37 | 9 | 37 | 13 | installed, exploded | PASS |
| `depot-terminal` | 44 | 10 | 44 | 14 | installed, exploded | PASS |

A definition-sheet or connection-control identifier is a required
deployment deliverable keyed to its product row. It is not evidence that
a signed fabrication drawing, supplier data or site approval already exists.
Those gates remain in the open-release register and each assembly traveler.
