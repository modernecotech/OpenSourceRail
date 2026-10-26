# License Texts And Path Mapping

<!-- osr-system-context:start -->
OpenSourceRail develops simple, affordable, locally maintainable urban transport. The development default is six 17 m comfort cars, each with 44 seats plus two wheelchair places and no planned standing; the 120-second service target gives 8,280 normal passengers/hour/direction. All permanent magnets and suspension controls remain onboard; concrete beams carry passive steel facings, while station windings provide launch and receiving power. Lightweight assemblies, repeated civil works and repairable local production support the low-cost ethos. Stable physical operation and manufacturing release remain open.

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
