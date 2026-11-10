# Samawah China bulk purchase vs project make/buy — bounded cost case

This private, source-bound sample revalues one existing five-line Samawah sensitivity under two supply scenarios. It is not a local demand forecast, supplier quotation, or complete/accepted railway design. The physical reference is `756a6887…` / body `9489e4f2…`; the newer compact-drive candidate `75075d…` is not mixed into this result.

## Same-candidate scope

- Candidate: `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3` (body `9489e4f2666fd3b3c73232c86df3f12adf42a5531eb27373834cf3fecb1a3117`).
- City input: `dd952bf0526a58894757dee67031894cece6cd4fc45c074d711a8c76188405de`; route: 57.873 km across five mapped lines.
- Planning sensitivity: line-1 at 1,200 passengers/hour/direction; lines 2–5 at 4,000. This was inherited from the source-bound Samawah five-line sensitivity and is explicitly **not surveyed demand**.
- Service, fleet, physical quantities and alignment are held identical between pricing cases. 72 total trainsets are present in this service scenario.
- Fourteen cost scopes are recalculated. The reference project-make/buy run exactly reproduces the archived longest-line sensitivity CAPEX, NPV, price/km and scope totals before the China case is compared.

## Calculated low/base/high totals (USD)

| Scenario | Installed CAPEX | Whole-life NPV | CAPEX per route-km |
| --- | ---: | ---: | ---: |
| `project-make-buy` | $299,023,190 / $1,092,521,225 / $6,650,586,087 | $579,958,993 / $2,105,695,949 / $12,537,904,914 | $5,166,864 / $18,877,828 / $114,916,410 |
| `china-bulk-buy` | $300,421,703 / $1,097,745,254 / $6,671,657,857 | $582,198,111 / $2,115,143,716 / $12,583,522,471 | $5,191,029 / $18,968,094 / $115,280,512 |

At the base case, China-bulk-buy is **$5,224,029 higher CAPEX** (+0.48%) and **$9,447,767 higher 30-year NPV** (+0.45%) in this modeled case. China-bulk-buy is not a saving in these inputs.

## Base-case delta by cost scope (China bulk minus project make/buy)

| Scope | Delta USD |
| --- | ---: |
| `construction` | $1,354,378 |
| `disposal` | $48,320 |
| `energy` | $0 |
| `factory-tooling` | $-826,656 |
| `fleet` | $268,317 |
| `guideway` | $0 |
| `land-utilities-depot` | $-43,957 |
| `maintenance` | $2,297,068 |
| `operations` | $0 |
| `recovery` | $0 |
| `reliability` | $0 |
| `renewals` | $1,878,350 |
| `rolling-stock` | $4,471,947 |
| `stations-power` | $0 |

## What the prices represent

- The source bundle `engineering/outline/data/china-supply-20261104.json` has dataset ID `42ccba06a2714d229f650fb1a2b6bcb8dc72885133cad8721504422f11b140a1`, 13 repository observations dated 4 November 2026. They include China-origin advertised prices/statistical inputs, not confirmed offers. The model marks these as unconfirmed and unqualified.
- `china-bulk-buy` uses the repository’s China-origin benchmark and calculated finished-stock proxies. The model adds explicit freight, insurance, duty, receiving/QA and local-delivery allowances where applicable. No project-specific supplier contract, Incoterm, container fit, customs quote, or negotiated fleet-volume discount was available to this calculation.
- `project-make-buy` chooses the modeled least-cost make or buy route at this city volume, with local labour/process assumptions and shared plant/tooling charged through the project accounts. Material inputs are still modeled from landed benchmark rates; this is not an Iraqi factory quotation.
- This does not price 266 cities at aggregated purchasing volume. No additional blanket discount was invented. A real multi-city consolidated order may change economics, but it needs matched quantities, logistics, financing, factory capacity and sourced volume tiers.
- The large uncertainty range remains: both project cases are cost-model outputs, not calibrated project estimates. The result only answers which of these two existing assumptions ranks lower for this one sensitivity.

## Evidence and limits

- Reproducible cost evaluator source pins: 58 files; exact input case and city hashes are in `request.json`.
- Reference project make/buy replay matches the prior sealed case exactly; all 14 scope totals are included in `cost-project-make-buy.json` and `cost-china-bulk-buy.json`.
- The service uses the common outline control where not perturbed. Passenger forecast, completed alignment, available propulsion force, independent brake map, grades, local site rates and operating performance remain unverified.
- The comparison changes pricing assumptions only; no selected baseline changed and all engineering, manufacturing, procurement and operating-release flags remain false.
- Execution limits: 120 s CPU, 1 GiB address space, 120 s timeout; measured 2.65 s wall, 273,828 KiB peak RSS. No CAD, FEM, GIS or external transaction ran. Network was not OS-blocked, but no network client was invoked.
- Failed execution attempts 01–03 are retained beside this successful run. They are not used as evidence; the successful run is `04`.

Artifacts: `request.json`, `summary.json`, two full cost records, `execution.json`, `run.py`, `run.sh`, and captured logs. `manifest.json` seals the packet.
