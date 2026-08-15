# License Texts And Path Mapping

This directory contains the complete license texts used by
OpenSourceRail:

- [`Apache-2.0.txt`](Apache-2.0.txt)
- [`CERN-OHL-S-2.0.txt`](CERN-OHL-S-2.0.txt)
- [`CC-BY-SA-4.0.txt`](CC-BY-SA-4.0.txt)

## Default Path Mapping

| Paths/material | SPDX identifier |
|---|---|
| `crates/`, `design-py/src/`, `mechanical-py/src/`, `scripts/`, `tools/`, tests, and executable portal code | `Apache-2.0` |
| `hardware/`, `mechanical-py/catalog/`, generated CAD, fabrication definitions, travelers, and hardware/mechanical drawings | `CERN-OHL-S-2.0` |
| `docs/`, repository Markdown, original diagrams, and original documentation media | `CC-BY-SA-4.0` |
| `formal/` model source | `Apache-2.0` |

Generated files follow the license of the source material unless their
manifest or embedded notice states otherwise. Third-party data, maps,
supplier documents, fonts, and cited material are not relicensed by this
mapping. OpenStreetMap-derived artifacts require OpenStreetMap
attribution and remain subject to the Open Database License where it
applies.

Contributors license changes under the license applicable to the path
they modify. New mixed-purpose directories must include a local license
notice before accepting substantive content.
