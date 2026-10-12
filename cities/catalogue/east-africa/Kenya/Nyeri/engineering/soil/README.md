# Nyeri civil soil screening

821 route/station sample locations; 821 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 791 |
| fine-soil-plasticity-and-shrink-swell-tests | 821 |
| granular-density-and-groundwater-tests | 12 |

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
| 0..30cm | clay | % | 30–36 | 17–49 | 821 |
| 0..30cm | sand | % | 35–48 | 13–71 | 821 |
| 0..30cm | silt | % | 21–30 | 9–41 | 821 |
| 0..30cm | bd.core | kg/m3 | 1080–1270 | 830–1440 | 821 |
| 0..30cm | soc | g/kg | 12.6–26 | 6.8–44.4 | 821 |
| 0..30cm | ph.h2o | pH | 5.5–6.3 | 4.7–7.2 | 821 |
| 30..60cm | clay | % | 32–39 | 19–52 | 821 |
| 30..60cm | sand | % | 35–47 | 13–72 | 821 |
| 30..60cm | silt | % | 19–30 | 5–44 | 821 |
| 30..60cm | bd.core | kg/m3 | 1140–1290 | 870–1450 | 821 |
| 30..60cm | soc | g/kg | 8.9–14.5 | 4.3–23.7 | 821 |
| 30..60cm | ph.h2o | pH | 5.5–6.4 | 4.7–7.3 | 821 |
| 60..100cm | clay | % | 31–38 | 17–54 | 821 |
| 60..100cm | sand | % | 34–47 | 12–72 | 821 |
| 60..100cm | silt | % | 20–30 | 3–43 | 821 |
| 60..100cm | bd.core | kg/m3 | 1140–1270 | 930–1460 | 821 |
| 60..100cm | soc | g/kg | 6.2–9.4 | 3.2–16.7 | 821 |
| 60..100cm | ph.h2o | pH | 5.6–6.5 | 4.7–7.8 | 821 |
