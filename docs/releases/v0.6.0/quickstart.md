# v0.6.0 evaluation quickstart

This guide uses the repository's Linux development path. Native CAD, GIS, FEA,
SUMO and business-system services are optional and are not required for the
Samawah software demonstration. The v0.6.0 release is still withheld until its
software gates and independent review pass.

## Get the evaluation files

```sh
git clone --filter=blob:none --sparse --branch main \
  https://github.com/modernecotech/OpenSourceRail.git
cd OpenSourceRail
git sparse-checkout set --no-cone \
  /tools/automation/prepare-v06-release-checkout.py \
  /docs/design-engine/outline-completion/manifest.json \
  /docs/design-engine/city-atlas/manifest.json \
  /docs/design-engine/coupled-railway/manifest.json \
  /docs/workbench/city-atlas-assets.json
python3 tools/automation/prepare-v06-release-checkout.py
```

The helper expands the clone to the current source, the published city packets,
Samawah's inputs, the browser verifier and exact source paths named by the
publication manifests. It includes about 521 MiB of catalogue files at the
reviewed source epoch, rather than the full 4.6 GiB catalogue tree. It omits
optional native solvers and unrelated research archives. Git fetches the
required blobs on demand.

## Install the small software-demo environment

```sh
python3 -m venv .venv
.venv/bin/python -m pip install pytest scipy==1.16.3
npm ci
npx playwright install chromium
```

The recorded local profile used Python 3.13.16, SciPy 1.16.3, Node 24.21.0,
npm 11.19.0 and Playwright 1.62.1 from the lockfile. Pytest is needed for the
release smoke tests; the Workbench itself only needs the Python numerical
dependency shown above. Install optional native tools separately only when
running their declared methods. See [the broader project setup guide](../../../../tools/README.md).

## Run the browser demonstration

With the project environment and browser dependencies installed, use a new
output directory outside the checkout. The script runs twice as a complete
demonstration, including an identical warm request inside each run:

```sh
node tools/automation/tests/verify-v06-software-journey-a.mjs \
  /tmp/osr-v06-samawah-journey-a-1
node tools/automation/tests/verify-v06-software-journey-a.mjs \
  /tmp/osr-v06-samawah-journey-a-2
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
  required for this release.
- **Candidate research:** open the engineering Workbench, select the named
  passive-wheel development reference, then compare a separately identified
  propulsion research case. Read its assumptions and holds before comparing
  results. A research alternative does not replace the reference.

The Workbench links to source packets and export manifests. An output marked
calculated or replay-verified is digital evidence, not physical acceptance.
