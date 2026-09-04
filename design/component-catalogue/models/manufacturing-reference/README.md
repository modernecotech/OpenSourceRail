# LM3 neutral manufacturing reference

This folder tracks DXF XY inspection projections, browser-viewable three-view
SVG reference sheets and the controlled hashes for deterministic STEP geometry
for the 62 locally manufactured (`MAKE`) product rows. Generate the local-only
STEP handoffs with `tools/automation/freecad-generate.sh --neutral-exports`;
they are excluded from Git as reproducible, bulky CAD interchange outputs.
DXF and SVG control only design-reference envelopes; they are not sheet-metal
flat patterns, tolerance drawings or NC files.

The complete hashes, fidelity levels and release gates are in
[`index.json`](index.json). Supplier freeze, detailed tolerance drawings,
developed flat patterns, weld maps, calculations and first-article evidence
remain mandatory before manufacture.
