# OSR City Projects

This directory contains the small, Git-reviewable source packages used by OSR
City Studio. Generated catalogue outputs remain under designs/.

Every project pins its input design/GIS/scenario bytes, records manual network
intent separately from generator output, defines weekly service plans, and can
materialize content-addressed revision records for pull-request review.
Manual stations and alignment controls live in `network/overrides.toml`; adding
or retiring one therefore remains an ordinary, reviewable Git diff.

Start with the [Samawah project](samawah/project.osr.toml) and the
[City Studio guide](../docs/city-studio/README.md).
