# Next Release Checklist

This is the mutable checklist for the next release. Select the final version
only after reviewing scope and evidence.

- [ ] All intended changes are reviewed and the working tree is clean.
- [ ] CI, Kani, repository health, and generated drift checks pass.
- [ ] Open release gates accurately distinguish completed and externally
  blocked work.
- [ ] `Cargo.toml`, `Cargo.lock`, `VERSION`, changelog, and release notes
  agree on the selected version.
- [ ] Local Markdown links pass.
- [ ] Reader PDF, brochure, evidence matrix, and any binary/image assets
  are generated from the release commit.
- [ ] SHA-256 checksums are generated for attached assets.
- [ ] The tag is created once, after the release commit is final.
- [ ] GitHub release metadata uses `modernecotech/OpenSourceRail`.
- [ ] Known safety, hardware, rolling-stock, civil, and deployment limits
  remain explicit in the published notes.

See [`versioning.md`](versioning.md) for the version policy.
