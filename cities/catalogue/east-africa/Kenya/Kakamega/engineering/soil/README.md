# Kakamega civil soil screening

115 route/station sample locations; 115 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 115 |
| fine-soil-plasticity-and-shrink-swell-tests | 115 |
| granular-density-and-groundwater-tests | 16 |

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
| 0..30cm | clay | % | 33–45 | 17–53 | 115 |
| 0..30cm | sand | % | 24–45 | 11–73 | 115 |
| 0..30cm | silt | % | 21–31 | 2–42 | 115 |
| 0..30cm | bd.core | kg/m3 | 1100–1190 | 920–1400 | 115 |
| 0..30cm | soc | g/kg | 10.8–24.8 | 5.5–44.7 | 115 |
| 0..30cm | ph.h2o | pH | 5.3–5.7 | 5–6.1 | 115 |
| 30..60cm | clay | % | 35–45 | 20–55 | 115 |
| 30..60cm | sand | % | 24–42 | 10–72 | 115 |
| 30..60cm | silt | % | 22–31 | 5–44 | 115 |
| 30..60cm | bd.core | kg/m3 | 1140–1230 | 940–1400 | 115 |
| 30..60cm | soc | g/kg | 7.5–12.4 | 3.8–21.8 | 115 |
| 30..60cm | ph.h2o | pH | 5.3–5.8 | 5–6.2 | 115 |
| 60..100cm | clay | % | 35–45 | 17–56 | 115 |
| 60..100cm | sand | % | 24–42 | 9–79 | 115 |
| 60..100cm | silt | % | 22–31 | 1–44 | 115 |
| 60..100cm | bd.core | kg/m3 | 1150–1260 | 960–1440 | 115 |
| 60..100cm | soc | g/kg | 6.3–8.7 | 3.1–14.8 | 115 |
| 60..100cm | ph.h2o | pH | 5.3–5.8 | 5–6.2 | 115 |
