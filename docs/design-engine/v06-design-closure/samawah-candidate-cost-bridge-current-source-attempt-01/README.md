# Samawah detailed-candidate cost bridge

This packet prices selected, physically matched quantity fragments for the exact package-07 detailed body and five-line Samawah planning case. It is **not** a complete city CAPEX or whole-life estimate.

## Candidate identity

- City candidate/evaluation: `9f37c5d864a34b56009030b07659abe0cc92d5dc97c5c1872384cc7b93a6b176` / `eaa84ee07efbff5763ec11e490142f88d2701c1196d09c63b7bfc9b18ce61a16`
- Body candidate/evaluation: `75075df9247dfff7082a78eadc273d3a99f37e5486450621536c43b1bfa2f797` / `c6c5efe577bd302c507756af53238a8f162c6e2cbeaefd2aa11fecd343b93fb3`
- Authenticated city input: `dd952bf0526a58894757dee67031894cece6cd4fc45c074d711a8c76188405de`; route quantity: 57.873 km.
- Ratebook packet: `e6b34efd7acf158b4ee3e03274e9eea4f281fb3c6b23e7bd8cf003d3e1d7634e`; ratebook candidate/body: `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3` / `9489e4f2666fd3b3c73232c86df3f12adf42a5531eb27373834cf3fecb1a3117`.
- The ratebook candidate is a different historical physical design. Its geometry, body, quantities, fleet, service, totals and NPV were not copied into this candidate. Only the named Class-C unit-cost ratios below were carried as explicit rate assumptions.

## Candidate-linked fragments (USD, low / base / high)

| Item | Candidate quantity | Rate basis | Cost fragment |
| --- | ---: | --- | ---: |
| `route-running-rails` | 13,938,193.416 kg | Historical Class-C rate from f44f93e8 | $10,035,321 / $14,600,083 / $22,159,637 |
| `route-complete-fasteners` | 385,825.000 sets | Historical Class-C rate from f89eb25a | $6,779,050 / $10,355,663 / $19,235,846 |
| `repeat-box-beams` | 5,794.000 spans | Historical Class-C rate from 7cc90d97 | $20,092,155 / $42,636,354 / $164,561,156 |
| `bearing-pads` | 5,794.000 spans | Historical Class-C rate from 1f6e24d1 | $2,877,815 / $11,511,258 / $67,149,007 |
| `beam-joints-drains-lifting` | 5,794.000 spans | Historical Class-C rate from df3c194e | $1,438,907 / $5,755,629 / $33,574,503 |
| Candidate counted BOM and process subtotal | 42 / 59 / 88 low/base/high trainsets | Candidate body’s own counted parts/process ledger | $29,152,279 / $88,678,591 / $297,135,615 |
| **Partial priced-fragment sum** | | The items above only | **$70,375,527 / $173,537,578 / $603,815,763** |

The partial sum covers the detailed body’s counted BOM/process subtotal plus five matched rail, fastening, repeat-beam, bearing-pad and joint/drain/lifting fragments. It is not an installed price. Construction haul, crane and erection cost is not transferred because the historical unit line mixes in station track absent from this candidate quantity set. The source beam’s load basis has not been checked against this candidate, and the beam quantity remains a reference geometry request pending a detailed civil load evaluation.

## Chinese supply and mass-purchase treatment

Rail mass uses the retained 60E1 profile coefficient of 60.21 kg/m from `engineering/outline/city_civil.py`. The retained Samawah make/buy and China-bulk cost packets have identical low/base/high rates for these five infrastructure rows. The current detailed body’s own BOM is not re-priced from the older vehicle’s China scenario. No China supplier quotation, project volume tier, negotiated discount, import contract or local market validation is available in this candidate packet, so no additional mass-purchase discount is assumed.

## Explicitly unpriced

- Exact-body force/braking, grade, detailed civil loads and station geometry.
- Support, foundation, ground, land, utilities, depot, station access, power, charging and protection quantities.
- Local wage/material rates, import duties/customs, tax treatment, exchange rate and current supplier quotations.
- Production tooling/factory scale, final assembly, test/commissioning, staffing and construction programme.
- Traction energy, operations, maintenance, renewals, recovery, reliability, disposal and financing inputs.
- Potential mismatch between historical 20 m beam design and current body loads; the rate does not validate the beam selection.
- Construction haul/crane/erection rates are not transferred because the retained line mixes mainline and station track quantities absent from this candidate quantity set.
- China-bulk source comparison for these matched infrastructure rows is identical to project make/buy; the current body BOM has no candidate-matched China reprice.
- The remaining cost scopes (construction/erection, stations/power, foundations/site, factory and tooling, land/utilities/depot, traction energy, operations, maintenance, renewals, recovery, reliability, disposal, finance/tax and full delivery) do not have candidate-matched scope totals.
- `installed_capex_usd` and `whole_life_npv_usd` therefore remain null. `cost_complete`, `service_complete` and every physical/release flag remain false.

## Reproduction and integrity

Run from the repository root:

```sh
tools/automation/osr-python docs/design-engine/v06-design-closure/samawah-candidate-cost-bridge/run.py --output-dir /tmp/osr-samawah-cost-bridge-replay
```

Execution ID: `41f86f727a9095e919f68e678634a3ddf0563b4e87b2d7a83411434c6cd4a149`. Packet integrity ID is in `manifest.json`. The run used the repository Python process; it did not invoke CAD, FEM, GIS, ERPNext, a network client or a supplier lookup. No OS sandbox or process resource limit is claimed. See `execution.json` for measured wall time and peak RSS. `bridge.json` contains exact source hashes and line calculations.

This is a priced outline fragment under unverified Class-C rates. It does not select propulsion, validate the train or guideway, approve procurement, or establish an investment estimate.
