# Pokhara civil soil screening

1,045 route/station sample locations; 1,045 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1045 |
| fine-soil-plasticity-and-shrink-swell-tests | 630 |
| granular-density-and-groundwater-tests | 848 |

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
| 0..30cm | clay | % | 16–26 | 6–40 | 1045 |
| 0..30cm | sand | % | 43–60 | 18–80 | 1045 |
| 0..30cm | silt | % | 23–31 | 9–48 | 1045 |
| 0..30cm | bd.core | kg/m3 | 890–1190 | 590–1540 | 1045 |
| 0..30cm | soc | g/kg | 10.2–17 | 3.1–43.8 | 1045 |
| 0..30cm | ph.h2o | pH | 5.4–5.8 | 4.6–6.9 | 1045 |
| 30..60cm | clay | % | 15–26 | 6–39 | 1045 |
| 30..60cm | sand | % | 44–63 | 17–83 | 1045 |
| 30..60cm | silt | % | 22–31 | 9–49 | 1045 |
| 30..60cm | bd.core | kg/m3 | 990–1240 | 680–1600 | 1045 |
| 30..60cm | soc | g/kg | 4.4–10.7 | 1.6–31.3 | 1045 |
| 30..60cm | ph.h2o | pH | 5.5–5.9 | 4.7–7 | 1045 |
| 60..100cm | clay | % | 15–27 | 6–41 | 1045 |
| 60..100cm | sand | % | 44–63 | 19–83 | 1045 |
| 60..100cm | silt | % | 21–31 | 6–48 | 1045 |
| 60..100cm | bd.core | kg/m3 | 1030–1280 | 640–1600 | 1045 |
| 60..100cm | soc | g/kg | 2.7–8.4 | 0.8–26.4 | 1045 |
| 60..100cm | ph.h2o | pH | 5.5–6 | 4.7–7.2 | 1045 |
