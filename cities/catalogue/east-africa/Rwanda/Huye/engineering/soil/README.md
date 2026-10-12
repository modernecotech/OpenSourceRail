# Huye civil soil screening

1,003 route/station sample locations; 1,003 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1003 |
| fine-soil-plasticity-and-shrink-swell-tests | 1003 |
| granular-density-and-groundwater-tests | 35 |
| organic-content-and-compressibility-tests | 4 |

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
| 0..30cm | clay | % | 27–38 | 16–46 | 1003 |
| 0..30cm | sand | % | 32–50 | 16–77 | 1003 |
| 0..30cm | silt | % | 22–31 | 8–43 | 1003 |
| 0..30cm | bd.core | kg/m3 | 1170–1320 | 930–1500 | 1003 |
| 0..30cm | soc | g/kg | 11.6–22.2 | 7.3–38.1 | 1003 |
| 0..30cm | ph.h2o | pH | 5.4–5.9 | 4.7–6.8 | 1003 |
| 30..60cm | clay | % | 28–39 | 16–49 | 1003 |
| 30..60cm | sand | % | 33–51 | 16–77 | 1003 |
| 30..60cm | silt | % | 21–30 | 5–45 | 1003 |
| 30..60cm | bd.core | kg/m3 | 1250–1360 | 1010–1550 | 1003 |
| 30..60cm | soc | g/kg | 6.7–12.5 | 3–34.3 | 1003 |
| 30..60cm | ph.h2o | pH | 5.8–6.2 | 5–7.3 | 1003 |
| 60..100cm | clay | % | 29–39 | 15–49 | 1003 |
| 60..100cm | sand | % | 33–51 | 15–75 | 1003 |
| 60..100cm | silt | % | 20–30 | 5–44 | 1003 |
| 60..100cm | bd.core | kg/m3 | 1260–1360 | 970–1590 | 1003 |
| 60..100cm | soc | g/kg | 5–15 | 2–58 | 1003 |
| 60..100cm | ph.h2o | pH | 6.2–6.6 | 5–8.2 | 1003 |
