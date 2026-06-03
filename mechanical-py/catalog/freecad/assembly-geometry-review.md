# FreeCAD Assembly Geometry Review

Generated from the build123d STEP catalogue. The checks below use FreeCAD/OCC
`Shape.isValid()`, `Shape.check(True)`, solid counts, volume, and bounding-box
sanity checks on each assembled-state input.

## Chassis + Bogie Assembly

| Item | Valid | OCC check | Solids | Volume mm^3 | Bounding box mm | Issue |
|---|---:|---:|---:|---:|---|---|
| Low-floor chassis | True | False | 41 | 13684494000 | 16440 x 2790 x 755 | OCC compound check reported overlaps/self-intersections: 2424x Error in Face: BOPAlgo SelfIntersect, 1142x Error in Edge: BOPAlgo SelfIntersect, 630x Error in Solid: BOPAlgo SelfIntersect, 140x Error in Vertex: BOPAlgo SelfIntersect |
| Bogie-to-chassis connector package | True | False | 38 | 1472149073 | 14260 x 2440 x 370 | OCC compound check reported overlaps/self-intersections: 258x Error in Solid: BOPAlgo SelfIntersect, 206x Error in Face: BOPAlgo SelfIntersect, 168x Error in Edge: BOPAlgo SelfIntersect, 84x Error in Vertex: BOPAlgo SelfIntersect |
| A-end motor bogie | True | False | 385 | 2152104744 | 3604 x 2644 x 1074 | OCC compound check reported overlaps/self-intersections: 6841x Error in Face: BOPAlgo SelfIntersect, 3249x Error in Edge: BOPAlgo SelfIntersect, 3133x Error in Solid: BOPAlgo SelfIntersect, 783x Error in Vertex: BOPAlgo SelfIntersect |
| B-end trailer bogie | True | False | 339 | 1591914328 | 3604 x 2644 x 1074 | OCC compound check reported overlaps/self-intersections: 5585x Error in Face: BOPAlgo SelfIntersect, 2345x Error in Edge: BOPAlgo SelfIntersect, 1463x Error in Solid: BOPAlgo SelfIntersect, 393x Error in Vertex: BOPAlgo SelfIntersect |
| A-end bogie-to-motor connector | True | False | 22 | 43773013 | 3354 x 817 x 327 | OCC compound check reported overlaps/self-intersections: 95x Error in Face: BOPAlgo SelfIntersect, 41x Error in Edge: BOPAlgo SelfIntersect, 32x Error in Solid: BOPAlgo SelfIntersect, 6x Error in Vertex: BOPAlgo SelfIntersect |

## Full Body Assembly

| Item | Valid | OCC check | Solids | Volume mm^3 | Bounding box mm | Issue |
|---|---:|---:|---:|---:|---|---|
| Body primary structure | True | False | 61 | 154479618286 | 17000 x 3110 x 3630 | OCC compound check reported overlaps/self-intersections: 2505x Error in Solid: BOPAlgo SelfIntersect, 2397x Error in Face: BOPAlgo SelfIntersect, 1932x Error in Edge: BOPAlgo SelfIntersect, 732x Error in Vertex: BOPAlgo SelfIntersect |
| Body exterior layer | True | False | 200 | 4803528316 | 16820 x 2970 x 4396 | OCC compound check reported overlaps/self-intersections: 2790x Error in Face: BOPAlgo SelfIntersect, 2000x Error in Edge: BOPAlgo SelfIntersect, 1178x Error in Solid: BOPAlgo SelfIntersect, 356x Error in Vertex: BOPAlgo SelfIntersect |
| Body interior layer | True | False | 44 | 6095395400 | 16380 x 2770 x 2725 | OCC compound check reported overlaps/self-intersections: 434x Error in Face: BOPAlgo SelfIntersect, 254x Error in Edge: BOPAlgo SelfIntersect, 124x Error in Solid: BOPAlgo SelfIntersect, 52x Error in Vertex: BOPAlgo SelfIntersect |
| Body service layers | True | False | 36 | 3671776000 | 14800 x 2800 x 4005 | OCC compound check reported overlaps/self-intersections: 92x Error in Face: BOPAlgo SelfIntersect, 68x Error in Solid: BOPAlgo SelfIntersect, 56x Error in Edge: BOPAlgo SelfIntersect, 16x Error in Vertex: BOPAlgo SelfIntersect |
| Car systems package | True | False | 283 | 5085045293 | 13740 x 3212 x 3900 | OCC compound check reported overlaps/self-intersections: 3221x Error in Solid: BOPAlgo SelfIntersect, 2843x Error in Face: BOPAlgo SelfIntersect, 2091x Error in Edge: BOPAlgo SelfIntersect, 827x Error in Vertex: BOPAlgo SelfIntersect |
| Mechanical interface package | True | False | 714 | 37356572335 | 18990 x 3076 x 3984 | OCC compound check reported overlaps/self-intersections: 27750x Error in Face: BOPAlgo SelfIntersect, 13776x Error in Edge: BOPAlgo SelfIntersect, 11613x Error in Solid: BOPAlgo SelfIntersect, 2935x Error in Vertex: BOPAlgo SelfIntersect |

