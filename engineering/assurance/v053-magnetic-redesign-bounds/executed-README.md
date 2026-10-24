# Isolated magnetic redesign bounds

This ignored scratch study changes no production source, configuration or canonical packet. Every hypothesis has its own research SHA and retains the failed parent as its provenance. No hypothesis is adopted or physically accepted.

At 8 mm and +120 A the baseline produces 3064.0 N versus its own 4275.4 N weight and 15371.3 N full AW3 allocation.
An optimistic 2.2 T rail-only ceiling is 3476.0 N: current or PM changes cannot make the current 25 mm return section lift its own module while retaining that limit.

For symmetric lift q=sqrt(F*mu0*A_pole), and rail wall t>=q/(stack_fill*x*B_limit). These are necessary, not sufficient bounds. The magnetomotive-force/thermal screens retain the actual nonlinear steel proxy, PM recoil/demag checks, coil fill, 120 A drive limit and 3.75 A/mm2 continuous limit.

| Hypothesis | Module kg | Full AW3 kg/car | Return+wear kg/m | Required A at 40 C | Equilibrium C | Static lift screen | 1.3 AW3 map valid |
|---|---:|---:|---:|---:|---:|---|---|
|baseline|435.97|37618.59|436.51|32168.01|none within40..120C|False|False|
|compact|356.24|35704.99|436.51|50110.93|none within40..120C|False|False|
|high-bias|503.08|39229.17|436.51|23961.94|none within40..120C|False|False|
|light-yoke|392.46|36574.34|436.51|32731.09|none within40..120C|False|False|
|rail-040|435.97|37618.59|693.49|8794.13|none within40..120C|False|False|
|rail-055|435.97|37618.59|963.75|331.07|none within40..120C|False|False|
|rail-065|435.97|37618.59|1151.29|87.65|111.03|False|False|
|rail-080|435.97|37618.59|1443.67|60.52|64.32|True|False|
|longer-stack-125-rail55|523.58|39721.24|963.75|100.60|none within40..120C|False|False|
|longer-stack-150-rail55|611.19|41823.89|963.75|59.73|69.57|True|False|
|pm80-rail55|452.55|38016.38|963.75|344.74|none within40..120C|False|False|
|copper32-rail55|449.82|37950.96|963.75|351.22|none within40..120C|False|False|

A static pass covers symmetric lift and conditional unchanged cooling only. The 1.3 AW3 point is a separate current/BH/demag/domain check, with no reserve-guide circuit, RL/transient/fault or spatial-field qualification.

The return rail wall grows outward at fixed gap faces. The continuous steel mass is counted before brackets; new joints, clearances, rail/civil strength, foundations and erection costs remain unresolved. Larger module stock and actual copper increase vehicle mass before recalculating its lift demand.

The direct symmetric stationarity reduction is checked by the original four-flux Newton evaluator. This is an independent algebraic cross-check of the same network, not an independent FE/spatial validation. Extreme saturated points are inadmissible extrapolations explaining failure, not proposed rated operating points.

Reproduce: OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 tools/automation/osr-python build/magnetic-redesign-bounds/run.py
