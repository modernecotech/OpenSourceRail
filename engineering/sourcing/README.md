# Sourcing, materials and cost intelligence

This package ingests dated, source-linked observations and evaluates them against one revision-bound candidate input. It supports manufacturer catalogues, distributor offers, commodity benchmarks, national statistics, marketplace indicators, exchange rates, construction awards, engineering estimates and direct supplier quotations. A source lead, product listing, engineering estimate and authenticated quotation remain different evidence classes.

## Data flow

```text
typed twin/BOM input ──> candidate-scoped requirements ──> specification match
                                  │                                │
dated source snapshot ──> catalogue products/offers ───────────────┤
commodity and FX data ─────────────────────────────────────────────┤
                                                                  ↓
                              price tiers / order constraints / uncertainty
                                                                  ↓
              cost coverage + disabled RFQ drafts + redesign/evidence tasks
```

The canonical records live in `engineering/sourcing/model.py`. The append-only SQLite `Store` preserves source, product, offer, FX, benchmark, process, requirement, assessment, RFQ and run identities. JSON packets contain the exact historical catalogue/input/request and replay the workflow without fetching a replacement price. A price date is not a valid-until date, supplier authentication, installed price or engineering approval.

Use `inputs.load_twin` for the vehicle registry, the 12-account selected reference BOM, or a typed federated whole-railway BOM. These namespaces deliberately remain distinct. The vehicle registry is not station/civil equipment; the selected BOM's aggregate accounts do not carry unit purchase quantities. Large requirements can be budgeted explicitly: unevaluated requirements persist in the publication backlog.

For a federated BOM that declares a `manufacturing_BOM`, the adapter can replace located stock-occurrence requirements with the source-declared manufacturing groups. It admits this roll-up only when group identities and candidate bindings are valid, memberships are disjoint, groups are homogeneous by system/material/stock scope, and the groups cover every located occurrence exactly once. Each resulting requirement and disabled RFQ keeps the full original occurrence-ID list and source group identity; unlocated accounts stay separate. This creates a practical request scope, not a purchasable bill: gross-stock mass is descriptive, while purchased quantity, order unit, yield, processing, price and installed completeness stay unresolved unless the source actually supplies usable evidence.

`./osr source procurement-bom` adds a higher-level draft quote-package view. Its current explicit path rules group the federated research candidate into body-system kits by car, partial bogie stock packages, passive-secondary kits by car, rail/concrete stock packages by span, and station-LIM primary material sets by bank. Each package links every member occurrence and source manufacturing, procurement and manufacturing-operation ID. A separate hierarchy-only index cross-references **4,766 of the 4,773 unlocated accounts** to related car, bogie, secondary, span or bank packages through **230 non-additive associations**. The links identify unresolved systems for supplier discussions; they do not become package members and add no mass, quantity or cost. Seven network-level infrastructure obligations remain unlinked. Unmatched located occurrences remain individual held lines. An optional same-candidate regional cost reference maps its three 2025 Baghdad concrete material-plus-labour scenarios onto the 81 exact span packages and original occurrences. The scopes make supplier inquiry packages more complete while preserving unknown purchase quantities, prices and assembly completeness.

## Build a source-linked research takeoff

`manufacturing.laminate_requirements` derives gross and net glass, mixed resin, core and declared process requirements from an explicit area, ply schedule, material fraction and scrap hypothesis. Missing adhesive, inserts, consumables, labour, tooling and cure time stay unresolved. `studies.laminate_study_requirements` demonstrates three separately identified 10 m² roof-panel material hypotheses linked to the actual digital-twin parent candidate. They are not cut from the vehicle CAD and do not replace its body revision.

Seed the reviewed research snapshot and load the current vehicle registry:

```python
from engineering.sourcing.catalogue import seed
from engineering.sourcing.database import Store
from engineering.sourcing.inputs import load_twin
from engineering.sourcing.publication import execute, publish, verify

with Store("/outside/the/checkout/sourcing.sqlite") as store:
    seed(store)
    source_input = load_twin("docs/design-engine/frame-refinement/packet")
    request = {"as_of": "2026-10-29", "target_currency": "GBP"}
    result = execute(store, source_input, request)
    publish(store, result, source_input, request, "/fresh/output/packet")
    verify("/fresh/output/packet")
```

Use a fresh output directory for each estimate. Never overwrite an old price observation. The CLI offers the same operations; run `./osr source --help` after installation.

