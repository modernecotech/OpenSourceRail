# Kakamega civil soil screening

630 route/station sample locations; 630 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 630 |
| fine-soil-plasticity-and-shrink-swell-tests | 630 |
| granular-density-and-groundwater-tests | 41 |
| organic-content-and-compressibility-tests | 1 |

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
| 0..30cm | clay | % | 32–46 | 13–54 | 630 |
| 0..30cm | sand | % | 24–48 | 11–81 | 630 |
| 0..30cm | silt | % | 20–31 | 2–42 | 630 |
| 0..30cm | bd.core | kg/m3 | 1100–1220 | 850–1440 | 630 |
| 0..30cm | soc | g/kg | 8.7–27.3 | 3.6–53.9 | 630 |
| 0..30cm | ph.h2o | pH | 5.2–5.7 | 5–6.1 | 630 |
| 30..60cm | clay | % | 33–47 | 17–56 | 630 |
| 30..60cm | sand | % | 23–46 | 9–79 | 630 |
| 30..60cm | silt | % | 21–31 | 4–44 | 630 |
| 30..60cm | bd.core | kg/m3 | 1140–1270 | 890–1460 | 630 |
| 30..60cm | soc | g/kg | 6.3–13.3 | 2.8–22.8 | 630 |
| 30..60cm | ph.h2o | pH | 5.2–5.8 | 4.9–6.2 | 630 |
| 60..100cm | clay | % | 33–47 | 16–57 | 630 |
| 60..100cm | sand | % | 23–46 | 8–81 | 630 |
| 60..100cm | silt | % | 21–31 | 1–44 | 630 |
| 60..100cm | bd.core | kg/m3 | 1150–1290 | 940–1520 | 630 |
| 60..100cm | soc | g/kg | 5.7–8.7 | 2.1–15.2 | 630 |
| 60..100cm | ph.h2o | pH | 5.3–5.8 | 4.9–6.3 | 630 |
