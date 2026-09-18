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

The release evidence manifest identifies the exact commit, source tree,
successful CI runs and asset hashes. The two selected Kani properties are
bounded software checks; they are not independent safety acceptance. Wider
modelling, supplier, manufacturing and physical commissioning work remains in
the [roadmap](ROADMAP.md) and controlled release registers.

## Release procedure

1. Review the intended changes, public API/schema compatibility, upgrade path,
   open audit work and documentation. Keep external acceptance gates explicit.
2. Align `Cargo.toml`, `Cargo.lock`, `VERSION`, package metadata, changelog and
   release notes. Regenerate the reader book, overview, catalogues and evidence
   summaries with `./osr build`, `./osr readiness` and the safety-case summary.
3. Run `./osr test`, the declared pinned Kani harnesses and native integrated acceptance,
   including the complete example-city lifecycle, restart, expansion, business and
   unmocked disposition checks.
   Review generated changes, commit the complete baseline and push it for CI.
4. Require successful `ci`, `kani`, `integrated-stack` and `example-city` workflows
   on that exact commit. The integrated workflow must reach its final outage/recovery
   test. The city run must start on a clean candidate commit and publish its hashed
   `city-evidence.json`; release packaging downloads and validates that run's reports.
5. With a clean tracked working tree, create the immutable annotated tag at the
   verified commit. Never move an existing release tag to repair a failure.
6. Build the publication assets from that tag:

   ```bash
   python3 tools/automation/release-evidence.py --tag v0.4.0 \
     --output build/releases/v0.4.0/publish
   ```

   The builder checks all four workflows, rebuilds the reader PDF with links
   pinned to the tag, embeds the overview images, exports the readiness report
   and release notes, and writes the evidence manifest and `SHA256SUMS`.
   It also downloads all eight `safety-execution-*` artifacts from the successful
   Kani run. Every declared harness must match the commit, runner, dependency
   hashes, result and log; missing, duplicate, failed and changed evidence is
   rejected. `OpenSourceRail-Kani-Evidence-<tag>.zip` retains all original manifests,
   TOML results and logs under their `build/assurance/<package>/` paths. The release
   manifest enumerates all declared harnesses; independent acceptance remains separate.
7. Publish the tag and versioned assets. Verify the uploaded assets against the
   local SHA-256 checksums and preserve the exact commit and workflow evidence.

Safety, hardware, rolling-stock, civil and deployment release remain independent
of this software-publication procedure. A failed or missing software check blocks
publication; an explicitly open physical gate must never be marked complete by
publishing software.

## Published v0.3.1 record

**v0.3.1 was tagged and published on 2026-08-30.** Its scope and claim
boundaries are recorded in the [patch notes](release-v0.3.1.md) and
[v0.3 notes](release-v0.3.md). The tag records that completed software baseline.
