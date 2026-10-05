# Chittagong civil soil screening

2,580 route/station sample locations; 2,570 complete profiles; 10 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 2570 |
| coverage-gap | 10 |
| fine-soil-plasticity-and-shrink-swell-tests | 2570 |
| granular-density-and-groundwater-tests | 2164 |
| organic-content-and-compressibility-tests | 1073 |
| silt-moisture-frost-and-erosion-review | 156 |

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
| 0..30cm | clay | % | 24–34 | 9–49 | 2570 |
| 0..30cm | sand | % | 35–52 | 6–83 | 2570 |
| 0..30cm | silt | % | 23–32 | 5–51 | 2570 |
| 0..30cm | bd.core | kg/m3 | 670–1110 | 330–1500 | 2570 |
| 0..30cm | soc | g/kg | 7.7–48.1 | 2–139.3 | 2570 |
| 0..30cm | ph.h2o | pH | 5.7–6.3 | 4.4–7.9 | 2570 |
| 30..60cm | clay | % | 24–35 | 6–50 | 2570 |
| 30..60cm | sand | % | 33–52 | 1–85 | 2570 |
| 30..60cm | silt | % | 23–34 | 3–54 | 2570 |
| 30..60cm | bd.core | kg/m3 | 800–1180 | 390–1600 | 2570 |
| 30..60cm | soc | g/kg | 5.3–33.8 | 0.8–104.6 | 2570 |
| 30..60cm | ph.h2o | pH | 5.9–6.7 | 4.8–8 | 2570 |
| 60..100cm | clay | % | 24–35 | 5–51 | 2570 |
| 60..100cm | sand | % | 34–51 | 2–85 | 2570 |
| 60..100cm | silt | % | 23–34 | 3–54 | 2570 |
| 60..100cm | bd.core | kg/m3 | 820–1190 | 190–1600 | 2570 |
| 60..100cm | soc | g/kg | 4.7–24.3 | 0.9–205.4 | 2570 |
| 60..100cm | ph.h2o | pH | 6–6.9 | 4.7–8.1 | 2570 |
