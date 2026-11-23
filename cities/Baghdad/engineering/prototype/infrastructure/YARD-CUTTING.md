# Ordering and cutting stock for one beam cage

A yard can quote all 280 conventional reinforcing blanks in the Airport beam from nine drawing marks. For one cage, the trial layout consumes 103 twelve-metre bars or 88 fourteen-metre bars. For 2,400 identical separately kitted beams these counts become 247,200 or 211,200 stock bars. The longer bar saves four metres of purchased length per beam. Ask for delivered prices at both lengths and confirm that the yard can receive and handle them. [Issued beam drawing and schedule](../civil-guide.md)

| Trial stock | Purchased length per beam | Developed blanks rounded up to the millimetre | End and cut allowance | Remaining offcuts |
|---|---:|---:|---:|---:|
| 12 m | 1,236 m | 1,168.272 m | 2.900 m | 64.828 m |
| 14 m | 1,232 m | 1,168.272 m | 2.600 m | 61.128 m |

The calculation assumes compatible stock of one grade for the 12 mm bars, 20 mm combined end trim on each length and 3 mm lost per blank. The shop should substitute measured allowances for its shear or saw. It places the longest blanks first and uses the first available length that fits. It preserves each mark, makes no splices, carries no offcut between beams and credits no scrap revenue. A fabricator may return a more efficient verified layout. The supply cost for either option is its stock count times the delivered price per bar, plus separately quoted handling and fabrication. This replaces the corresponding cage scope in a beam quotation.

## Prepare the yard enquiry

1. Extract the buyer issue. Open `infrastructure/stock-cases.json` for both layouts and `infrastructure/bar-cut-tags.csv` for the cut sequence. Filter the tags by **one** stock length. Each pattern applies to its indicated number of stock bars per beam. The repeated offcut column describes the remainder after the whole pattern.
2. Reconcile the number of cut pieces of every mark to `drawings/beam-bar-strand-schedule.csv`. Use `drawings/beam-cage-section.svg` and the civil article to distinguish the two U-bar hands and their positions. The rounded-up stock estimate leaves final dimensions, bend compensation, mandrel and tolerances to the approved schedule and first-off inspection.
3. Return the grade, mill certificate, available lengths, delivered rate, cutting and bending time, setup, handling capacity and offcut disposition. Before cutting, assign a beam serial, material specification and heat to each stock batch. Tag the cut bundles and carry the inspection and heat references through to cage assembly. [CRSI bar tag examples](https://www.crsi.org/reinforcing-basics/reinforcing-steel/bar-tags/)
4. Price the prestressing strand separately. Each beam embeds 120 m. The extra strand for stressing beds, anchor tails and dummy lengths needs the proposed bed layout. End zones, transfer strength and lifting remain with the engineer and yard before a production issue.

From the repository root, run a different supplier scenario with the same candidate and drawing revision. An undersized stock bar produces an error naming the mark which it cannot furnish.

```sh
python3 -m cities.Baghdad.engineering.prototype.infrastructure.bar_stock --stock-mm 12000 --cut-loss-mm 3 --end-trim-mm 20
```
