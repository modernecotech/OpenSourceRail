# Chittagong civil soil screening

1,947 route/station sample locations; 1,917 complete profiles; 30 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1917 |
| coverage-gap | 30 |
| fine-soil-plasticity-and-shrink-swell-tests | 1917 |
| granular-density-and-groundwater-tests | 1588 |
| organic-content-and-compressibility-tests | 813 |
| silt-moisture-frost-and-erosion-review | 109 |

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
| 0..30cm | clay | % | 24–35 | 9–50 | 1917 |
| 0..30cm | sand | % | 35–54 | 7–84 | 1917 |
| 0..30cm | silt | % | 22–32 | 5–51 | 1917 |
| 0..30cm | bd.core | kg/m3 | 670–1070 | 330–1460 | 1917 |
| 0..30cm | soc | g/kg | 7.9–48.1 | 1.9–139.3 | 1917 |
| 0..30cm | ph.h2o | pH | 5.7–6.3 | 4.4–7.9 | 1917 |
| 30..60cm | clay | % | 24–35 | 7–50 | 1917 |
| 30..60cm | sand | % | 34–53 | 1–84 | 1917 |
| 30..60cm | silt | % | 23–33 | 4–53 | 1917 |
| 30..60cm | bd.core | kg/m3 | 830–1130 | 320–1510 | 1917 |
| 30..60cm | soc | g/kg | 5.3–33.8 | 0.9–133.1 | 1917 |
| 30..60cm | ph.h2o | pH | 5.9–6.6 | 4.7–8 | 1917 |
| 60..100cm | clay | % | 25–35 | 7–51 | 1917 |
| 60..100cm | sand | % | 34–51 | 2–84 | 1917 |
| 60..100cm | silt | % | 23–33 | 4–52 | 1917 |
| 60..100cm | bd.core | kg/m3 | 830–1150 | 180–1560 | 1917 |
| 60..100cm | soc | g/kg | 4.8–24.3 | 1–205.4 | 1917 |
| 60..100cm | ph.h2o | pH | 6–6.8 | 4.6–8.1 | 1917 |
