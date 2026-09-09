# Maputo civil soil screening

397 route/station sample locations; 397 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 396 |
| fine-soil-plasticity-and-shrink-swell-tests | 369 |
| granular-density-and-groundwater-tests | 397 |

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
| 0..30cm | clay | % | 17–31 | 3–47 | 397 |
| 0..30cm | sand | % | 45–73 | 19–96 | 397 |
| 0..30cm | silt | % | 10–24 | 0–39 | 397 |
| 0..30cm | bd.core | kg/m3 | 1070–1380 | 810–1580 | 397 |
| 0..30cm | soc | g/kg | 5.1–23.6 | 2.2–48.8 | 397 |
| 0..30cm | ph.h2o | pH | 6–7 | 5–8.3 | 397 |
| 30..60cm | clay | % | 19–33 | 3–48 | 397 |
| 30..60cm | sand | % | 45–72 | 18–96 | 397 |
| 30..60cm | silt | % | 8–22 | 0–40 | 397 |
| 30..60cm | bd.core | kg/m3 | 1080–1500 | 810–1680 | 397 |
| 30..60cm | soc | g/kg | 3.3–15.3 | 1.6–34.5 | 397 |
| 30..60cm | ph.h2o | pH | 6.2–7.1 | 5–8.2 | 397 |
| 60..100cm | clay | % | 19–33 | 3–48 | 397 |
| 60..100cm | sand | % | 46–72 | 14–96 | 397 |
| 60..100cm | silt | % | 7–21 | 0–42 | 397 |
| 60..100cm | bd.core | kg/m3 | 1050–1530 | 740–1750 | 397 |
| 60..100cm | soc | g/kg | 2.3–11.9 | 0.9–29.1 | 397 |
| 60..100cm | ph.h2o | pH | 6.2–7.1 | 4.6–8.4 | 397 |
