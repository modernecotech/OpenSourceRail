# Kumba civil soil screening

108 route/station sample locations; 108 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 108 |
| fine-soil-plasticity-and-shrink-swell-tests | 84 |
| granular-density-and-groundwater-tests | 107 |
| organic-content-and-compressibility-tests | 19 |

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
| 0..30cm | clay | % | 18–34 | 8–53 | 108 |
| 0..30cm | sand | % | 39–69 | 3–85 | 108 |
| 0..30cm | silt | % | 13–28 | 0–45 | 108 |
| 0..30cm | bd.core | kg/m3 | 980–1100 | 680–1380 | 108 |
| 0..30cm | soc | g/kg | 9.7–40.8 | 3.4–81.7 | 108 |
| 0..30cm | ph.h2o | pH | 5.5–5.8 | 4.8–6.4 | 108 |
| 30..60cm | clay | % | 20–36 | 10–54 | 108 |
| 30..60cm | sand | % | 37–64 | 3–80 | 108 |
| 30..60cm | silt | % | 16–30 | 2–47 | 108 |
| 30..60cm | bd.core | kg/m3 | 1030–1160 | 750–1490 | 108 |
| 30..60cm | soc | g/kg | 5.7–20.1 | 2.7–43 | 108 |
| 30..60cm | ph.h2o | pH | 5.5–5.8 | 4.9–6.4 | 108 |
| 60..100cm | clay | % | 21–37 | 12–55 | 108 |
| 60..100cm | sand | % | 34–63 | 1–79 | 108 |
| 60..100cm | silt | % | 16–29 | 2–46 | 108 |
| 60..100cm | bd.core | kg/m3 | 1070–1220 | 760–1530 | 108 |
| 60..100cm | soc | g/kg | 5.6–12.4 | 2.4–27.7 | 108 |
| 60..100cm | ph.h2o | pH | 5.6–5.9 | 4.8–6.5 | 108 |
