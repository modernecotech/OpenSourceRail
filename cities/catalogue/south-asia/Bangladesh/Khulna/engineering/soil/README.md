# Khulna civil soil screening

3,520 route/station sample locations; 3,500 complete profiles; 20 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 3499 |
| coverage-gap | 20 |
| fine-soil-plasticity-and-shrink-swell-tests | 3500 |
| granular-density-and-groundwater-tests | 3500 |
| organic-content-and-compressibility-tests | 1399 |
| silt-moisture-frost-and-erosion-review | 10 |

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
| 0..30cm | clay | % | 18–30 | 4–46 | 3500 |
| 0..30cm | sand | % | 39–66 | 8–89 | 3500 |
| 0..30cm | silt | % | 17–31 | 2–50 | 3500 |
| 0..30cm | bd.core | kg/m3 | 770–1180 | 400–1540 | 3500 |
| 0..30cm | soc | g/kg | 8.4–43.8 | 3–181.6 | 3500 |
| 0..30cm | ph.h2o | pH | 5.9–6.8 | 4.7–8 | 3500 |
| 30..60cm | clay | % | 19–30 | 2–47 | 3500 |
| 30..60cm | sand | % | 40–65 | 6–90 | 3500 |
| 30..60cm | silt | % | 16–31 | 2–49 | 3500 |
| 30..60cm | bd.core | kg/m3 | 810–1210 | 510–1560 | 3500 |
| 30..60cm | soc | g/kg | 5.8–28.3 | 1.2–106.5 | 3500 |
| 30..60cm | ph.h2o | pH | 6.2–6.9 | 4.9–8 | 3500 |
| 60..100cm | clay | % | 20–30 | 2–48 | 3500 |
| 60..100cm | sand | % | 40–62 | 5–91 | 3500 |
| 60..100cm | silt | % | 18–31 | 2–49 | 3500 |
| 60..100cm | bd.core | kg/m3 | 890–1210 | 530–1730 | 3500 |
| 60..100cm | soc | g/kg | 4.8–18 | 1.2–83.3 | 3500 |
| 60..100cm | ph.h2o | pH | 6.2–7.1 | 4.9–8.2 | 3500 |
