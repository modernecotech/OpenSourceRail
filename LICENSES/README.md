# License Texts And Path Mapping

<!-- osr-system-context:start -->
OpenSourceRail v0.6 develops simple, affordable, locally maintainable station-powered rail. The reference vehicle has six 17 m comfort cars, each with 44 seats and two wheelchair places, no planned standing, and passive steel-wheel bogies on conventional rails carried by concrete. Its passive LIM interface is available for comparison; no installed propulsion architecture or powered length is selected. Acceleration, braking, speed and headway are candidate-specific design variables. The retained 120-second service control gives 8,280 nominal places/hour/direction. The reference vehicle has service batteries and independent brakes, without onboard traction motors, traction batteries or suspension magnets; alternatives must account for their complete system effects. Calculated, priced corridor and city outlines support comparison with explicit assumptions. Engineering verification, prototype validation and manufacturing or operating release remain separate gates.

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