## Source adapters and commercial controls

The bounded adapters in `adapters/` parse official World Bank monthly commodity workbooks, ECB daily FX XML, Caltrans awarded-price pages/CSV, supplier quotation files and DigiKey v4 catalogue responses. Easy Composites catalogue pages can be parsed only for an explicitly selected SKU and currency. Raw public input bytes are hashed; they are not copied into the repository unless redistribution rights allow it. DigiKey live pricing requires user-provided account credentials and an eligible API account. Missing credentials produce a hold, never a synthetic offer.

The current snapshot includes public catalogue observations for selected GFRP cloth/resin, a prototype vacuum pump, door mechanism, HVAC units, solar module, rail profile, fastening leads, precast production equipment and crane specifications. It also retains World Bank metal benchmarks, ECB exchange rates, Caltrans civil award rows and Iraqi/UNGM procurement leads. Scope notes and retrieval dates are part of each record. A California awarded unit rate is a benchmark, not an Iraqi construction price; visible Iraqi BOQ documents without awarded rates stay unpriced.

Order MOQ/multiples, taxes, shipping, delivery terms, part origin and installation scope remain unknown where the source did not state them. The evaluator may show a listed-price extension at requested quantity, but it does not treat this as an order total or purchasable quantity. Supplier quotations parsed from a file are unverified until authenticated outside the file. No supplier communications are sent.

## Domestic fabrication cost screen

`fabrication.domestic_fabrication_estimate` and `./osr source estimate fabrication` calculate an explicit recipe from exact source-linked material and wage benchmarks. `fabrication.domestic_fabrication_takeoff_estimate` and `./osr source estimate takeoff` can scale that recipe onto one exact, fully quantified material-takeoff roll-up while retaining its manufacturing-group and engineering-occurrence IDs. The formula is:

```text
estimate = (material quantity × material benchmark rate
          + person-hours × hourly wage benchmark) × (1 + explicit uplift)
```

The uplift is set to 20% in the Iraq reference examples. It is a planning allowance on direct material plus direct labour; the database does not assign it to overhead, profit, contingency or tax. Material and labour quantities must be declared. Units and currency must match the selected benchmarks; this screen does not silently convert currencies or assume unknown quantities are zero. The output retains the digital-twin candidate and input identities, exact benchmark/source IDs, line extensions and excluded cost categories. A unit-rate screen remains separate from candidate takeoff, complete process cost and installed cost.

The example recipes in `docs/design-engine/sourcing/domestic-fabrication/recipes/` estimate one tonne of reinforcing steel input through an illustrative cut/bend route using the September 2026 Iraqi-origin CSO rebar benchmark and the 2025 Baghdad skilled-worker average wage. Labour hours are explicitly varied at 4/8/16 hours per input tonne because measured local cycle times were unavailable. These are generic unit-rate screens and are not mapped to a railway occurrence. The separate concrete takeoff recipes apply their declared batch assumptions to the exact modeled concrete-volume roll-up, preserve all mapped group and occurrence IDs, and write a separate ingredient/labour/uplift estimate for each group. They still do not represent a designed mix, purchased order, finished beam or complete installed cost.

`iraq_cost_scenarios` uses the official 2025 CSO Iraqi-origin material-price and governorate wage tables plus Ur Company posted aluminium prices to create 102 source-linked regional scenarios. It emits concrete batching estimates where all three local material benchmarks are available, rebar cut/bend scenarios across the 15 listed governorates, processing sensitivities for three profile forms and four sheet forms, and 2/4/8-hour Baghdad concrete estimates mapped to the exact research takeoff groups and occurrence IDs. A source-table zero is treated as missing. The file-backed report is not a supplier quote; its metal-processing hours are assumptions, not local factory routes, and the 20% allowance applies only to declared raw material plus base-wage proxy.

`iraq_gfrp_cost_scenarios` and `./osr source estimate gfrp-laminate` evaluate the exact three current 10 m² GFRP laminate study packets using their listed Easy Composites cloth/resin extensions, a dated Central Bank of Iraq GBP/IQD reference, and the CSO 2025 skilled-worker hourly base wage. Each recipe carries Baghdad 8/16/32-hour scenarios plus 135 regional scenarios (15 listed governorates × 3 hour assumptions × 3 recipes), applies the 20% allowance to known listed material plus base labour, and retains unresolved core/adhesive costs as unknown. The regional source excludes Kurdistan Region; construction-worker wage averages are only a proxy for composite-shop labour, and employer burden is absent. The output is an Iraqi-labour/imported-material sensitivity, not a local composite quote or a complete fabrication estimate. Packet hashes, candidate identities and the current source-observation epoch are checked before computation.

