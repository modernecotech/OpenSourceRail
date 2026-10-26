# License Texts And Path Mapping

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. Six 17 m comfort cars carry 44 seats plus two wheelchair places/car and no planned standing; the 120-second target gives 8,280 passengers/hour/direction. Passive steel-wheel bogies run on conventional rails carried by precast concrete. Station LIMs act on passive onboard secondaries; there are no traction motors, traction batteries or suspension magnets onboard. Service batteries, independent brakes and the existing station-led GoA4 architecture remain. The reference design is research only; city numerical regeneration, economics and physical release remain open. Maglev documents below are retained historical research, not the selected v0.6 physical design.

[Project introduction](../README.md) · [Engineering approach and current status](../docs/design-engine/current/README.md)
<!-- osr-system-context:end -->

This directory contains the complete license texts used by
OpenSourceRail:

- [`Apache-2.0.txt`](Apache-2.0.txt)
- [`CERN-OHL-S-2.0.txt`](CERN-OHL-S-2.0.txt)
- [`CC-BY-SA-4.0.txt`](CC-BY-SA-4.0.txt)

## Default Path Mapping

| Paths/material | SPDX identifier |
|---|---|
| `crates/`, Python implementations in `engineering/`, `tools/`, tests, and executable portal code | `Apache-2.0` |
| Hardware specifications, generated CAD, fabrication definitions, travelers, and electrical/mechanical drawings | `CERN-OHL-S-2.0` |
| `docs/`, repository Markdown, original diagrams, and original documentation media | `CC-BY-SA-4.0` |
| Executable formal model source | `Apache-2.0` |

Generated files follow the license of the source material unless their
manifest or embedded notice states otherwise. Third-party data, maps,
supplier documents, fonts, and cited material are not relicensed by this
mapping. OpenStreetMap-derived artifacts require OpenStreetMap
attribution and remain subject to the Open Database License where it
applies.

Contributors license changes under the license applicable to the path
they modify. New mixed-purpose directories must include a local license
notice before accepting substantive content.
