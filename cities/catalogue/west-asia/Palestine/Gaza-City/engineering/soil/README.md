# Gaza-City civil soil screening

255 route/station sample locations; 241 complete profiles; 14 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 14 |
| fine-soil-plasticity-and-shrink-swell-tests | 241 |
| granular-density-and-groundwater-tests | 226 |

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
| 0..30cm | clay | % | 22–29 | 5–44 | 241 |
| 0..30cm | sand | % | 41–57 | 16–87 | 241 |
| 0..30cm | silt | % | 19–30 | 3–44 | 241 |
| 0..30cm | bd.core | kg/m3 | 1370–1430 | 1140–1650 | 241 |
| 0..30cm | soc | g/kg | 2.8–9.6 | 1.1–17.7 | 241 |
| 0..30cm | ph.h2o | pH | 7.5–7.7 | 6.9–8.6 | 241 |
| 30..60cm | clay | % | 24–31 | 2–45 | 241 |
| 30..60cm | sand | % | 40–58 | 14–89 | 241 |
| 30..60cm | silt | % | 18–30 | 0–46 | 241 |
| 30..60cm | bd.core | kg/m3 | 1460–1560 | 1140–1830 | 241 |
| 30..60cm | soc | g/kg | 2.2–5.8 | 0.9–13.4 | 241 |
| 30..60cm | ph.h2o | pH | 7.6–7.8 | 6.7–8.7 | 241 |
| 60..100cm | clay | % | 24–31 | 2–47 | 241 |
| 60..100cm | sand | % | 39–57 | 10–90 | 241 |
| 60..100cm | silt | % | 19–31 | 0–48 | 241 |
| 60..100cm | bd.core | kg/m3 | 1480–1580 | 1080–1860 | 241 |
| 60..100cm | soc | g/kg | 1.7–3.7 | 0.3–7.7 | 241 |
| 60..100cm | ph.h2o | pH | 7.6–7.9 | 6.7–9 | 241 |
