# Samawah make-or-buy sensitivity: Chinese bulk purchase vs project manufacturing

This packet compares two procurement/manufacturing assumptions for the same five-line Samawah planning sensitivity. It does not change the v0.6 development reference.

- Physical reference candidate: `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`
- Body candidate: `9489e4f2666fd3b3c73232c86df3f12adf42a5531eb27373834cf3fecb1a3117`
- City input: `dd952bf0526a58894757dee67031894cece6cd4fc45c074d711a8c76188405de`
- Route outline: 57.873 km; 72 active plus reserve trainsets.
- Demand scenario: line 1 at 1,200 passengers/hour/direction and lines 2–5 at 4,000. These are planning sensitivities, not surveys.
- Comparison: `project-make-buy` against `china-bulk-buy`, across all fourteen cost scopes.

## Calculated comparison

| China bulk purchase minus project make/buy | Low | Base | High |
| --- | ---: | ---: | ---: |
| Installed capital | +$1.399m | +$5.224m | +$21.072m |
| Whole-life NPV | +$2.239m | +$9.448m | +$45.618m |

Under these declared assumptions, the China-bulk case is more costly. This is not evidence that a real supplier bid will cost more: the Chinese advertised/statistical input rates are provisional Class C values, not project offers. The model includes freight, insurance, duty, receiving/QA and local-delivery allowances; no project-specific negotiated volume discount or binding quotation is present. Project make/buy is also a modeled factory/tooling allocation plus Iraqi material and labour/process assumptions, not a priced factory proposal.

All 58 source pins match source commit `199679166ce9eabe8da108b8034d6030d3487b3e`. Packet manifest ID: `e6b34efd7acf158b4ee3e03274e9eea4f281fb3c6b23e7bd8cf003d3e1d7634e`. Manifest SHA-256: `81230f52c8051c30c27ae6219f48b31031555e3fa910250e08fd81ea5708b080`. The exact cost outputs, service assumptions, source manifest, code snapshots and execution logs are retained alongside this note.

This single Samawah sensitivity does not transfer to Baghdad or the other 264 city studies. The underlying vehicle propulsion, service and site assumptions remain conditional; this does not close the all-city reconciliation gate.
