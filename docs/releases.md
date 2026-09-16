# Release Policy And Checklist

OpenSourceRail is pre-1.0 and uses semantic `vMAJOR.MINOR.PATCH` tags.

- `Cargo.toml` carries the full software version.
- `VERSION` carries the release line (`MAJOR.MINOR`) used by generators.
- A tag is immutable. A published release pack becomes a historical record.
- Generated assets must be produced from the tag, checksummed and attached to
  that release.
- Safety approval, hardware release and deployment acceptance are separate
  controlled baselines; a software tag does not imply them.

## Current v0.4 development line

The repository version is now **0.4.0**. The minor-version change recognizes the
addition of the ERPNext business platform, FUXA equipment supervision, the OSR
integration historian/gateway and their shared Workbench lifecycle. The current
scope and its explicit deployment limits are recorded in the
[v0.4 development notes](release-v0.4.md). This is not a published immutable tag;
the checklist below still applies before release publication.

## Published v0.3.1 record

**v0.3.1 was tagged and published on 2026-08-30.** Its scope and claim
boundaries are recorded in the [patch notes](release-v0.3.1.md) and
[v0.3 notes](release-v0.3.md). The tag records the completed release baseline;
this page must not present its pre-tag checklist as unfinished current work.

## v0.4 release checklist

- [x] Select v0.4.0 and define ERP/supervision integration as its intended scope.
- [ ] Review all intended changes and start from a clean working tree.
- [ ] Run CI, Kani, repository health, generated drift and local link checks.
- [ ] Confirm that open gates remain distinct from completed evidence.
- [x] Make `Cargo.toml`, `Cargo.lock`, `VERSION`, changelog and notes agree.
- [ ] Regenerate the root reader PDF, overview, evidence matrix and release
  assets from the intended release commit with `./osr build`.
- [ ] Publish versioned assets with SHA-256 checksums.
- [ ] Create the immutable tag only after the release commit is final.
- [ ] Keep safety, hardware, rolling-stock, civil and deployment limits explicit.

Before tagging, review public API and schema changes, generated catalogue
compatibility and open audit tasks.
