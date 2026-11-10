# Independent review — attempt 03

Attempt 03 passed the independent packet and replay audit.

- The root packet contains 81 listed files; every recorded file hash and the packet identity recompute correctly. The two nested historical packets also verify: attempt 02 contains 53 files and attempt 01 contains 25. Parent manifests and hashes match.
- Source commit `f03fb6a2d641398359bf40de26fb3405170f38bd`, the runner and worker hashes, request identity, and all 60 consumed source records match the committed source and worktree.
- Station-merge ancestry, the original and merged city inputs, body identity, and all scenario city/candidate/evaluation identities agree. The 25 post-merge station IDs and coordinates remain fixed.
- Independently recomputed 5 m sampled deviations stay within the declared 25 m, 50 m and 100 m tolerances. All three scenarios have zero 120 m platform-envelope definition failures; the closest adjacent stops are 280.386 m apart. Each retains four non-platform evaluator holds.
- README route, fleet, runtime and guideway quantities match the summary. All fourteen cost scopes remain unknown. Existing civil classes were transferred proportionally; this packet does not remap site crossings or evaluate civil loads.
- The runner was replayed with `PYTHONDONTWRITEBYTECODE=1 python3 -B docs/design-engine/v06-design-closure/samawah-merged-alignment-runner-01/run.py --output-dir /tmp/osr-verify-samawah-merged-alignment-attempt-03`. It returned 0; summary, README and scenario outputs matched byte-for-byte.

This is an unselected sampled planning geometry, not a surveyed or buildable alignment. It does not establish right-of-way, access, catchment, utilities, geotechnical suitability, continuous curvature/grade feasibility, propulsion, braking, a protected timetable, civil design, complete costs, accessibility or physical acceptance. No GIS, CAD, FEM, ERPNext or supplier lookup ran.

No OS-level read-only sandbox was enforced; the source tree was writable. The bounded replay used 60-second CPU and wall limits, a 1 GiB address-space limit, commit-byte checks and before/after integrity checks. No network client was invoked.
