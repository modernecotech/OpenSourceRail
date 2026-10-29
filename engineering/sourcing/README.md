# Sourcing, materials and cost intelligence

This package ingests dated, source-linked observations and evaluates them against one revision-bound candidate input. It supports manufacturer catalogues, distributor offers, commodity benchmarks, exchange rates, construction awards, engineering estimates and direct supplier quotations. A source lead, product listing, engineering estimate and authenticated quotation remain different evidence classes.

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

Candidate substitutions are only proposals. A supplier mass observation for a different SKU does not transfer old CAD geometry, interfaces, joints, electrical duty or maintenance assumptions. The proposal creates a new physical identity and invalidates dependent analyses. A property-only observation can preserve the physical identity only for the same exact product identity and scope.

## Evidence boundary

All new records default to no engineering/procurement approval, no physical acceptance, no manufacturing/operating release, no selected-reference change and no zero-for-unknown behavior. Current product rows are research leads. An offer does not prove compatibility; compatible catalogue scope does not prove a fully installed component; a material price does not establish a structural allowable; a cost ledger without complete quantities and commercial coverage is not a railway estimate.

The user-facing dashboard and sourcing dossier report coverage by requirement and maintain explicit holds. Native physical qualification, supplier responses, Iraqi installed civil rates, complete vehicle mass, moving LIM force map, validated journey, safety acceptance and whole-life cost remain separate work.
