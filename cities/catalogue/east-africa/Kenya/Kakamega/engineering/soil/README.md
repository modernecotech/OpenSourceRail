# Kakamega civil soil screening

97 route/station sample locations; 97 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 97 |
| fine-soil-plasticity-and-shrink-swell-tests | 97 |
| granular-density-and-groundwater-tests | 10 |

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
| 0..30cm | clay | % | 32–45 | 18–53 | 97 |
| 0..30cm | sand | % | 24–48 | 11–73 | 97 |
| 0..30cm | silt | % | 20–31 | 2–42 | 97 |
| 0..30cm | bd.core | kg/m3 | 1100–1200 | 920–1400 | 97 |
| 0..30cm | soc | g/kg | 9.3–25.6 | 4.9–44.7 | 97 |
| 0..30cm | ph.h2o | pH | 5.3–5.7 | 5–6.1 | 97 |
| 30..60cm | clay | % | 33–45 | 17–55 | 97 |
| 30..60cm | sand | % | 24–46 | 10–72 | 97 |
| 30..60cm | silt | % | 21–31 | 4–44 | 97 |
| 30..60cm | bd.core | kg/m3 | 1140–1240 | 920–1400 | 97 |
| 30..60cm | soc | g/kg | 6.7–12.5 | 3.2–22.8 | 97 |
| 30..60cm | ph.h2o | pH | 5.3–5.8 | 5–6.2 | 97 |
| 60..100cm | clay | % | 33–45 | 16–56 | 97 |
| 60..100cm | sand | % | 24–46 | 9–79 | 97 |
| 60..100cm | silt | % | 21–31 | 1–44 | 97 |
| 60..100cm | bd.core | kg/m3 | 1150–1260 | 960–1440 | 97 |
| 60..100cm | soc | g/kg | 5.5–8.7 | 3.1–14.8 | 97 |
| 60..100cm | ph.h2o | pH | 5.3–5.8 | 5–6.2 | 97 |
