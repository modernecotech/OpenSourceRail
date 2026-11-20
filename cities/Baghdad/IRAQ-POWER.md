# Buying traction electricity and equipment in Iraq

Budget **144.2 IQD/kWh (9.55 US cents)** for energy in the base case. At the published service level that buys 524.3 GWh/year for the first network and 1,965.5 GWh/year for the metropolitan alternative. The electricity bill falls by about $12.8m/year and $48.2m/year respectively against the existing $0.12/kWh engineering allowance. Each network has its own service and fleet. The main financing model can replace its energy line with the appropriate case. [Engineering cost ledger](COST-AND-DELIVERY.md) · [Buyer financing](BUYER-COMPARISON.md)

<!-- calculated tables -->

| Network | Electricity case | IQD/kWh | Energy $m/year | Change from ledger $m/year | 30-year overhead premium after repricing energy, $m |
|---|---|---:|---:|---:|---:|
| First | Low | 60.0 | 20.8 | -42.1 | 43.8 |
| First | Base | 144.2 | 50.1 | -12.8 | 49.7 |
| First | High | 216.8 | 75.3 | +12.4 | 54.8 |
| Metropolitan | Low | 60.0 | 78.1 | -157.8 | 170.3 |
| Metropolitan | Base | 144.2 | 187.7 | -48.2 | 192.5 |
| Metropolitan | High | 216.8 | 282.2 | +46.3 | 211.7 |

| Network | Site count | Grid request MW | Present direct allowance $m | Direct sites low / base / high $m | Domestic value low / base / high $m |
|---|---:|---:|---:|---:|---:|
| First | 30 | 151.6 | 240.0 | 159.4 / 240.3 / 334.2 | 32.0 / 81.1 / 150.4 |
| Metropolitan | 100 | 568.4 | 800.0 | 531.4 / 801.0 / 1,114.0 | 106.7 / 270.3 / 501.3 |

<!-- end calculated tables -->

## Electricity contract

