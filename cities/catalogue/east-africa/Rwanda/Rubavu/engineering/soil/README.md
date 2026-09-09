# Rubavu civil soil screening

174 route/station sample locations; 172 complete profiles; 2 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 48 |
| coverage-gap | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 172 |
| granular-density-and-groundwater-tests | 106 |
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
| 0..30cm | clay | % | 28–36 | 14–48 | 172 |
| 0..30cm | sand | % | 36–54 | 17–76 | 172 |
| 0..30cm | silt | % | 17–28 | 3–45 | 172 |
| 0..30cm | bd.core | kg/m3 | 1010–1190 | 720–1390 | 172 |
| 0..30cm | soc | g/kg | 11.8–41.2 | 5.1–80.2 | 172 |
| 0..30cm | ph.h2o | pH | 5.9–6.8 | 5.1–7.5 | 172 |
| 30..60cm | clay | % | 30–39 | 12–53 | 172 |
| 30..60cm | sand | % | 36–51 | 11–75 | 172 |
| 30..60cm | silt | % | 18–26 | 1–42 | 172 |
| 30..60cm | bd.core | kg/m3 | 1040–1190 | 740–1400 | 172 |
| 30..60cm | soc | g/kg | 7.8–17.8 | 2.4–33.4 | 172 |
| 30..60cm | ph.h2o | pH | 5.9–6.7 | 5.2–7.7 | 172 |
| 60..100cm | clay | % | 31–40 | 12–55 | 172 |
| 60..100cm | sand | % | 34–50 | 11–76 | 172 |
| 60..100cm | silt | % | 19–26 | 0–43 | 172 |
| 60..100cm | bd.core | kg/m3 | 1080–1180 | 640–1500 | 172 |
| 60..100cm | soc | g/kg | 5.4–13.9 | 1.6–31.1 | 172 |
| 60..100cm | ph.h2o | pH | 5.9–6.7 | 5.1–7.7 | 172 |
