# Published v0.6.1 installation verified

The v0.6 handover is complete: repository instructions agree with the published
release, and the installation path from its download succeeded in a fresh
local environment. The immutable v0.6.0 and v0.6.1 tags are unchanged.

On 12 November 2026 the published downloads were fetched and checked against
SHA256SUMS. A new public clone of tag v0.6.1 resolved to
`5cfe89488a64549b37d4a7fd3ea9e3d3a8923aea`. Sparse expansion, a new Python
environment, pinned dependencies, npm installation and a separate Chromium
installation all succeeded. Two documented Samawah journeys completed from
that installed source, covering cold calculation, unchanged warm reuse,
changed-demand calculation, exports and independent result replay. Git status
was empty after both journeys.

The run used Python 3.13.16, Node 24.21.0 and npm 11.19.0 on the existing Linux
host, with fresh venv/npm dependencies and a separate browser cache. It was
not an OS-isolated/container install. Each stage retains exact command/output,
wall time and /usr/bin/time resource logs.

[Machine-readable results and raw-log hashes](installation-verification.json)
bind this run to the published tag and preserve evaluation identities and
measured timings. Raw outputs remain in the external local run directory,
not Git. Follow the [installation guide](quickstart.md) to reproduce.

The retained readiness-browser repair is maintenance alongside v0.7 and does
not change either released tag. Open engineering findings remain visible in
the design-closure ledger.
