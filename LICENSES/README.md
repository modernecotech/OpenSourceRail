# License Texts And Path Mapping

<!-- osr-system-context:start -->
OpenSourceRail connects locally maintainable railway hardware, design and delivery tools, and train and wayside software. The published v0.7.2 Baghdad opening study includes a service plan, traction assessment and supplier dossier. Current development joins revised route, vehicle, power, civil and purchasing assumptions for v0.8 production preparation; first-article measurements and independent review remain open. The v0.6 passive-wheel vehicle is a separate research selector. Safety and accessibility remain mandatory, and digital results do not grant fabrication or passenger-operation approval.

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
