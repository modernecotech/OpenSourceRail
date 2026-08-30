# Release Policy And Checklist

OpenSourceRail is pre-1.0 and uses semantic `vMAJOR.MINOR.PATCH` tags.

- `Cargo.toml` carries the full software version.
- `VERSION` carries the release line (`MAJOR.MINOR`) used by generators.
- A tag is immutable. A published release pack becomes a historical record.
- Generated assets must be produced from the tag, checksummed and attached to
  that release.
- Safety approval, hardware release and deployment acceptance are separate
  controlled baselines; a software tag does not imply them.

## v0.3 release candidate

The selected next version is **v0.3.0**. Scope and claim boundaries are in the
[v0.3 notes](release-v0.3.md). Do not create the tag until every item below is
complete on the intended release commit.

- [ ] All intended changes are reviewed and the working tree is clean.
- [ ] CI, Kani, repository health and generated drift checks pass.
- [ ] Open gates distinguish completed work from external evidence gaps.
- [ ] `Cargo.toml`, `Cargo.lock`, `VERSION`, changelog and notes agree.
- [ ] Local Markdown links pass.
- [ ] Root reader PDF, public overview, evidence matrix and release assets are
  regenerated from the release commit with `./osr build`.
- [ ] Attached assets have SHA-256 checksums.
- [ ] The immutable tag is created only after the release commit is final.
- [ ] GitHub release metadata uses `modernecotech/OpenSourceRail`.
- [ ] Safety, hardware, rolling-stock, civil and deployment limits remain
  explicit in the published notes.

Before tagging, review public API and schema changes, generated catalogue
compatibility and open audit tasks.
