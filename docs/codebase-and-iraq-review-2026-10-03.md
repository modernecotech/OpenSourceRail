# Codebase review and regenerated Iraqi examples — 3 October 2026

Reviewed baseline: `4951645a287b0de0d9071b473ef68c417ed9f4b5` and the local changes described here. Changes are local and have not been committed or published. This review combines repository-wide automated checks with inspection of the architecture, assurance boundaries, regeneration pipeline, cost models, project controls and documentation. It does not claim manual inspection of every source line or physical acceptance of a railway.

The three requested cities are complete **planning examples** against the current controlled layouts and software. They contain current engineering, operations, financial and simulation evidence. Construction and operational release remain blocked by their recorded physical gates. The Iraqi funding structure is proposed and uncommitted.

## Findings and corrections

| Finding | Correction and evidence |
|---|---|
| A routine rebuild could replace an existing layout using unrelated local corridor caches. In the review trial this removed Mosul's ring and relocated Samawah's interchange. | Retain controlled layouts by default. `--resynthesise-design`, `--resynthesise-corridors` or `--from-scratch` explicitly request replacement. Regenerated examples retain the original station identities and controlled workspace inputs. A regression verifies preservation of a ring despite an unrelated cache. |
| Resynthesis omitted Samawah's explicit hot-axle detection policy. | Retain its controlled HABD setting through `design-overrides.toml`; validate override scope and values before emitting scenarios. Positive HABD passage tests remain in place. |
| Cost recalculation did not refresh station, depot and fleet unit prices, and could rewrite historical execution hashes and workspace locks. | Refresh every affected cost bucket and EPC using the current catalogue. Record a cost migration receipt; never reattest old runs, approvals or source locks. A regression changes prices while preserving an execution record. The portfolio's existing fleet prices were already current: the audit changed zero designs. |
| Project controls called 30-working-day buckets calendar months. | Convert working-day milestones using the explicit 260-working-day annual assumption and 30 working days before NTP. Regenerate all 266 project twins, construction cash requirements and operations manifests. The approved Iraqi holiday/calendar baseline remains open. |
| Generic five-year, uniform debt financing obscured actual Iraqi draw dates, currencies and public support. | Add schedule-linked Chinese component credit, government capital, sovereign IQD bonds and IQD bank credit. Separate interest, principal, fees, reserves, subsidies and cash gaps. Retain generic calculations only as labelled comparators. |
| Finance and twin records could appear current despite stale additional financial inputs. | Validate all declared input hashes, including the Iraq terms, financing implementation and retained schedule projection. The portfolio twin audit checks current budgets, bucket reconciliation and source bindings. |
| Large ignored procurement CSVs left funding schedules unavailable in a fresh checkout. | Track a compact `funding-input.csv` projection of actual budget, timing and procurement-origin fields. Finance validates it against current CAPEX before using it. |
| Package completion conflated a complete planning example with accepted infrastructure. | Add explicit `planning_example_complete` and `operational_release=false`. Depot and stabling placement/cost/physical failures remain visible; selected simulation failures cannot be excused. Default package status remains `incomplete` while physical gates are open. |
| Native resilience reruns discarded completed executions and processed independent cases in rigid batches. | Reuse actual runs only when simulator binary, scenario, duration, options and output hashes match; reject damaged cache entries. Execute independent cases through a shared worker pool. No simulation physics or safety acceptance criterion was weakened. |
| The subsystem control register omitted the current dual-channel source. | Recompile its generated register against the actual source set; retain qualification boundaries. |
| RFC 0001's current amendment disagreed with its older body about voter sizing, snapshots, witnesses and service availability. Its witness intersection also ambiguously took a maximum speed restriction. | Align the body with the three-voter reference and unimplemented logical snapshots/witnesses; separate original timing/cost targets from measured behavior. Preserve occupied resources after permission expiry, identify required-channel loss as a stop, and specify the minimum permitted maximum speed on compatible routes. Remove unsupported blanket vendor-cost and availability comparisons. |
| Station rebuilds could omit installed EnergyPlus/FDS tools because their directory was absent from the inherited search path. | Export the configured engineering toolchain path and execute both tools again. Baseline failing thermal/fire cases remain recorded alongside the proposed mitigations. |
| City documents and the Baghdad offer contained stale or fixed quantities. | Generate current quantities, schedule, costs, funding and screenshots from controlled records; rebuild the evidence-linked Baghdad PDF. Update Iraq/national briefs, portfolio summaries, catalogue index and documentation inventory. Repository health now checks the structured Iraqi disclosure rather than requiring obsolete generic financing rows. |
| Browser acceptance omitted the new civil register in its drainage/ground and structural role counts. Its temporary workspaces also appeared as missing public documentation during concurrent checks. | Require ten drainage/ground and eleven structural roles, explicitly verifying the missing civil register remains a gate. Ignore disposable hidden browser workspaces and align book-manifest tests with the reader's existing hidden-directory exclusion. |
| The reader-book rebuild failed on qualification table rows taller than one page. Its city briefs also truncated networks to eight lines and presented design-base cost without the separately sized solar provision. | Enable row pagination, respect PDF frame padding, show every line and use current design-bound reconciled city finance totals. Add a regression that builds a PDF with a multi-page table row and check all 265 brief totals/line counts. Include the three Iraqi funding appraisals and consolidated programme in the book. |

