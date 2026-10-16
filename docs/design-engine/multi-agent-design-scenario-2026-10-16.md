# Multi-agent civil, mechanical and manufacturing design scenario

This scenario allocates the railway and both Baghdad factory examples to **63 controlled work packages**, then uses generative searches where the repository has a suitable computational model. The executable scope is [system-scope.json](../../engineering/generative_design/data/system-scope.json). Every package remains open until its load, material, manufacturing and evidence predicates are satisfied for the exact integrated revision. A computationally feasible representative part does not complete its parent system.

The scope audits the existing source inventories rather than treating the two newest searches as the entire railway:

| Source inventory | Assigned scope |
| --- | --- |
| [Trainset manifest](../../design/component-catalogue/catalog/buildable-trainset/buildable-trainset-manifest.json) | All 120 products and 26 assemblies |
| [Trainset factory packages](../../design/component-catalogue/catalog/buildable-trainset/factory-release-work-packages.json) | All 16 packages and 80 controlled products |
| [Production-data release register](../../design/component-catalogue/catalog/buildable-trainset/production-data-release-register.json) | All 62 locally made products and their required artifact gates |
| Supplier configuration outside those local packages | Remaining 40 products assigned in 18 parent-assembly packages |
| [Station factory packages](../../design/component-catalogue/catalog/buildable-stations/factory-release-work-packages.json) | All 9 packages and 50 controlled products across seven station archetypes |
| [Civil reusable-type release register](../../design/component-catalogue/catalog/buildable-civil/reusable-type-release-register.json) | All 6 packages and 19 reusable types |
| [Design-detail register](../../engineering/models/bim/design-detail-register.json) | All 12 mechanical interface control definitions |
| [Factory equipment register](../../engineering/factory_examples/data/equipment.json) | All 14 equipment examples, plus configured machinery and factory-system packages |

The other packages cover accepted project basis, tooling, the precast plant, equipment selection, site and drainage, factory structures/slabs/runways, MEP and fire systems, handling/transport, production flow, route compatibility, energy, system safety, integration and independent assurance. Inventory coverage proves that work has an owner; it does not prove design completion. Newly discovered requirements or components extend the controlled scope.

## Agent assignments and exchange contract

The coordinator holds the system configuration and accepted interface baseline. A civil designer owns guideway, piers, foundations and station structure variants. A mechanical designer owns vehicle, supplier-system, tool and handling variants. A manufacturing integrator checks process, stock, equipment, access, tolerances, production resources and evidence routing. An independent critic challenges shortlisted candidates and integration assumptions. Four concurrent slots support the coordinator and three workers initially; a worker slot then rotates to critique. The critic must not approve their own proposed design, and an AI role does not appoint a legally accountable design authority.

Each package records exact source paths/IDs, dependencies, owner role, available common problem mappings, new representative search mappings, proposed generative variables, unavailable capabilities and four evidence gates. A candidate exchange must retain its source hashes, architecture, variables and units, load/material assumptions, solver identity, native artifacts, reactions and interface geometry, manufacturing route, checks, rejection reasons and unknowns. Results may be compared only within a compatible declared function and load domain.

The catalogue uses **LM3 three-car product identities** while the Baghdad factory examples and several research charters use **metro-6car**. The `BASIS-CONFIGURATION` package requires an accepted six-car axle/CG and interface allocation before transferring structural results. The retained three-car axle trace and its historical 9.81 m/s² force convention remain labelled. No agent may silently scale that trace into an accepted six-car design.

## Generative iteration

1. Verify all source SHA256 values and enumerate the actual inventories before allocating work. `source_inventory[].inventory_collections` specifies the collection path, ID field and expected IDs. Require equality with current source IDs and require their coverage by the union of package `authoritative_sources` references for that exact source path. Reject missing IDs, unknown dependencies and dependency cycles.
2. Start each package from the accepted function, interfaces, load envelope and manufacturing constraints. Existing research charters retain their declared assumptions. Missing site, supplier or material inputs remain unknown and block release even if an exploratory search runs.
3. Enumerate or adaptively generate bounded alternatives. Run the actual adapter rather than copying a predecessor's score. Reject invalid geometry, missing load equilibrium, hard manufacturing limits and failed mandatory checks. Retain unsuccessful candidates so the next iteration can change the responsible variable or model.
4. Form a set of feasible alternatives for the stated research checks. Compare mass, resource/time, maintainability and imported content only when those quantities have evidence. Unknown installed price or origin stays null; it cannot improve a candidate's ranking.
5. Refine promising alternatives using independent benchmarks, holdout loads, native geometry/mesh evidence and the applicable failure cases. The critic checks scope, constitutive/load assumptions, sensitivity and unsupported extrapolation before a candidate can advance.
6. Reconcile the selected interfaces: vehicle/rail and platform gap, load/reaction transfers, bearings and movement, foundation actions, lifting/transport, machine/workpiece access, utility and heat rejection, datums and tolerance accumulation, removal/inspection paths and production resources. An accepted interface change invalidates affected descendants and reopens their evidence.
7. Freeze an integrated revision only when every package's completion predicate is true, actual manufacturing data and first articles are accepted, and appointed reviewers approve the exact evidence. Otherwise issue the remaining open-gate ledger and the next input, adapter or physical-evidence action.

