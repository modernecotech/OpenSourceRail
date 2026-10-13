# Release Policy And Checklist

OpenSourceRail is pre-1.0 and uses semantic `vMAJOR.MINOR.PATCH` tags.

- `Cargo.toml` carries the full software version.
- `VERSION` carries the release line (`MAJOR.MINOR`) used by generators.
- A tag is immutable. A published release pack becomes a historical record.
- Generated assets must be produced from the tag, checksummed and attached to
  that release.
- Safety approval, hardware release and deployment acceptance are separate
  controlled baselines; a software tag does not imply them.

## v0.4.0 software baseline

The [v0.4.0 notes](release-v0.4.md) define the ERPNext, Frappe HR, FUXA,
OSR integration gateway and shared Workbench release scope, review corrections,
upgrade procedure and remaining limits. The
[GitHub release](https://github.com/modernecotech/OpenSourceRail/releases/tag/v0.4.0)
is the authoritative publication record and asset catalogue.

The historical release evidence manifest identifies the exact commit, source tree,
successful CI runs and asset hashes. Its two selected Kani properties are
bounded software checks; they are not independent safety acceptance. Wider
modelling, supplier, manufacturing and physical commissioning work remains in
the [roadmap](ROADMAP.md) and controlled release registers.

## Release procedure

1. Review the intended changes, public API/schema compatibility, upgrade path,
   open audit work and documentation. Keep external acceptance gates explicit.
2. Align `Cargo.toml`, `Cargo.lock`, `VERSION`, package metadata, changelog and
   release notes. Regenerate the reader book, overview, catalogues and evidence
   summaries with `./osr build`, `./osr readiness` and the safety-case summary.
3. Run development checks and regenerate prerequisites. Review generated changes
   and commit the complete baseline. GitHub Actions are disabled; computation runs
   locally according to the [local validation guide](local-validation.md).
4. Require successful local `ci`, `kani`, `integrated-stack` and `example-city`
   profiles on that exact clean commit. Use fresh ignored output directories,
   for example `build/validation/release-ci`, `release-kani`, `release-integrated`
   and `release-city` beneath `build/validation/`. Native acceptance must run on a
   disposable local host; the integrated profile must finish outage/recovery and
   the city profile must finish lifecycle, restart, expansion, business,
   disposition, native engineering change and recovery. City public reports are
   captured before cleanup and their source-bound manifest is validated again
   during packaging. Every declared Kani harness remains required.
5. With a clean tracked working tree, create the immutable annotated tag at the
   verified commit. Never move an existing release tag to repair a failure.
6. Build the publication assets from that tag:

   ```bash
   tools/automation/osr-python tools/automation/release-evidence.py --tag v0.4.0 \
     --local-validation build/validation/release-ci \
     --local-validation build/validation/release-kani \
     --local-validation build/validation/release-integrated \
     --local-validation build/validation/release-city \
     --output build/releases/v0.4.0/publish
   ```

   Use the intended new version in this example; never recreate the published
   `v0.4.0` tag. The builder verifies all four local receipts, rebuilds the reader PDF with links
   pinned to the tag, embeds the overview images, exports the readiness report
   and release notes, and writes the evidence manifest and `SHA256SUMS`.
   It exports all eight local `safety-execution-*` artifact directories from the
   successful Kani run. Every declared harness must match the commit, local runner, dependency
   hashes, result and log; missing, duplicate, failed and changed evidence is
   rejected. `OpenSourceRail-Kani-Evidence-<tag>.zip` retains all original manifests,
   TOML results and logs at their recorded checkout-relative paths. The release
   manifest enumerates all declared harnesses and local command/log hashes;
   independent acceptance remains separate. Raw integration logs remain local.
   `--backend github` is available only to package historical successful run
   evidence; it reads and downloads artifacts without dispatching any workflow.
7. Publish the tag and versioned assets. Verify the uploaded assets against the
   local SHA-256 checksums and preserve the exact commit and execution evidence.

Safety, hardware, rolling-stock, civil and deployment release remain independent
of this software-publication procedure. A failed or missing software check blocks
publication; an explicitly open physical gate must never be marked complete by
publishing software.

## Published v0.3.1 record

**v0.3.1 was tagged and published on 2026-08-30.** Its scope and claim
boundaries are recorded in the [patch notes](release-v0.3.1.md) and
[v0.3 notes](release-v0.3.md). The tag records that completed software baseline.
