# Vientiane civil soil screening

174 route/station sample locations; 171 complete profiles; 3 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 171 |
| coverage-gap | 3 |
| fine-soil-plasticity-and-shrink-swell-tests | 171 |
| granular-density-and-groundwater-tests | 105 |
| silt-moisture-frost-and-erosion-review | 91 |

- No bearing capacity, CBR, friction angle, cohesion, groundwater, contamination, sulfate/chloride or deep stratigraphy is inferred from these maps.
- Desert, water, urban fill and other nodata remain unknown; no nearest-pixel or climate-based substitution.
- Texture fractions are independent predictions; they are not renormalised or converted to a geotechnical soil class.
- Prioritisation thresholds are editable OSR screening rules, not statutory limits or evidence of a hazard.
- No excavation depths, foundation dimensions, treatment quantities or civil costs are changed from pedological predictions.

Source: [OpenLandMap soilDB](https://github.com/openlandmap/soildb), Hengl et al., DOI 10.5194/essd-2025-336, CC BY 4.0. Exact source revision, URLs and raster metadata are retained in the receipt.

## Sampled property ranges

Ranges below span the sampled locations; they are not a city-wide characteristic soil value. The uncertainty envelope spans the lowest p16 to highest p84.

| Depth | Property | Unit | Mean range | Uncertainty envelope | Available locations |
|---|---|---|---:|---:|---:|
| 0..30cm | clay | % | 21–30 | 7–43 | 171 |
| 0..30cm | sand | % | 33–53 | 6–84 | 171 |
| 0..30cm | silt | % | 26–37 | 8–53 | 171 |
| 0..30cm | bd.core | kg/m3 | 1080–1390 | 870–1590 | 171 |
| 0..30cm | soc | g/kg | 5.8–13.7 | 3.1–30.5 | 171 |
| 0..30cm | ph.h2o | pH | 5.8–6.2 | 4.8–7.6 | 171 |
| 30..60cm | clay | % | 22–32 | 7–43 | 171 |
| 30..60cm | sand | % | 32–51 | 5–87 | 171 |
| 30..60cm | silt | % | 26–37 | 8–55 | 171 |
| 30..60cm | bd.core | kg/m3 | 1150–1440 | 880–1680 | 171 |
| 30..60cm | soc | g/kg | 3.8–8.2 | 1.7–20.6 | 171 |
| 30..60cm | ph.h2o | pH | 5.9–6.3 | 4.9–7.9 | 171 |
| 60..100cm | clay | % | 23–32 | 6–44 | 171 |
| 60..100cm | sand | % | 31–51 | 5–86 | 171 |
| 60..100cm | silt | % | 26–37 | 7–56 | 171 |
| 60..100cm | bd.core | kg/m3 | 1210–1430 | 830–1690 | 171 |
| 60..100cm | soc | g/kg | 2.6–6.3 | 1–18.3 | 171 |
| 60..100cm | ph.h2o | pH | 6.1–6.5 | 4.8–8.1 | 171 |
