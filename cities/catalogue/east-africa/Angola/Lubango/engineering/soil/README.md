# Lubango civil soil screening

308 route/station sample locations; 308 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 302 |
| fine-soil-plasticity-and-shrink-swell-tests | 308 |
| granular-density-and-groundwater-tests | 259 |

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
| 0..30cm | clay | % | 24–33 | 9–46 | 308 |
| 0..30cm | sand | % | 44–61 | 21–82 | 308 |
| 0..30cm | silt | % | 15–24 | 2–39 | 308 |
| 0..30cm | bd.core | kg/m3 | 1240–1430 | 1030–1650 | 308 |
| 0..30cm | soc | g/kg | 5–13.4 | 1.9–22.5 | 308 |
| 0..30cm | ph.h2o | pH | 5.8–6.6 | 4.9–7.6 | 308 |
| 30..60cm | clay | % | 27–36 | 9–49 | 308 |
| 30..60cm | sand | % | 40–58 | 18–86 | 308 |
| 30..60cm | silt | % | 15–26 | 0–45 | 308 |
| 30..60cm | bd.core | kg/m3 | 1280–1440 | 990–1650 | 308 |
| 30..60cm | soc | g/kg | 4.2–6.6 | 1.7–12.7 | 308 |
| 30..60cm | ph.h2o | pH | 6–6.7 | 5–7.7 | 308 |
| 60..100cm | clay | % | 27–36 | 8–50 | 308 |
| 60..100cm | sand | % | 40–56 | 13–84 | 308 |
| 60..100cm | silt | % | 16–27 | 0–48 | 308 |
| 60..100cm | bd.core | kg/m3 | 1270–1510 | 760–1730 | 308 |
| 60..100cm | soc | g/kg | 3–5.9 | 0.8–13.5 | 308 |
| 60..100cm | ph.h2o | pH | 6.1–6.8 | 4.9–8.4 | 308 |
