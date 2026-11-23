# OpenSourceRail v0.7.2 · Baghdad opening integration

The Airport operating option connects six stops over 12 km of elevated double track. Three working six-car sets provide four departures an hour in each direction. Three spares cover the workshop, inspection and recovery allowances. At 700 normal places per train, the offer is 2,800 places an hour in each direction. The daily diagram includes 144 passenger trips, two empty positioning trips and the depot shunts. The original 21-set Airport proposal remains available for comparison. [Original Airport opening budget](../../../cities/Baghdad/AIRPORT-OPENING.md)

The same workings drive the feeder calculation. A pair of accelerating trains can draw more than 10 MW. The existing three-site, 1.5 kV midpoint trial falls to 1.023 kV on one feed with two trains. A radial option carries the same conductor resistance through 30 supply sites, 116 outgoing circuits and 58 midpoint ties. With 10% additional source and circuit resistance, the most demanding two-train outage gives 1.350925 kV. The margin above the 1.35 kV planning floor is 0.93 V. A six-site alternative requires lower source and circuit resistance. Its installed price awaits a supplier return. [Traction supply single-line diagram](../../../cities/Baghdad/airport-traction-single-line.svg) · [Feeder evaluator](../../../cities/Baghdad/airport_supply.py)

The central planning case budgets **$1,122.8m** of construction and **$13.08m** of annual operations in 2026 USD. The estimate prices each of the 58 normally open ties at the existing $50,000 section-equipment allowance, adding $2.90m in direct cost. Annual upkeep on the additional sites and switchgear uses 1% of their direct equipment allowance in the central case, with a 0.5–2% sensitivity. At the retained demand assumption of 10,121 paid journeys per day, $1.56m of annual net fares leaves **$11.52m** of annual operating support, or $3.12 per paid journey, before renewals and financing. The full-life priced scope is $1,470.6m in 30-year present value. The urban comparator needs its own demand counts and site-specific power design. [Airport operating plan and cost scenarios](../../../cities/Baghdad/airport-integration.html)

The [supplier dossier](../../../cities/Baghdad/airport-dossier.zip) joins the train workings, controlled equipment quantities, brake and power demands, civil quantities, preliminary investment, maintenance and phased cash flows. Quote returns identify the design and the scope they replace. A complete supplier weight return updates the train load used for traction, the wheel and civil load calculations, and the electricity allowance per train-kilometre. The published case uses the planning mass until those weights are available. The separate bench procedure calls for witnessed measurements at the doors, brake and drive. [Assembly calculations](../../../cities/Baghdad/airport_assembly.py) · [Station bench procedure](../../../cities/Baghdad/engineering/controls/STATION-BENCH.md)

The separate seven-line first-programme scenario stages openings in 2029, 2030 and 2031. It reaches 24.67 million annual train-kilometres in 2032 and mature fare revenue in 2033 under its assumed demand ramp. [Phased service and funding](../../operator-review/finance/phased-first.html)

## Run the compact source installation

The Airport source archive runs on Linux with Bash, Git and Python 3.11 or later. Extract it in an empty directory, enter the source folder, then run the following commands. The first calculation checks the published Airport opening. The second writes the supplier dossier. The last two commands reproduce the synthetic 30 km design and the separate seven-line financing scenario.

```sh
python3 -m venv --without-pip .venv
./osr design railway airport --check
./osr design railway airport --packet build/airport-supplier.zip
./osr reference v07
.venv/bin/python -m cities.Baghdad.phased_finance --check
```

From the full repository, run `python3 tools/automation/check-airport-install.py` to export the checked-out commit to a small source archive and exercise these commands in a fresh installation. The verifier records the commit, archive and dossier checksums under the ignored build directory. [Release series and evidence](../../RELEASE-v0.7.md)

## Work before a prototype or passenger opening

The opening budget depends on assumed ridership, Iraqi planning rates and available parcels. Passenger counts, independently weighed assemblies, hot circuit measurements, fault protection, approved site layouts and supplier prices remain open. v0.8 production preparation needs reviewed mating dimensions and tolerances, joint inspection plans, drawings for fabrication and lifting, and authenticated first-article evidence. The opening date, total funded capital and authority to operate require separate owner decisions.
