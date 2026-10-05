# Khulna civil soil screening

1,261 route/station sample locations; 1,239 complete profiles; 22 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1239 |
| coverage-gap | 22 |
| fine-soil-plasticity-and-shrink-swell-tests | 1239 |
| granular-density-and-groundwater-tests | 1239 |
| organic-content-and-compressibility-tests | 628 |
| silt-moisture-frost-and-erosion-review | 1 |

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
| 0..30cm | clay | % | 18–29 | 4–46 | 1239 |
| 0..30cm | sand | % | 42–63 | 8–89 | 1239 |
| 0..30cm | silt | % | 19–30 | 2–50 | 1239 |
| 0..30cm | bd.core | kg/m3 | 780–1130 | 400–1500 | 1239 |
| 0..30cm | soc | g/kg | 10.6–46.2 | 3.6–151.2 | 1239 |
| 0..30cm | ph.h2o | pH | 5.9–6.6 | 4.7–7.9 | 1239 |
| 30..60cm | clay | % | 19–30 | 2–47 | 1239 |
| 30..60cm | sand | % | 40–62 | 6–90 | 1239 |
| 30..60cm | silt | % | 18–32 | 3–49 | 1239 |
| 30..60cm | bd.core | kg/m3 | 870–1190 | 530–1560 | 1239 |
| 30..60cm | soc | g/kg | 6.4–28.5 | 1.2–106.5 | 1239 |
| 30..60cm | ph.h2o | pH | 6.2–6.8 | 4.9–8 | 1239 |
| 60..100cm | clay | % | 21–30 | 2–48 | 1239 |
| 60..100cm | sand | % | 39–59 | 5–91 | 1239 |
| 60..100cm | silt | % | 19–32 | 3–49 | 1239 |
| 60..100cm | bd.core | kg/m3 | 910–1190 | 540–1730 | 1239 |
| 60..100cm | soc | g/kg | 4.8–18.2 | 1.3–83.3 | 1239 |
| 60..100cm | ph.h2o | pH | 6.3–7.1 | 4.9–8.2 | 1239 |
