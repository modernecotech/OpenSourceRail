# Dakar civil soil screening

404 route/station sample locations; 336 complete profiles; 68 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 336 |
| coverage-gap | 68 |
| granular-density-and-groundwater-tests | 336 |

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
| 0..30cm | clay | % | 6–15 | 0–29 | 336 |
| 0..30cm | sand | % | 61–80 | 30–92 | 336 |
| 0..30cm | silt | % | 12–26 | 5–41 | 336 |
| 0..30cm | bd.core | kg/m3 | 1290–1500 | 970–1690 | 336 |
| 0..30cm | soc | g/kg | 3.2–8.7 | 1–22.9 | 336 |
| 0..30cm | ph.h2o | pH | 5.7–6.6 | 3.2–8.2 | 336 |
| 30..60cm | clay | % | 6–15 | 0–34 | 336 |
| 30..60cm | sand | % | 62–82 | 31–92 | 336 |
| 30..60cm | silt | % | 11–25 | 4–41 | 336 |
| 30..60cm | bd.core | kg/m3 | 1240–1500 | 990–1730 | 336 |
| 30..60cm | soc | g/kg | 2.8–6.2 | 0.5–40.9 | 336 |
| 30..60cm | ph.h2o | pH | 5.2–6.6 | 3.3–8.4 | 336 |
| 60..100cm | clay | % | 6–15 | 0–33 | 336 |
| 60..100cm | sand | % | 62–83 | 31–92 | 336 |
| 60..100cm | silt | % | 11–23 | 4–40 | 336 |
| 60..100cm | bd.core | kg/m3 | 1170–1530 | 740–1780 | 336 |
| 60..100cm | soc | g/kg | 2–5.7 | 0.5–29.4 | 336 |
| 60..100cm | ph.h2o | pH | 5.5–6.8 | 3.6–8.3 | 336 |
