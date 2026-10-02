# Synthetic drainage scenarios

These small models adapt the repository's [SWMM installation benchmark](../../../analysis/benchmarks/swmm/simple-runoff.inp) for the [civil demonstration](../README.md). They retain the synthetic 1 ha catchment and storm and use dynamic-wave routing at a one-second routing step.

- `normal.inp`: 0.5 m circular conduit and free outlet.
- `blocked-drain.inp`: 0.1 m effective conduit diameter as a blockage sensitivity.
- `backwater.inp`: fixed 1.5 m outlet stage.

The reduced diameter is an illustrative sensitivity, not a calibrated debris model. Rainfall, catchment geometry, flood levels, culvert/outfall design, blockage and scour assumptions need site-specific review. [Recorded statistics](../calculations/drainage-sanity.json) show hydraulic failures despite acceptable continuity.
