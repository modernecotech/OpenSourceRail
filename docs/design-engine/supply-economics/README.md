# Project-volume purchasing and manufacturing

The current outline calculator compares **original reference rates**, **China-origin bulk purchasing with local assembly**, and **project-volume make/buy**. Select a pricing basis in the Workbench. Transport demand, train mass, civil quantities, required force and service performance stay the same; this is a pricing evaluation, without hardware or procurement approval.

<!-- BEGIN calculated supply comparison -->
## Same-service 30 km comparison

All three rows retain 12 stations, 52 six-car trainsets, 120-second peak headway and the same physical quantities.

| Pricing scenario | Central installed capital | Central cost / route-km | Central 30-year NPV |
| --- | --- | --- | --- |
| Original generic rates | US$738.0m | US$24.60m | US$1,568.3m |
| China-origin bulk purchasing | US$554.3m | US$18.48m | US$1,331.6m |
| Project-volume make/buy | US$548.1m | US$18.27m | US$1,324.4m |

The current project case spans US$172.1m / US$548.1m / US$2,374.0m, low/base/high. These are broad sensitivity cases, not confidence bounds or supplier offers.

Calculation identity: `68c16fd5030fce52298409f35bc34bd3f3c6ba0345e1b9f044a759826879e274`.
<!-- END calculated supply comparison -->

## What changed

The original vehicle estimate applied a finished-equipment allowance of IQD 80,000/kg (about US$53/kg) to unresolved body stock as well as equipment. Its base aluminium and steel family proxies were about US$12/kg and US$6.6/kg. The new evaluator replaces selected structural-stock allowances with explicit material mixtures, yield, processing, labour, machine operation, QA and supplier overhead. Unknown materials remain pricing proxies; no material strength, installed mass or geometry is changed.

The [versioned evidence dataset](../../../engineering/outline/data/china-supply-20261104.json) records Chinese official wholesale benchmarks and manufacturer advertisements with grade, currency, unit, minimum quantity, terms and exclusions. The [NBS October 21–31 release](https://www.stats.gov.cn/english/PressRelease/202611/t20261104_1965741.html) and [CFETS reference FX](https://www.chinamoney.com.cn/english/bmkcpr/index.html) provide reproducible commodity/translation observations. Manufacturer motor and converter listings calibrate bare industrial equipment only.

Current Chinese aluminium-feedstock and steel benchmarks are below the original proxies. Copper is higher than the former allowance. A cheap extrusion advertisement below the current ingot benchmark is held for reconciliation. The US$37.50 seat is a shell without legs/armrests; an ambiguously rated US$2,890 HVAC listing is not substituted for a complete qualified train installation. Batteries, HVAC, seating and other unmatched equipment retain bounded allowances.

## Bulk pricing and landed scope

Quantity tiers are final rates. The model does not apply another blanket discount to already-wholesale or bulk prices. At the declared project scale, setup and fixed costs are divided only over committed quantities, and supplier manufacturing costs remain inside purchased prices.

Finished purchases include freight, packing/handling, insurance, duty assumptions, local delivery and incoming QA. Long structural subassemblies receive an explicit oversized/volumetric delivery allowance; the model does not assume that a17 m frame fits an ordinary container or that new modular joints already exist. Grade, current, temperature, overload, fire and rail-interface compatibility remain separate engineering requirements.

Import duty already included in landed component rates is excluded from the second project allowance. The remaining provision covers unmatched equipment and unlanded packages. These are planning cash assumptions, not statements of tax law.

## Establish manufacturing when it pays

Each comparison includes purchased material, yield/scrap, productive and paid labour, setup, cash machine operation, energy, consumables and QA. Making adds machinery, tooling, commissioning and the required parallel cells. Shared buildings, yards and land are allocated once in the project ledger. Full machine-hire/depreciation charges are not added on top of owned equipment.

The capacity basis is three years, two eight-hour production/construction shifts,250 workdays/year and 75% productive utilisation. This gives 9,000 productive hours per workplace/cell. Paid idle time is charged through the wage basis once. Parallel cells and batch/setup steps make the break-even curve potentially nonmonotonic; the kernel reports its examined domain and does not invent one global crossover.

Under the declared assumptions, local precasting and complete fastener integration can be selected at 3,000 spans and 210,000 fastener assemblies. Project precasting counts 27 base-case moulds, rather than 20 moulds with a second availability penalty omitted. The model buys finished 60E1 rail from an existing mill; it does not substitute the advertised GB43 profile or finance a new rolling mill for this batch. Vehicle decisions retain their complete alternative calculations, including imported precision running components and local fabrication options.

With long-load delivery included, the base vehicle comparison selects local underframe and mixed body-stock production. Four other repriced subassembly groups remain purchases. The selected 312-car production routes require US$475,000 of owned process equipment/tooling/commissioning and 590 m² of process-cell floor; the project separately prices shared buildings, receiving/storage, assembly, land and the civil facilities once. These are calculated workshop requirements, not approved factory quotations or verified production layouts.

Future fleet replacements include the relevant new production setup once. Initial factory cost is not amortized over speculative future orders, and precast plant is not automatically rebuilt with the vehicle fleet. A cheaper purchase price alone does not prove lower physical maintenance or disposal effort, so those reserves remain at the original same-service basis. Prototype, independent-review and contingency obligations remain; percentage provisions are recalculated on their declared scope, rather than described as supplier discounts.

## Reproduction and limits

[summary.json](summary.json) contains compact results and [manifest.json](manifest.json) binds the source epoch and full private calculation hash. Full ledgers, source checkpoints and unsuccessful review attempts remain outside Git. The study compares the exact 30 km / 12 station / 52 train benchmark at equal service; the separate demand-led example has a different requirement identity.

```sh
.venv/bin/python -m engineering.outline supply --output build/my-supply-study
.venv/bin/python -m engineering.outline supply-verify --output build/my-supply-study
```

Use a fresh output directory. Supplier advertisements and calculated finished-component prices are not firm delivered quotations. All prices are Class C planning scenarios with wide uncertainty. Physical qualification, available propulsion force, degraded stopping and site-specific feasibility remain open; existing grade sensitivity failures are retained. Other transport approaches remain available under the open transport-goal policy.
