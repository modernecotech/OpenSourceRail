# Campaign review and evidence consolidation, 17 October 2026

The [unified campaign review](campaign-review/index.html) brings configuration,
applicability, failed checks, missing inputs and next actions into one workflow.
It covers 63 work packages and 5,364 review records. Records include bounded
candidates, fixed references, resource bounds and sampled stress responses;
they are not 5,364 independent component designs. Filter by architecture, case,
family, evidence packet and screening result; compare at most two records.
Cross-configuration and source-changing proposals carry comparison warnings.
An isolated passing predicate never becomes a complete screening pass.

The factory portability repair now separates the runtime toolchain metadata in
both `development.json` and the nested copy in `report.json`. Retained bytes,
the sealed original producer and all physical/numerical results remain strict.
Only the verifier source binding was renewed; all 48 original artifact hashes
and the recorded producer identity were preserved. The capability directory is
regenerated from current sources and checked by the local `quick` profile.

The `factory-native` profile now also runs a fresh architecture campaign and
verifies exactly the two required selected models: the heaviest retained LM3
proposal and the heaviest six-car planning case. Independent membership and
selection checks precede native model, part, bound, volume, export-hash and
FCStd/STEP reopen checks. Missing models, failed exports and incomplete receipts
fail acceptance and leave diagnostic artifacts available. Old factory-only
receipts cannot satisfy this profile. The
[fresh architecture packet](review-architecture-2026-10-17/index.html) is checked
against current numerical sources when the unified projection is generated;
older packets remain visibly historical. This static applicability label is a
check at generation time, rather than a live source or physics recomputation.

Three historical campaign packets were migrated to a shared immutable,
content-addressed evidence store. Their exact original files, including seals,
can be reconstructed and verified. Repeated JSON subtrees are stored once;
small references and a compact UI projection replace duplicated large reports.
Non-JSON review and CAD assets remain directly usable. The three original
packets occupied 179,243,607 bytes. Their projections plus reachable shared
objects occupy 19,627,052 bytes, an 89.1% reduction before the new current packet.
These are file-byte totals, excluding filesystem block overhead and Git history.
Historical integrity verification passes for all three original packets.

Generate the compact review after publishing an applicable architecture packet:

```sh
.venv/bin/python tools/automation/campaign-review.py \
  --architecture docs/design-engine/review-architecture-2026-10-17
.venv/bin/python tools/automation/migrate-design-evidence.py verify
.venv/bin/python tools/automation/capabilities.py --check
PLAYWRIGHT_BROWSERS_PATH="$HOME/.local/share/opensource-rail/toolchains/playwright" \
  npx playwright test --config playwright.campaign.config.mjs
./osr validate run --profile factory-native
```

The browser matrix checks desktop and narrow mobile layouts from repository and
`docs` web roots, filtered negative results, evidence links, comparison limits
and configuration warnings. Python tests cover portable reproduction,
immutable storage, tampering, mandatory native membership and review semantics.
See the [runner documentation](../../engineering/generative_design/README.md)
for archive reading and maintenance.

Engineering acceptance remains open. The review does not approve a vehicle
configuration, material resistance, connections, dynamics, foundations or a
supplier configuration. The existing manufacturing audit still has 472 missing
or unissued artifacts, 416 planned inspection characteristics without measured
results, and 47 drawing definitions without issued references. Native geometry
checks and software acceptance cannot supply those records. The
[architecture engineering priorities](architecture-feedback-2026-10-17.md)
continue to govern subsequent design development.
