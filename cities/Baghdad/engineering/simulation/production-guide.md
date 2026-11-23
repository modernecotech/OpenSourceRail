# Airport workshop, procurement and operating cash

The opening estimate covers 36 powered cars in six sets, 72 bogies, 2,400 beams, 2,402 pier/foundation positions, six station sites and 30 traction source groups. On the published buyer-estimate basis, allow **USD 1,124.32m opening capital and USD 13.09m annual operations** in constant 2026 dollars. At 3.69m assumed paid journeys and USD 0.42 net receipts per passenger, the indicated first-full-year operating support is USD 11.53m or **USD 3.12 per paid journey**. Fares and paid demand remain planning inputs. [Opening buyer estimate](../prototype/sourcing-estimate.json)

## Workshop and site capacity

| Production case | Last set proved, workday | Last beam installed, workday | Last modelled completion, workday | Gross steel bars / sheets |
|---|---:|---:|---:|---:|
| Normal | 449.3 | 498.9 | 498.9 | 819 / 44 |
| Material releases delayed 30 workdays | 490.3 | 528.9 | 528.9 | 819 / 44 |
| Reduced capacity and 75% availability | 772.3 | 938.0 | 938.0 | 819 / 44 |
| Rejected first vehicle article | 501.3 | 498.9 | 501.3 | 853 / 50 |

Time runs in effective workdays. Crews, workcells, fixtures, haul and site installation take separate finite bookings. Beam moulds stay occupied from placement until stressing, demould and reservation of a staging position. Haul releases the yard reservation and carries the beam to a bearing/foundation/erection route. Normal peak staging is two beam positions under the modelled dispatch assumptions. The larger existing factory allowance covers other release, inspection and weather conditions. Both figures require an actual yard and route plan. Each route reports backlog, queue waiting and occupied resource workdays. The crew counts, on-site foundation booking, material pacing and delivery times need contractor returns. Workstations collect the archived production loads by product, and the model groups shared body/package operations conservatively. The article rejection assumes a scrapped fabrication sequence, corrective booking, repeated first-off inspection and serial release after inspection. The model assumes earliest permitted booking for accepted material and completed equipment. [Factory routes and equipment](../prototype/factory-routes.json)

The reference saw patterns yield 88.6% by nominal blank length and the plate layouts yield 81.0% by nested profile area. Gross purchases count each required bar and mixed sheet pattern once, rounded up for each alternative fleet. The pattern estimate covers cuts, tails and remnants within the released stock files. Installed mass, bending, weld procedure, finishing consumables and reusable scrap value need their own manufacturing returns. Hybrid and aluminium options use an explicit steel-pattern analogue for scheduling, material-specific CAM remains open. [CAM stock and profile drawings](../prototype/cam/CAM.md)

## Cash, purchasing and local capability

The reported project cash covers three budget draw years at 20%, 45% and 35%, then 30 full operating years. It discounts annual gross priced cash, including scheduled renewals, at 4% real. The reference priced present value is USD 1,343.38m. Reduced capacity moves the opening assumption from year 4 to year 5. Additional claim, scrap, idle labour and delivery delay prices remain open. The 256 seeded draws correlate source capital/operating price spreads, opening delays and demand stress. The illustrative P10/P50/P90 priced present values are USD 1,289m, USD 1,342m and USD 1,437m. These reflect chosen stress inputs and need calibration from quotations, historical delays and demand counts. [Published opening cash](../prototype/airport-prototype.zip)

The smaller formation splits fixed and car-dependent purchase scope. Wider spans use separate quantity and workload proxies with an explicit hold for revised beams, reinforcement, moulds, lifting and supporting works. The paired six-site case replaces the three radial supply/line lots and recurring feeder upkeep with the published paired-path provision, leaving paired power renewals and the exact upkeep boundary open. Changing the service supplies new train-km, delivered energy and paid journeys. Cases with different offered service require demand, capacity and journey support comparisons alongside the cost figures. [Sourcing lots and alternatives](../prototype/sourcing-estimate.json)

The workshop schedule gives addressable equipment and work by parent lot, including fixtures, workshops, hired plant, contract operations and training. Open-source CAM setup, practice coupons, review and skills transfer have their own price breakdown inside their parent allowances. A workshop quote can replace the corresponding priced scope only after a matched allocation confirms the credit. The buyer needs invoices, production records, local labour costs, imported stock/equipment costs and subcontract declarations to calculate verified Iraqi value. Verified share, funded opening cost, firm installed prices, tax and duties, and physical acceptance remain open. [Shop price breakdown and overlap controls](../prototype/shop-costs.json)

Generate the receipt from the repository root. It includes input file digests, workcell and stock scenarios, lot quantities, comparable planning amounts, scope holds and a deterministic evaluation ID.

```sh
python3 -m cities.Baghdad.engineering.simulation.production > build/airport-production.json
python3 -m unittest cities.Baghdad.engineering.simulation.production_test
```
