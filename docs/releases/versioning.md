# Versioning And Release Policy

OpenSourceRail is pre-1.0 and uses semantic `vMAJOR.MINOR.PATCH` tags.

- `Cargo.toml` carries the full software version.
- `VERSION` carries the release line (`MAJOR.MINOR`) used by generators.
- A tag is immutable. A published release pack becomes a historical
  record and must not instruct maintainers to recreate its tag.
- Post-tag work belongs to `docs/releases/next.md` until a release
  version is selected.
- Generated release assets must be produced from the tag, checksummed,
  and attached to that release.
- Safety approval, hardware release, and deployment acceptance versions
  are separate controlled baselines and must not be inferred from a
  software tag.

Before selecting the next version, review public API/schema changes,
generated catalogue compatibility, and the open audit tasks.