The computational run has finite evaluation and wall-time budgets. Exhausting a search space or budget ends that campaign with open work recorded; it cannot turn unknown checks into passed checks. Repeating identical inputs indefinitely cannot obtain absent soil investigations, supplier capacities, material tests or signed acceptance. The coordinator resumes affected packages when a controlled input or model changes.

## Available searches and their limits

The common engine already exposes bounded problems for panels, interfaces, battery/HVAC installation, complete reference assemblies, civil alternatives/foundations, synthetic steel demonstrators and factory fixture/precast studies. The manifest maps these as **partial research coverage**. A mapping identifies a useful computational investigation; it does not declare that the adapter can qualify the entire named source product.

The new civil lane explores Pi-beam section/prestress and handling alternatives. The new mechanical lane explores a representative tooling cassette. Their `mapped_generative_lanes` entries are deliberately limited to the directly relevant beam/bed and tooling packages. Common native searches for `mechanical-cleat` and `civil-steel-beam` remain their fixed synthetic functions and loads; a successful demonstrator is not a released carbody bracket, station frame or railway bridge.

Complete crash, braking/control safety, door and gangway qualification, fire/smoke, reinforced/prestressed-concrete detailing, foundation/site acceptance, bearing/CWR interaction, building/MEP design and physical production qualification require additional discipline models and external evidence. Their packages explicitly expose those unavailable capabilities. Existing screening or reference models can support the work without supplying those acceptances.

## Manufacturing and supplier gates

A candidate needs a feasible process as well as geometry: purchasable stock/grade, tool reach and machine work envelope, weld and machining sequence, access and clamping, achievable fits/tolerances, heat treatment/finish, inspection datums, material/serial identity, replacement/service access and a qualified first article. For precast work this includes released reinforcement/end zones/inserts, concrete mix and transfer strength, strand/grip compatibility, losses, stressing/release and curing procedures, handling/storage/transport states and accepted mould/bed capacity.

Each machine or bought subsystem must carry exact-model origin, specification, GA and interface evidence. Prioritise **confirmed British manufacture**, then evaluate UK supply/integration and overseas manufacture explicitly where needed. Record Northern Ireland manufacture distinctly where relevant. A UK company address, distributor or potential UKEF eligibility does not establish manufacturing origin. Compare capacity at the actual working span, geometry, duty and Baghdad conditions; a catalogue model-class maximum is insufficient. Enquiries remain prepared and unsent. This scenario does not contact suppliers or authorize purchasing.

Manufacturing closure requires issued, checked and approved drawings, production files, material/process and inspection instructions; accepted supplier returns; measured tooling and first articles; and an independently accepted exact configuration. Existing frozen factory review snapshots remain historical evidence. The new campaign creates separate results and keeps `physical_release: false` while any required gate remains open.

## Run and review

The campaign entry points keep planning, execution, integrity verification and review publication separate:

```sh
./osr design campaign plan
./osr design campaign run --output build/generative-design/baghdad-1 \
  --native --common native --civil-budget 128 --mechanical-budget 128
./osr design campaign verify --output build/generative-design/baghdad-1
./osr design campaign publish --output build/generative-design/baghdad-1 \
  --destination docs/design-engine/generative-campaign
```

The two lane budgets are exploration limits, not iteration counts or proof of convergence. The common-engine path also accepts an existing controlled store and explicit `--import-job` references for source-bound native runs; the verifier must validate their integrity and applicability before counting their evidence. Other common charters receive bounded screen variations. Coupled stressing-bed sensitivity must carry any increased prestress reactions into the bed study rather than assuming the predecessor bed remains suitable.

The retained campaign report is the source for actual attempted/evaluated candidates, rejection reasons, native evidence and package coverage. No counts or feasibility results are implied by this scenario document. The per-package ledger must distinguish a useful computational result from missing accepted basis, unavailable adapter, supplier evidence, physical qualification and independent acceptance.