## Geometry Issues

- Chassis + Bogie Assembly: Low-floor chassis: OCC compound check reported overlaps/self-intersections: 2424x Error in Face: BOPAlgo SelfIntersect, 1142x Error in Edge: BOPAlgo SelfIntersect, 630x Error in Solid: BOPAlgo SelfIntersect, 140x Error in Vertex: BOPAlgo SelfIntersect
- Chassis + Bogie Assembly: Bogie-to-chassis connector package: OCC compound check reported overlaps/self-intersections: 258x Error in Solid: BOPAlgo SelfIntersect, 206x Error in Face: BOPAlgo SelfIntersect, 168x Error in Edge: BOPAlgo SelfIntersect, 84x Error in Vertex: BOPAlgo SelfIntersect
- Chassis + Bogie Assembly: A-end motor bogie: OCC compound check reported overlaps/self-intersections: 6841x Error in Face: BOPAlgo SelfIntersect, 3249x Error in Edge: BOPAlgo SelfIntersect, 3133x Error in Solid: BOPAlgo SelfIntersect, 783x Error in Vertex: BOPAlgo SelfIntersect
- Chassis + Bogie Assembly: B-end trailer bogie: OCC compound check reported overlaps/self-intersections: 5585x Error in Face: BOPAlgo SelfIntersect, 2345x Error in Edge: BOPAlgo SelfIntersect, 1463x Error in Solid: BOPAlgo SelfIntersect, 393x Error in Vertex: BOPAlgo SelfIntersect
- Chassis + Bogie Assembly: A-end bogie-to-motor connector: OCC compound check reported overlaps/self-intersections: 95x Error in Face: BOPAlgo SelfIntersect, 41x Error in Edge: BOPAlgo SelfIntersect, 32x Error in Solid: BOPAlgo SelfIntersect, 6x Error in Vertex: BOPAlgo SelfIntersect
- Full Body Assembly: Body primary structure: OCC compound check reported overlaps/self-intersections: 2505x Error in Solid: BOPAlgo SelfIntersect, 2397x Error in Face: BOPAlgo SelfIntersect, 1932x Error in Edge: BOPAlgo SelfIntersect, 732x Error in Vertex: BOPAlgo SelfIntersect
- Full Body Assembly: Body exterior layer: OCC compound check reported overlaps/self-intersections: 2790x Error in Face: BOPAlgo SelfIntersect, 2000x Error in Edge: BOPAlgo SelfIntersect, 1178x Error in Solid: BOPAlgo SelfIntersect, 356x Error in Vertex: BOPAlgo SelfIntersect
- Full Body Assembly: Body interior layer: OCC compound check reported overlaps/self-intersections: 434x Error in Face: BOPAlgo SelfIntersect, 254x Error in Edge: BOPAlgo SelfIntersect, 124x Error in Solid: BOPAlgo SelfIntersect, 52x Error in Vertex: BOPAlgo SelfIntersect
- Full Body Assembly: Body service layers: OCC compound check reported overlaps/self-intersections: 92x Error in Face: BOPAlgo SelfIntersect, 68x Error in Solid: BOPAlgo SelfIntersect, 56x Error in Edge: BOPAlgo SelfIntersect, 16x Error in Vertex: BOPAlgo SelfIntersect
- Full Body Assembly: Car systems package: OCC compound check reported overlaps/self-intersections: 3221x Error in Solid: BOPAlgo SelfIntersect, 2843x Error in Face: BOPAlgo SelfIntersect, 2091x Error in Edge: BOPAlgo SelfIntersect, 827x Error in Vertex: BOPAlgo SelfIntersect
- Full Body Assembly: Mechanical interface package: OCC compound check reported overlaps/self-intersections: 27750x Error in Face: BOPAlgo SelfIntersect, 13776x Error in Edge: BOPAlgo SelfIntersect, 11613x Error in Solid: BOPAlgo SelfIntersect, 2935x Error in Vertex: BOPAlgo SelfIntersect

Note: several interface packages are review compounds made from overlapping rectangular solids. `Shape.isValid()` and child-solid validity can still be true while OCC's Boolean-operation checker reports compound self-intersections at welded/contacting envelope overlaps. Treat these as geometry cleanup flags before solid/shell meshing, not as missing STEP imports.
