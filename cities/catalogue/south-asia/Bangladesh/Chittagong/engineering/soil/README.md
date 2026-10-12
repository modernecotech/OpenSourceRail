# Chittagong civil soil screening

9,526 route/station sample locations; 9,498 complete profiles; 28 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 9498 |
| coverage-gap | 28 |
| fine-soil-plasticity-and-shrink-swell-tests | 9498 |
| granular-density-and-groundwater-tests | 8176 |
| organic-content-and-compressibility-tests | 2937 |
| silt-moisture-frost-and-erosion-review | 397 |

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
| 0..30cm | clay | % | 22–34 | 6–51 | 9498 |
| 0..30cm | sand | % | 35–58 | 6–83 | 9498 |
| 0..30cm | silt | % | 21–33 | 4–51 | 9498 |
| 0..30cm | bd.core | kg/m3 | 670–1190 | 330–1580 | 9498 |
| 0..30cm | soc | g/kg | 7.7–49.6 | 1.7–152.2 | 9498 |
| 0..30cm | ph.h2o | pH | 5.6–6.3 | 4.4–7.9 | 9498 |
| 30..60cm | clay | % | 22–35 | 4–50 | 9498 |
| 30..60cm | sand | % | 33–56 | 0–85 | 9498 |
| 30..60cm | silt | % | 22–33 | 3–56 | 9498 |
| 30..60cm | bd.core | kg/m3 | 800–1230 | 290–1600 | 9498 |
| 30..60cm | soc | g/kg | 5–33.8 | 0.8–135.8 | 9498 |
| 30..60cm | ph.h2o | pH | 5.9–6.7 | 4.7–8 | 9498 |
| 60..100cm | clay | % | 22–35 | 5–51 | 9498 |
| 60..100cm | sand | % | 34–55 | 1–86 | 9498 |
| 60..100cm | silt | % | 22–34 | 3–56 | 9498 |
| 60..100cm | bd.core | kg/m3 | 810–1250 | 180–1610 | 9498 |
| 60..100cm | soc | g/kg | 4.3–25.2 | 0.7–284.7 | 9498 |
| 60..100cm | ph.h2o | pH | 6–6.9 | 4.6–8.3 | 9498 |
