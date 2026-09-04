# CAD and IFC model coverage

This generated register is the concise fidelity view for the LM3 and station
models. Product maturity, geometry fidelity and release approval are separate
states; no row is a construction release merely because geometry exists.

## Summary

- LM3 product models: 120
- Unique station product models: 45
- Complete station variant assemblies: 7
- Geometry levels: `coordination-envelope`=89, `design-reference-detail`=23, `interface-detailed`=53

## Meaning

`coordination-envelope` controls space and interfaces for sourced equipment;
`manufacturing-envelope` adds OSR manufacturing intent; `design-reference-detail`
adds inspectable subcomponents; `interface-detailed`
models repeatable datums, connections or service routes. `fabrication-detailed`
and `released` require controlled drawings, tolerances and accepted evidence.

The complete machine-readable per-product mapping, analysis IDs, evidence gates
and FreeCAD/IFC/neutral-output paths are in
[`model-coverage.json`](model-coverage.json).
