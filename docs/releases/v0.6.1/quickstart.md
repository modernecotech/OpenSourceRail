# Install and run the published v0.6.1 release

[v0.6.1 is published](https://github.com/modernecotech/OpenSourceRail/releases/tag/v0.6.1).
The authoritative release installation asset is
[INSTALL-v0.6.1.md](https://github.com/modernecotech/OpenSourceRail/releases/download/v0.6.1/INSTALL-v0.6.1.md).
Use the attached SHA256SUMS to verify downloads before installation. This guide
uses the same Linux route. Native CAD, GIS, FEA, SUMO and business-system
services are optional for the Samawah software demonstration.

## Get the tagged software

```sh
git clone --filter=blob:none --sparse --branch v0.6.1 \
  https://github.com/modernecotech/OpenSourceRail.git
cd OpenSourceRail
test "$(git rev-parse HEAD)" = 5cfe89488a64549b37d4a7fd3ea9e3d3a8923aea
test "$(git rev-parse 'HEAD^{tree}')" = 58ba4411d502a166b3a14000bc1e09b733b65cbd
git sparse-checkout set --no-cone \
  /.github/release-smoke-tests.txt \
  /tools/automation/prepare-v06-release-checkout.py \
  /docs/design-engine/outline-completion/manifest.json \
  /docs/design-engine/city-atlas/manifest.json \
  /docs/design-engine/coupled-railway/manifest.json \
  /docs/workbench/city-atlas-assets.json \
  /docs/design-engine/v06-design-closure/compact-drive-source-replay-01/compact-737-h100/body.json.gz
python3 tools/automation/prepare-v06-release-checkout.py
```

The helper expands the clone to the selected release sources, the outline and
city-atlas inputs, Samawah's data, the browser verifier and the source paths
needed by the pinned Baghdad and candidate examples. It omits the unrelated
source paths in the held global current-dossier manifest, optional native
solvers and unrelated research archives. Git fetches required blobs on demand;
the helper reports the allocated checkout size and remaining free disk.

The global current dossier remains explicitly held at this reviewed source
epoch. The Workbench reports that hold and does not use its stale global costs
or portfolios. It is excluded from supported v0.6 results and release evidence
until its exact source provenance is resolved. The Samawah calculation has a
separate source and evaluation identity and does not require a full 266-city
publication refresh.

## Install the small software-demo environment

```sh
python3 -m venv .venv
.venv/bin/python -m pip install pytest==9.2.0 scipy==1.16.3
npm ci
npx playwright install chromium
```

The recorded local profile used Python 3.13.16, SciPy 1.16.3, Node 24.21.0,
npm 11.19.0 and Playwright 1.62.1 from the lockfile. Pytest is needed for the
release smoke tests; the Workbench itself only needs the Python numerical
dependency shown above. Install optional native tools separately only when
running their declared methods. See [the broader project setup guide](../../../tools/README.md).

## Run the browser demonstration

With the project environment and browser dependencies installed, use a new
output directory outside the checkout. Run the script twice as a complete
demonstration, including an identical warm request inside each run:

```sh
run_root="$(mktemp -d /tmp/osr-v061-demo.XXXXXX)"
node tools/automation/tests/verify-v06-software-journey-a.mjs \
  "$run_root/journey-a-1"
node tools/automation/tests/verify-v06-software-journey-a.mjs \
  "$run_root/journey-a-2"
```

Each run starts a loopback Workbench, calculates the default Samawah case,
repeats the same request to check cache reuse, changes peak demand, and verifies
that the changed request gets a distinct identity. It writes the report and
exports to the supplied directory. It runs no native solver. It requires at
least 4 GiB free at job admission and caps each output package at 64 MiB.

Inspect each report's source commit, input and evaluation IDs, 14 cost scopes,
resource measurements, cache result and independent replay before using the
example in another study. Compare cold and warm wall time, CPU time, peak RSS,
cache-store bytes and filesystem free space between runs. The script
demonstrates software behavior; it does not validate route survey, physical
railway design or cost quotations.

## Open the precomputed examples

- **Baghdad:** open the city atlas, select Baghdad and inspect the published
  route/service comparison and its source/evaluation identities. Treat it as a
  read-only, precomputed planning example; no new Baghdad calculation is
  required for this release. The source-bound result download is available;
  native RustGIS project export is held by a publication-epoch mismatch.
- **Candidate research:** the Workbench shows the selected passive-wheel
  development reference, but its portfolio selector is held at this source
  commit by a stale current-dossier source binding. Inspect the precomputed
  [coupled-railway packet](../../design-engine/coupled-railway/README.md) for
  separate candidate IDs and read its limits. This packet is verified in its
  recorded historical source epoch; the current railway verifier holds when
  that epoch no longer matches. Run
  `python -m engineering.station_rail.retired_station_reference verify` to
  check the retained source-pinned packet set. This check reads original Git
  blobs from the historical source epoch, which the sparse evaluation checkout
  does not fetch. Run it from a clean full-history checkout of the same commit.
  This separate historical byte check does not replay the campaign or admit old
  results as current evaluations or physical evidence. A research alternative
  does not replace the reference.

The Workbench links to source packets and export manifests. An output marked
calculated or replay-verified is digital evidence, not physical acceptance.
