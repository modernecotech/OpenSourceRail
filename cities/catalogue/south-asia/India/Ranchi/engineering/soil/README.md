# Ranchi civil soil screening

430 route/station sample locations; 430 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 429 |
| fine-soil-plasticity-and-shrink-swell-tests | 392 |
| granular-density-and-groundwater-tests | 190 |
| silt-moisture-frost-and-erosion-review | 301 |

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
| 0..30cm | clay | % | 21–29 | 8–41 | 430 |
| 0..30cm | sand | % | 34–51 | 11–79 | 430 |
| 0..30cm | silt | % | 29–38 | 12–53 | 430 |
| 0..30cm | bd.core | kg/m3 | 1250–1440 | 970–1640 | 430 |
| 0..30cm | soc | g/kg | 5.5–10.1 | 2–23.5 | 430 |
| 0..30cm | ph.h2o | pH | 5.6–6.5 | 4.8–7.8 | 430 |
| 30..60cm | clay | % | 21–29 | 7–42 | 430 |
| 30..60cm | sand | % | 32–50 | 8–80 | 430 |
| 30..60cm | silt | % | 29–39 | 11–54 | 430 |
| 30..60cm | bd.core | kg/m3 | 1350–1520 | 1030–1720 | 430 |
| 30..60cm | soc | g/kg | 3.4–5.4 | 0.9–12.4 | 430 |
| 30..60cm | ph.h2o | pH | 5.8–6.6 | 5–7.8 | 430 |
| 60..100cm | clay | % | 21–29 | 6–42 | 430 |
| 60..100cm | sand | % | 31–49 | 5–79 | 430 |
| 60..100cm | silt | % | 30–40 | 11–59 | 430 |
| 60..100cm | bd.core | kg/m3 | 1380–1560 | 920–1790 | 430 |
| 60..100cm | soc | g/kg | 2.8–3.8 | 1.1–7.8 | 430 |
| 60..100cm | ph.h2o | pH | 5.9–6.6 | 5–8.1 | 430 |