```bash
./tools/automation/osr-python -m engineering.sourcing.iraq_cost_scenarios \
  --takeoff docs/design-engine/sourcing/material-takeoff/federated-v06-stock-takeoff.json.gz \
  --output build/iraq-domestic-cost-scenarios
```

```bash
./osr source seed
./osr source estimate fabrication \
  --input docs/design-engine/sourcing/packets/federated-purchasing-groups-iraq-sources-final/input.json.gz \
  --recipe docs/design-engine/sourcing/domestic-fabrication/recipes/rebar-cut-bend-08h.json \
  --output /tmp/osr-rebar-fabrication-estimate.json

./osr source estimate takeoff \
  --takeoff docs/design-engine/sourcing/material-takeoff/federated-v06-stock-takeoff.json.gz \
  --recipe docs/design-engine/sourcing/domestic-fabrication/takeoff-recipes/concrete-04h-per-m3.json \
  --output /tmp/osr-concrete-takeoff-estimate.json

./osr source estimate gfrp-laminate \
  --packet-root docs/design-engine/sourcing/packets/laminate-materials-iraq-domestic-sources-v2 \
  --output /tmp/osr-gfrp-local-fabrication-screen.json
```

The Iraqi input library includes CSO construction-material prices and governorate wages, an Iraqi state producer's aluminium price page, and domestic steel/precast manufacturer leads. It also records local GRP façade, polymer raw-material and polyester/epoxy supplier leads, while keeping them separate from sourced product offers. Missing design-grade specifications, supplier availability, current binding quotes, production yields, locally made glass-fibre reinforcement, employer-loaded labour, tooling, QA, utilities, transport and installation remain explicit gaps. Local supplier pages document capability leads only; they do not authorize or select products.

The source-bound draft package output for the federated research candidate is indexed in `docs/design-engine/sourcing/validation.json` and detailed in `docs/design-engine/sourcing/procurement-bom/federated-v06-research-packages.json.gz`. Its internal package counts are not purchase quantities; occurrence identity and the source research candidate remain fixed.

The sourcing backlog also supports `decision_sensitivity` declarations on candidate BOM groups. A declaration can include cost and mass impact ranges with their source/model basis, uncertainty fraction and basis, downstream decisions, safety/design-blocking status, alternatives, simulations to rerun, supplier/catalogue evidence requests, and a cost margin for testing whether the result could change the preferred candidate. The controller scores each dimension as `range width × uncertainty fraction × (1 + dependent decision count)`, ranks safety/design blockers first, and keeps cost and mass on separate axes with Pareto fronts. It never converts IQD, USD and kilograms into one score. Missing inputs remain unranked with explicit missing-field names; category priority is only the fallback queue.

The current federated BOM has no reviewed `decision_sensitivity` declarations, so its economic and mass impact scores remain unavailable. The controller reports missing inputs for the 137 evaluated unresolved groups; 6,905 other groups remain pending and are unevaluated, not assigned numeric or zero scores. The newly sourced market and wage statistics do not yet supply candidate purchase quantities, alternative design deltas, or a measured workshop labour route. The feature makes those inputs consumable and exposes the gap; it does not manufacture an expected value of information from category labels.

Candidate substitutions are only proposals. A supplier mass observation for a different SKU does not transfer old CAD geometry, interfaces, joints, electrical duty or maintenance assumptions. The proposal creates a new physical identity and invalidates dependent analyses. A property-only observation can preserve the physical identity only for the same exact product identity and scope.

## Evidence boundary

All new records default to no engineering/procurement approval, no physical acceptance, no manufacturing/operating release, no selected-reference change and no zero-for-unknown behavior. Current product rows are research leads. An offer does not prove compatibility; compatible catalogue scope does not prove a fully installed component; a material price does not establish a structural allowable; a cost ledger without complete quantities and commercial coverage is not a railway estimate.

The user-facing dashboard and sourcing dossier report coverage by requirement and maintain explicit holds. Native physical qualification, supplier responses, Iraqi installed civil rates, complete vehicle mass, moving LIM force map, validated journey, safety acceptance and whole-life cost remain separate work.