The federal Ministry of Electricity schedule reproduced by JICA lists flat industrial and governmental energy charges of 60 and 120 IQD/kWh from January 2018. The low case assumes industrial eligibility and all energy at that rate. The base and high cases assume government billing and buy 5% and 20% of annual energy at a premium. UNDP estimates a 2022 Iraqi private-generator cost of $0.40/kWh. We use that historical price as a proxy for the premium energy volume. The percentages are buyer assumptions about purchases under a second supply agreement. The model holds the historical benchmark prices flat for this comparison and translates IQD at the project rate of 1,510 per dollar. These terms await a utility offer for a railway connection. [Iraqi tariff schedule, table 2](https://openjicareport.jica.go.jp/pdf/12352100.pdf) · [UNDP power-sector study, p. 84](https://www.undp.org/sites/g/files/zskgke326/files/2025-09/energy_transition_in_iraq_english_version_250914_122841.pdf) · [Project currency convention](iraq-market.toml)

The operator pays a retail bill and the public budget may also support the utility. The IMF reports Iraqi electricity operating expenses of nearly IQD 16 trillion against around IQD 2 trillion of collections in 2022. A buyer considering the public cost of a discounted tariff should obtain the utility's incremental supply cost separately. [IMF 2025 Iraq consultation](https://www.elibrary.imf.org/view/journals/002/2025/183/article-A001-en.xml)

The grid requests in the table apply the service model's 1.90 peak factor to purchases during 18 operating hours a day. Ask the distributor for available firm MW by location and season, simultaneous outages on both feeds, restoration time, fault levels, contracted kW and demand charges. For scale, each additional $1/kW-month billed at the full planning request adds about $1.8m/year or $6.8m/year respectively. The scenarios price energy at the meter. Any standby capacity reservation, dedicated generation, reinforcement beyond site limits, tax and connection fee require their own commercial returns. Essential onboard batteries cover separate train safety loads. [Supply and service assumptions](system.toml) · [Electrical duty and scope](COST-AND-DELIVERY.md)

The overhead premium column replaces only the metered electricity expense of each option over 30 years at 4% real, using the respective overhead and conductor losses. It holds construction, renewal and passenger service at the published comparison values. The small advantage still depends on conductor equipment price, utility terms and maintenance. [Supply comparison](system-results.json)

## What each traction supply site buys

| Scope per site | Low $m | Base $m | High $m | Basis |
|---|---:|---:|---:|---|
| Utility-side AC equipment | 0.91 | 1.01 | 1.14 | Two Iraqi utility equipment procurements with price-date allowances |
| Utility feeder termination, on-site building, cable routes, installation and earthing | 1.40 | 2.00 | 3.00 | Planning allowance for access, building and connection complexity |
| Traction rectification and cooling | 1.40 | 2.40 | 3.50 | Converter/transformer equipment and heat rejection |
| DC feeders, negative return and switchgear within site | 0.90 | 1.40 | 2.00 | Protection, isolators and connections up to outgoing site terminals |
| Site auxiliaries and integration | 0.70 | 1.20 | 1.50 | Enclosures, cable assemblies, local controls, factory tests and site integration |
| **Direct cost** | **5.31** | **8.01** | **11.14** | Compare with $8.00m per site in the protected-conductor capital plan |

Twanist lists June 2022 supply of nine 33/11 kV, 31.5 MVA mobile substations for IQD 12.42bn, and January 2023 supply of two 33/11 kV, 2 × 31.5 MVA substations for IQD 2.995bn. Dividing each price by its count gives IQD 1.380bn and 1.4975bn per unit. Low, base and high take the lower, mean and upper prices with assumed price-date adjustments of 0%, 6% and 15%. Both are AC distribution equipment comparators with different ratings and site arrangements from the railway. The four other table lines are engineering allowances. Equipment duty, measured quantities and complete offers could move the price outside this range. [Contractor's completed project register, rows 69 and 93](https://www.twanist.com/imppro) · [Price assumptions](iraq-power.toml)

The network totals replace only the direct grid-site allowance in a comparison. The conductor along the guideway, section switches, central control gateways, system-wide test and assurance, land and project contingency already have separate ledger lines. The matched site quote should define the AC and DC boundaries, utility network reinforcement, installed protection, spares, cooling and commissioning. The grid request divided equally over the planned sites is an arithmetic average. A section study must determine actual feeder ratings, voltage drop, return paths and whether braking power can be received during coincident train movements. [Capital scope](system-results.json)

## Work an Iraqi supplier could undertake

For an indicative domestic value-added range, apply 15% / 30% / 45% to utility-side equipment, 45% / 70% / 80% to local site works and 10% / 20% / 30% to railway plant. The base estimate is **$2.70m per $8.01m site**. Iraq's Ministry of Trade describes Diyala's transformer plants and its use of imported raw and semifinished materials for distribution transformers. Ur General Company's profile lists power cables and winding wire. These capabilities support enquiries for transformer assembly, cable supply, enclosures and installation. The percentage assumptions have no supplier commitment behind them. [Diyala General Company](https://www.iitp.mot.gov.iq/Home/CompanyProfile?AspxAutoDetectCookieSupport=1&Id=32) · [Ur General Company](https://www.iitp.mot.gov.iq/Home/CompanyProfile?AspxAutoDetectCookieSupport=1&Id=276)

Ask each turnkey and open-design bidder to price the same site and mark imported equipment and materials, Iraqi value added, factory testing, local repair rights, spares lead time and training. Count imported input value once and deduct it from the domestic share, including imports purchased through an Iraqi distributor. Show duties, margins and exclusions separately. Test cost and local share independently in negotiations. Whole-network local-contract targets use a different definition from domestic value added at one supply site. [Price inputs](iraq-power.toml) · [Reproduce both network estimates](iraq_power.py)
