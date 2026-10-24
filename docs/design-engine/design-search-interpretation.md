# First carrier and guidebeam campaign: engineering interpretation

OpenSourceRail aims for simple fixed lines, affordable construction and repair,
local production and high normal passenger throughput. This campaign tests
whether carrier and beam changes help one consistent physical configuration.
It retains added material, unresolved mechanisms and failures alongside useful
improvements. The six-car Baghdad context remains explicit.

The [comparison Workbench](design-search/index.html),
[source and payload receipt](design-search/manifest.json) and
[complete results](design-search/comparison.json.gz) identify the exact campaign,
evaluations and declared selection policy. The five physical candidates comprise
three initial families and two bounded revisions. Twenty-five primary
calculations and five arithmetic/source confirmations support the comparison.
The confirmations concern the retained baseline's five evaluators; they do not
independently confirm magnetic, thermal, structural or operating physics.

## What changed

Masses below are known AW3 stock subtotals per car, including retained unlocated
allocations. Bearings, slides, retention and complete installed mass distribution
remain unresolved. Mechanical utilisation is governed by the retained **M8
collector splice**, with a screen limit of 1. The lift comparison uses a uniform
**1.3 AW3 allocation per module** against the **+120 A sampled calculation**;
that sample is not an established continuous thermal rating.

| Physical ID prefix | Carrier and beam | Counted wall | AW3 subtotal t/car | Mechanical utilisation | Live beam deflection mm / limit ratio | Required / sampled lift kN |
|---|---|---:|---:|---:|---:|---:|
| `ed05b47c` | Retained rigid; deep 25 m | No added carrier walls | 37.619 | 14.251 | 8.255 / 0.660 | 19.983 / 3.064 |
| `65987a41` | Four yaw groups; shallow 25 m | 6 mm | 38.406 | 14.549 | 19.083 / 1.527 | 20.401 / 3.064 |
| `a5977148` | Four yaw groups; deep 25 m, revised from `65987a41` | 6 mm | 38.406 | 14.549 | 8.428 / 0.674 | 20.401 / 3.064 |
| `d5bdd99a` | Five yaw/slide groups; wider 20 m | 6 mm | 38.497 | 14.631 | 4.374 / 0.437 | 20.449 / 3.064 |
| `30152e6e` | Five yaw/slide groups; wider 20 m, revised from `d5bdd99a` | 8 mm | 38.765 | 14.747 | 4.405 / 0.440 | 20.592 / 3.064 |

Deepening the shallow beam reduces calculated live deflection **55.84%** at
unchanged vehicle subtotal. It adds **6.642 tonnes per span**, or **2.655 m³ of
concrete**. Passing that deflection comparison does not close the remaining
civil, handling, installation and site requirements.

Increasing carrier walls from 6 to 8 mm adds **267.880 kg per car**. It leaves
the governing M8 splice unchanged and increases its demand. Beam deflection and
required lift also rise. This is a retained rejected revision, and gives a clear
reason to target the actual connection before adding more generic carrier steel.

Five yaw/slide groups reduce calculated 150 m curve mismatch to **3.586 mm**
within the studied 4 mm geometric allowance, but require approximately **2.907 m
of stock width**, exceeding the inherited 2.65 m envelope. Bearings and slides
still lack complete installed detail and mass. This is a necessary geometry
result, not an accepted curved installation.

The wider 20 m span has lower gross piece mass than the deep 25 m span:
approximately **54.951 versus 61.893 tonnes**. Its mass per route metre is higher,
approximately **2.748 versus 2.476 tonnes/metre**, and it needs approximately
25% more spans/support positions on the same route. Foundations, transport,
lifting, maintenance and unquoted work prevent a complete cost-saving claim.

## Selection and next design tasks

**No candidate qualifies as an integrated baseline.** Magnetic and mechanical
screens fail for every alternative, while installed inventory and coupled
thermal/deformation/gap calculations remain incomplete. The declared policy
selects the retained rigid/deep-beam family as the next experiment, preserving a
common reference with fewer added mechanisms and lower counted vehicle mass.
It does not select a train for construction or operation.

The next bounded work should:

1. Investigate the governing collector splice with actual revised connection
   stock, fasteners, load paths, installation access and removal geometry.
   Recount its mass and rerun the same load cases before adjusting carrier walls.
2. Independently model the common magnetic module and actual return rails on
   identical geometry, comparing force and flux allocation hypotheses. The
   sampled 3.064 kN lift is below the module's approximately 4.275 kN weight and
   far below required support. Speed or dwell changes cannot resolve that static
   deficit.
3. Prepare the existing
   [qualification programme](ferrite-maglev/qualification/README.md)'s restrained
   magnetic-module force/flux procedure with measured gaps, both circuit currents,
   voltage, flux, temperature, resistance and inductance. Physical fixture and
   test limits remain subject to that programme; no test was performed here.
4. Resolve complete joints, retention, protection, cooling and installed mass
   distribution, then connect thermal/deformation maps to the coupled evaluator.
5. Recompute equal-service operations and whole-route quantities for survivors.
   The primary six-car case retains 120 normal passengers/car and 14,400
   passengers/hour/direction at 180-second headway. Any changed formation, speed,
   station spacing or dwell must carry platform, charging, fleet, evacuation and
   civil consequences in a separate versioned specification.

The [research twin](design-search-twins/ed05b47c9216df1819f745bef9597812a9d1ef009501cc399ae1da78904b5798/README.md)
compiles the selected known-stock component scope. Native geometry and business
records retain the same physical candidate identity and the failed engineering
evidence. They do not replace the missing installed design or physical evidence.
