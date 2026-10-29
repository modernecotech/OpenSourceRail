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
```

The Iraqi input library includes CSO construction-material prices and governorate wages, an Iraqi state producer's aluminium price page, and domestic steel/precast manufacturer leads. Missing design-grade specifications, supplier availability, current binding quotes, production yields, employer-loaded labour, tooling, QA, utilities, transport and installation remain explicit gaps. Local supplier pages document capability leads only; they do not authorize or select products.

The sourcing backlog also supports `decision_sensitivity` declarations on candidate BOM groups. A declaration can include cost and mass impact ranges with their source/model basis, uncertainty fraction and basis, downstream decisions, safety/design-blocking status, alternatives, simulations to rerun, supplier/catalogue evidence requests, and a cost margin for testing whether the result could change the preferred candidate. The controller scores each dimension as `range width × uncertainty fraction × (1 + dependent decision count)`, ranks safety/design blockers first, and keeps cost and mass on separate axes with Pareto fronts. It never converts IQD, USD and kilograms into one score. Missing inputs remain unranked with explicit missing-field names; category priority is only the fallback queue.

The current federated BOM has no reviewed `decision_sensitivity` declarations, so its economic and mass impact scores remain unavailable. The controller reports missing inputs for the 137 evaluated unresolved groups; 6,905 other groups remain pending and are unevaluated, not assigned numeric or zero scores. The newly sourced market and wage statistics do not yet supply candidate purchase quantities, alternative design deltas, or a measured workshop labour route. The feature makes those inputs consumable and exposes the gap; it does not manufacture an expected value of information from category labels.

Candidate substitutions are only proposals. A supplier mass observation for a different SKU does not transfer old CAD geometry, interfaces, joints, electrical duty or maintenance assumptions. The proposal creates a new physical identity and invalidates dependent analyses. A property-only observation can preserve the physical identity only for the same exact product identity and scope.

## Evidence boundary

All new records default to no engineering/procurement approval, no physical acceptance, no manufacturing/operating release, no selected-reference change and no zero-for-unknown behavior. Current product rows are research leads. An offer does not prove compatibility; compatible catalogue scope does not prove a fully installed component; a material price does not establish a structural allowable; a cost ledger without complete quantities and commercial coverage is not a railway estimate.

The user-facing dashboard and sourcing dossier report coverage by requirement and maintain explicit holds. Native physical qualification, supplier responses, Iraqi installed civil rates, complete vehicle mass, moving LIM force map, validated journey, safety acceptance and whole-life cost remain separate work.
