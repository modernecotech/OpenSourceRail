# Meknes civil soil screening

327 route/station sample locations; 327 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 327 |
| granular-density-and-groundwater-tests | 126 |

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
| 0..30cm | clay | % | 22–33 | 9–42 | 327 |
| 0..30cm | sand | % | 31–53 | 11–77 | 327 |
| 0..30cm | silt | % | 25–36 | 11–48 | 327 |
| 0..30cm | bd.core | kg/m3 | 1310–1450 | 1110–1590 | 327 |
| 0..30cm | soc | g/kg | 5.1–14 | 2.8–26 | 327 |
| 0..30cm | ph.h2o | pH | 7.1–7.7 | 6.3–8.3 | 327 |
| 30..60cm | clay | % | 23–35 | 7–46 | 327 |
| 30..60cm | sand | % | 31–53 | 13–80 | 327 |
| 30..60cm | silt | % | 23–34 | 9–45 | 327 |
| 30..60cm | bd.core | kg/m3 | 1460–1580 | 1270–1750 | 327 |
| 30..60cm | soc | g/kg | 3–5.5 | 1.2–10.5 | 327 |
| 30..60cm | ph.h2o | pH | 7.3–7.8 | 6.4–8.5 | 327 |
| 60..100cm | clay | % | 23–35 | 9–48 | 327 |
| 60..100cm | sand | % | 33–55 | 12–80 | 327 |
| 60..100cm | silt | % | 22–32 | 6–48 | 327 |
| 60..100cm | bd.core | kg/m3 | 1490–1600 | 1250–1790 | 327 |
| 60..100cm | soc | g/kg | 2.3–3.8 | 1–8.1 | 327 |
| 60..100cm | ph.h2o | pH | 7.4–8 | 6.5–8.7 | 327 |
