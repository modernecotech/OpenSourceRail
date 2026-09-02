# Station product reconciliation

**Status:** PASS

This generated register proves stable identities in both directions across
the station manifest, BOM, traveler, compact variant definition/drawing
register, native FreeCAD installed/exploded states and IFC4.3 handoff.
It proves configuration consistency, not construction readiness.

| Variant | Products | Assemblies | Definition sheets | Connection controls | States | Result |
|---|---:|---:|---:|---:|---|---|
| `halt` | 25 | 8 | 25 | 8 | installed, exploded | PASS |
| `standard` | 28 | 8 | 28 | 10 | installed, exploded | PASS |
| `major` | 29 | 8 | 29 | 10 | installed, exploded | PASS |
| `interchange` | 29 | 8 | 29 | 10 | installed, exploded | PASS |
| `interchange-elevated` | 30 | 8 | 30 | 10 | installed, exploded | PASS |
| `terminal` | 36 | 9 | 36 | 13 | installed, exploded | PASS |
| `depot-terminal` | 43 | 10 | 43 | 14 | installed, exploded | PASS |

A definition-sheet or connection-control identifier is a required
deployment deliverable keyed to its product row. It is not evidence that
a signed fabrication drawing, supplier data or site approval already exists.
Those gates remain in the open-release register and each assembly traveler.