Superseded station-only experiments remain diagnostic records, with their original source bindings and failed results. Their hashes were not rewritten to imply acceptance of the selected station/depot plan. Other cities' historical solver evidence is retained and explicitly marked unverified where stale; this task executes the full city refresh for Baghdad, Samawah and Mosul.

## Current city examples

| City | Lines | Stations | Trainsets | City CAPEX, USD m | Capital-cash horizon, calendar months | Minimum operating DSCR before public support |
|---|---:|---:|---:|---:|---:|---:|
| [Baghdad](../cities/catalogue/west-asia/Iraq/Baghdad/README.md) | 9 | 182 | 831 | 7,555.74 | 361 | 1.00 |
| [Samawah](../cities/catalogue/west-asia/Iraq/Samawah/README.md) | 3 | 21 | 108 | 415.34 | 53 | 0.70 |
| [Mosul](../cities/catalogue/west-asia/Iraq/Mosul/README.md) | 6 | 69 | 256 | 1,926.74 | 116 | 0.21 |

These totals include timetable-sized solar provision and exclude the shared national factory. Geometry is a planning layout, not a surveyed route. All three nominal simulations and eight mandatory resilience scenarios pass. Samawah's selected 48-hour hybrid stabling replay passes both overnight allocation and morning-launch checks: 40 trainsets at stations and 68 at depots. This does not resolve surveyed depot access, land, detailed yard geometry, costs or physical acceptance.

The finance horizon follows the existing finite-resource construction/manufacturing schedule. Baghdad's roughly 30-year full-network completion is a significant planning finding. This cannot be marketed as a five-year financed construction programme. Approved phases, production capacity and phase-specific revenue require a new resource and operating baseline. The consolidated comparison does not accept simultaneous use of one factory by all three cities.

## Iraqi sources, uses and cashflows

The [three-city funding programme](../cities/catalogue/west-asia/Iraq/IRAQ-FUNDING-PROGRAMME.md) includes one shared factory, counted once at USD 299.16 million plus USD 20.94 million EPC. Consolidated capital uses are **USD 10,217.93 million**.

| Proposed capital source | USD million |
|---|---:|
| Chinese export buyer credit | 924.34 |
| Government capital | 5,576.15 |
| Domestic IQD bonds | 2,788.08 |
| IQD bank term credit | 929.36 |
| **Total** | **10,217.93** |

The editable [Iraq assumptions](../lib/templates/iraq-funding.toml) allocate proposed Chinese credit to qualified invoices for solar panels/inverters, bogies, traction and station batteries, windows, doors and shared manufacturing tooling. These are allocations **within existing imported budgets**, not additional CAPEX or verified supplier origin. The assumed invoice advance is 85%; government cash covers the downpayment. Government, bonds and bank credit cover 60%, 30% and 10% respectively of the capital remaining after proposed Chinese proceeds.

Proposed terms are USD Chinese credit at 5% with 48 months' grace and 180 months' repayment; IQD bonds at 8% with 24 months' grace and 180 months' repayment; and IQD bank credit at 9% with immediate amortisation over 84 months. Each draw starts its own grace/maturity clock. These rates, tenors, allocations and guarantees are appraisal assumptions, not offered facilities. Construction cohorts require separate approved facilities; a long modelled programme does not imply a decades-long lender draw window.

Monthly ledgers show milestone capital requirements and receipts, native-currency debt, fees, revenue ramps, OPEX, principal/interest, unrestricted cash and restricted debt-service reserves. Government support is explicit and excluded from DSCR. Peak combined annual public cash in the simultaneous-financial-close comparison is **USD 1,249.18 million**, including capital, fees, construction interest, reserves and operating/debt support. Fares do not fund pre-opening construction. Samawah and Mosul require explicit operating/debt support in the low-demand case.

