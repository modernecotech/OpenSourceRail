# Baghdad Airport GIS simulation and cost estimate

The 17.46 km desktop study carries public elevation, soil texture and historical surface-water data through the alignment, train and feeder replay, civil quantities and 30-year cash estimate. All costs are planning estimates in constant 2026 USD.

## Terrain and rail profile

The 879 route samples span 30.43 to 51.07 m in the DEM. The model places the rail above that surface and keeps the platform intervals level. The maximum simulated grade is 0.600%. The soffit is 6.00 to 23.10 m above the sampled surface.

The DEM is a surface model, so structures can affect sampled heights. Soil texture guides scenario allowances for foundation treatment. Historical water occurrence screens surface-water exposure. Bearing strength, groundwater and design flood levels remain assumptions in this model.

The soil grid returns a shallow clay estimate at 330 of the 879 samples. Historical water data cover 879 samples.

| Stop | Chainage km | Rail elevation m |
|---|---:|---:|
| Baghdad Airport terminal | 0.000 | 59.07 |
| Al Amiriya | 7.449 | 47.23 |
| Hay Al Aamil | 13.016 | 44.81 |
| Al Bayaa | 14.962 | 47.42 |
| Um Al Tubol | 16.212 | 46.46 |
| Al Qadisiya | 17.461 | 47.27 |

## Train and power replay

The declared service runs every 30 minutes with 35 s dwell. The demand model projects 2,647,702 requested journeys per year under the study assumptions.

| Supply | Duty | Completed / booked trips | Lowest live collector V |
|---|---|---:|---:|
| radial30 | normal | 72 / 72 | 1,485.5 |
| radial30 | hot | 72 / 72 | 1,484.0 |
| radial30 | site_out | 72 / 72 | 1,484.0 |
| radial30 | path_out | 0 / 72 | 1,489.8 |
| radial30 | combined | 0 / 72 | 1,473.6 |
| paired6 | normal | 72 / 72 | 1,492.3 |
| paired6 | hot | 72 / 72 | 1,491.7 |
| paired6 | site_out | 72 / 72 | 1,487.8 |
| paired6 | path_out | 72 / 72 | 1,491.4 |
| paired6 | combined | 72 / 72 | 1,471.2 |

| Supply | Failed integrated screens | Inputs still open in the model |
|---|---|---|
| radial30 | timetable, aged battery, traction adhesion, one-driven-axle-out required force | returned equipment, battery continuous hot power, battery brake and egress peak duty, protected stopping distance, installed door and suspension clearances |
| paired6 | aged battery, traction adhesion, one-driven-axle-out required force | returned equipment, battery continuous hot power, battery brake and egress peak duty, protected stopping distance, installed door and suspension clearances |

## What the site layers change

The 20m U 1.55m / shared trial prices 1,748 placements across 875 supports. Trial column heights range from 4.75 to 21.85 m. Columns above standard stock add 3,909 m³ of concrete. The foundation scenarios vary the bearing pressure, bore length and amount of ground treatment.

| Bearing assumption | Standard pad failures | Enlarged pads | Shaft allowance |
|---|---:|---:|---:|
| low · 250 kPa | 76 | 76 | 9 supports |
| base · 200 kPa | 421 | 406 | 35 supports |
| high · 150 kPa | 875 | 787 | 88 supports |

| Additional priced site scope | Low USD m | Base USD m | High USD m |
|---|---:|---:|---:|
| gis-pier-height | 0.67 | 0.97 | 1.56 |
| gis-shallow-footing | 0.11 | 1.56 | 21.56 |
| gis-foundation-allowance | 0.08 | 0.62 | 2.81 |
| gis-end-closure-allowance | 0.07 | 0.11 | 0.18 |

## Simulated purchaser cash

| Layout | Price case | Capital USD m | Annual operation USD m | 30-year present cost USD m |
|---|---|---:|---:|---:|
| radial30 | low | 910.23 | 9.44 | 1,068.27 |
| radial30 | base | 1,041.75 | 11.43 | 1,222.00 |
| radial30 | high | 1,334.71 | 14.93 | 1,552.41 |
| paired6 | low | 703.44 | 8.71 | 820.98 |
| paired6 | base | 863.94 | 10.34 | 1,001.18 |
| paired6 | high | 1,179.86 | 13.73 | 1,357.80 |

Compare the priced layouts against the replayed outage service above. The capital and cash totals include modelled equipment and site allowances. The record lists each lot, its estimate basis, any remaining scope exclusions and the annual cash flows.

The decision record preserves the test conditions, rate sources and candidate identities.

[Inputs and evaluation instructions](GIS-SIMULATION-GUIDE.md) · [Route map](site-study.geojson) · [Route samples](site-study-profile.csv) · [Cost and decision record](site-study.json)

Evaluation `8a04542fd45e6c158954385ab7427e62a466dd30b7c8223685909de608adce2b`.
