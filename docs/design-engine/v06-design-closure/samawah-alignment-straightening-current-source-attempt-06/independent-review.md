# Independent artifact and calculation review

A separate verifier audited this exact attempt-06 bundle. It confirmed all 42
listed files against the recursive manifest; packet and request identities;
source commit, runner and worker binding; and the three derived city input,
physical candidate and evaluation identities. All complete cost scopes remain
null. The guideway quantities match the scenario evaluations and README:

| Screen | 20 m beams | Shared bents | Running rail (m) | Fastening sets |
|---|---:|---:|---:|---:|
| Current map | 5,794 | 2,902 | 231,493.0 | 385,825 |
| 25 m | 5,458 | 2,734 | 218,073.2 | 363,458 |
| 50 m | 5,426 | 2,718 | 216,810.7 | 361,353 |
| 100 m | 5,406 | 2,708 | 215,970.2 | 359,952 |

The attempt-06 run is bound to source commit
`f2650d93fa2d1d5a9b06165756c2d6fadeae7705`; this is the source commit recorded
in the execution packet and is the commit containing the runner/worker hashes.
It is newer than attempt 05's `1aaacf5…` source. The attempt-05 verifier result
is historical context and is not used as a substitute for this attempt-06
review.

The verifier confirmed all three alternatives still retain one 120 m
platform-envelope failure at the 56.552 m close-stop gap. These guideway values
are reference quantity screens, not complete civil takeoffs; they do not price
foundations, joints, reinforcement, bearings, stations or construction.
All alternatives remain unselected. Full site, access, demand, curvature/grade,
force/braking, civil, cost and accessibility checks remain open.

## Isolation and physical evidence limits

The verifier was instructed to work read-only, but agents shared the repository
environment. No OS-level read-only sandbox was enforced. The check was based on
hashes and evaluator reproduction, not external engineering review. No GIS,
CAD, FEM, ERPNext, network client, survey or physical equipment was used.
