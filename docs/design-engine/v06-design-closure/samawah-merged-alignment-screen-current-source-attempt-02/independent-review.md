# Independent artifact and calculation review

A separate verifier audited this run bundle before this review note was added.
The audited packet ID was
`bc7c5c05cccb41d7ea1c7d1859ae05fca9f4ed854af84250398f0792ecdd30fb`; its 53
manifest-listed files, including the retained nested attempt-01 manifest,
matched the recursive hashes. The request identity, source commit
`440a19d020d957d998a119bb2b8a61d175893ab1`, runner and worker hashes, and all
candidate/evaluation identities were checked. The verifier reran the committed
runner and reproduced the candidate IDs, summary, README and evaluation
artifacts byte-for-byte; run timing and execution metadata naturally differed.

The merged parent is city input `7377b6fc…`, descending from original input
`dd952bf0…`, with station-merge candidate/evaluation `f3e65323…` /
`96759ca6…`. It consolidates the prior 79.977 m line-1 pair. This screen keeps
those resulting 25 station IDs and coordinates fixed. The exact body remains
`75075df9…` / `c6c5efe5…`.

The independently recomputed maximum 5 m-sampled deviations in metres are:

| Tolerance | Line 1 | Line 2 | Line 3 | Line 4 | Line 5 |
|---|---:|---:|---:|---:|---:|
| 25 m | 24.543 | 22.124 | 18.668 | 20.490 | 19.068 |
| 50 m | 46.946 | 45.881 | 18.668 | 49.470 | 36.880 |
| 100 m | 58.701 | 84.401 | 18.668 | 60.034 | 36.880 |

All are within their declared tolerances under the local projection and 5 m
sampling method. This does not establish a continuous surveyed route envelope.
The alternatives have zero 120 m platform-envelope definition failures; the
shortest adjacent stop spacing is 280.386 m.

Each scenario still has four general evaluator holds:

- Exact-body propulsion, braking, thermal, charging and service evidence is absent.
- Exact-body mapped civil and station/terminal assemblies have not been evaluated.
- All fourteen complete cost scopes and whole-life NPV remain unknown.
- The 18-hour service day exceeds the two 8-hour shifts in the current roster assumption.

The point-train route, fleet and runtime values are conditional screens, not a
protected timetable or demonstrated service. Civil classes are proportionally
transferred without site reclassification or civil-load evaluation. Beam, bent,
rail and fastening counts are reference quantity screens, not a complete or
priced civil takeoff. Right-of-way, obstacles, land, crossings, utilities,
ground, access, grades and curves remain unverified; this is a simplification
screen, not a shortest-alignment optimization.

The review was procedural and hash/evaluator based. No OS-level sandbox was
enforced; the repository was writable. The run applied a 60-second CPU limit,
1 GiB address-space limit and 60-second parent timeout, with commit-byte and
before/after integrity checks. No GIS, CAD, FEM, ERPNext or network client was
invoked. This is not external engineering review or physical acceptance.

The current packet manifest was recomputed after adding this note. The
independent check applies to the run artifacts listed in the audited packet ID
above; this review note is a coordinator-authored record of those findings.
