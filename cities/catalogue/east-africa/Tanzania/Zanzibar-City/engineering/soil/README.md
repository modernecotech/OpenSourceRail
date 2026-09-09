# Zanzibar-City civil soil screening

279 route/station sample locations; 268 complete profiles; 11 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 267 |
| coverage-gap | 11 |
| fine-soil-plasticity-and-shrink-swell-tests | 223 |
| granular-density-and-groundwater-tests | 268 |
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
| 0..30cm | clay | % | 16–31 | 4–47 | 268 |
| 0..30cm | sand | % | 50–74 | 14–94 | 268 |
| 0..30cm | silt | % | 9–19 | 0–37 | 268 |
| 0..30cm | bd.core | kg/m3 | 1090–1330 | 890–1540 | 268 |
| 0..30cm | soc | g/kg | 5.5–25.8 | 2.2–53 | 268 |
| 0..30cm | ph.h2o | pH | 5.9–6.7 | 4.9–8 | 268 |
| 30..60cm | clay | % | 16–34 | 3–54 | 268 |
| 30..60cm | sand | % | 49–79 | 15–93 | 268 |
| 30..60cm | silt | % | 5–17 | 0–42 | 268 |
| 30..60cm | bd.core | kg/m3 | 1050–1430 | 770–1600 | 268 |
| 30..60cm | soc | g/kg | 3.9–18.2 | 1.4–40.4 | 268 |
| 30..60cm | ph.h2o | pH | 5.9–6.8 | 4.9–7.9 | 268 |
| 60..100cm | clay | % | 16–35 | 3–56 | 268 |
| 60..100cm | sand | % | 47–78 | 12–93 | 268 |
| 60..100cm | silt | % | 6–19 | 0–43 | 268 |
| 60..100cm | bd.core | kg/m3 | 1020–1460 | 730–1650 | 268 |
| 60..100cm | soc | g/kg | 3.4–14.5 | 1.1–43.2 | 268 |
| 60..100cm | ph.h2o | pH | 6–6.9 | 4.4–8.2 | 268 |