The model covers demand reduction, CAPEX increases, IQD depreciation, interest increases, delayed commissioning, declined Chinese credit, delayed public payments, short bullet-bond redemption and combined downside. Declined/delayed funding creates visible uncovered requirements; it does not silently create a bridge loan or rollover. Base arithmetic reconciliation and repayment within the model horizon establish calculation consistency, not committed funding or bankability.

Use the city [Baghdad](../cities/catalogue/west-asia/Iraq/Baghdad/engineering/finance/FUNDING-MODEL.md), [Samawah](../cities/catalogue/west-asia/Iraq/Samawah/engineering/finance/FUNDING-MODEL.md) and [Mosul](../cities/catalogue/west-asia/Iraq/Mosul/engineering/finance/FUNDING-MODEL.md) funding pages for component allocations, sensitivity tables, charts and monthly/annual CSVs. The [combined annual cashflow](../cities/catalogue/west-asia/Iraq/finance/three-city-annual-cashflow.csv) exposes public exposure across the three cities and factory. Structured planning models were also generated for the remaining Iraqi catalogue cities, which are outside this consolidated programme.

## Primary sources and remaining decisions

The [IMF 2025 Article IV release](https://www.imf.org/en/news/articles/2025/07/08/pr-25243-iraq-imf-executive-board-concludes-2025-article-iv-consultation) supplies the historical 2024 average of 1,300 IQD/USD and fiscal context. The model uses that historical anchor, not a verified October 2026 dealing rate. Existing income/demand inputs are explicitly labelled planning proxies rather than current surveyed Iraqi statistics.

The [CBI fiscal-agent description](https://www.cbi.iq/page/26) and [Injaz issuance example](https://cbi.iq/news/view/2620) support a proposed Ministry of Finance sovereign issuance route. This review does not establish municipal borrowing powers or market acceptance of the proposed long amortising bonds. [China Exim's export buyer-credit product](https://english.eximbank.gov.cn/Business/CreditB/SupportingFT/201810/t20181016_6965.html) supports the instrument concept; it does not verify this model's advance, interest rate or tenor.

Financial close needs a controlled sponsor and borrowing authority, signed term sheets and guarantees/insurance where required, appropriation and subsidy agreements, bond placement/redemption arrangements, supplier-origin evidence, quotations, FX access, tax/duty/land/utility pricing, surveyed demand and an accepted phased resource calendar. Base costs and revenues are nominal without escalation; imported maintenance exposure and factory operating budgets need separate appraisal. The factory ledger isolates capital financing and does not represent a complete factory business case.

Existing platform boundaries remain: process-level paired control is a software reference; independent physical outputs/watchdogs/power, calibrated train and infrastructure interfaces, formal refinement, HIL and independent assessment remain open. The city simulator is not an accepted export of a complete city into the bounded two-train TACS reference. Passing software tests does not close those gaps.

## Validation record

| Check | Result |
|---|---|
| Rust workspace, all targets/features, and documentation tests | 974 passed, zero failures, one ignored; Clippy passes with warnings denied. |
| Full Python suites across city generation, component catalogue, engineering and automation | 1,499 passed, one skipped, 12 subtests passed; the additional book pagination regression is checked separately after its fix. The single warning is the deliberately duplicated ZIP entry in an invalid-backup regression. |
| Frontend unit and browser acceptance | Ten unit tests passed; 42 browser cases passed in the full run, followed by a passing City Studio rerun after correcting its stale required-role assertions. All 43 cases are verified, including all 145 City Studio checks. |
| Three-city native simulation | Nominal screens and all eight mandatory resilience cases pass for each city. |
| Samawah hybrid stabling | Both overnight cycles and morning launches pass in the selected 48-hour replay. |
| Station thermal/fire and analytical screens | Actual EnergyPlus and FDS runs completed; mitigation comparisons retained without physical release. |
| Financial/project controls audit | All 266 cities reconcile; zero findings. |
| City packages | All three have zero missing artifacts, no stale analysis sources, current operations bundles and `planning_example_complete=true`; depot/stabling physical gates remain open. |
| Documentation and hygiene | Maintained/generated README checks, national/portfolio/overview/catalogue drift checks, Markdown inventory, repository health, artifact-size and whitespace checks pass. CSV CRLF is recognised as its existing format. |

The reader book includes this review, the consolidated Iraq programme and the three full funding appraisals. The Baghdad concept/FEED offer is also rebuilt with current source-bound figures and visually checked screenshots/charts. Tests establish the recorded software and planning behavior; they do not close the financial, physical or approval decisions above.
