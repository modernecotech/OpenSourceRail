# Mbuji-Mayi civil soil screening

224 route/station sample locations; 219 complete profiles; 5 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 219 |
| coverage-gap | 5 |
| fine-soil-plasticity-and-shrink-swell-tests | 219 |
| granular-density-and-groundwater-tests | 212 |

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
| 0..30cm | clay | % | 26–32 | 11–46 | 219 |
| 0..30cm | sand | % | 42–54 | 13–85 | 219 |
| 0..30cm | silt | % | 19–26 | 1–45 | 219 |
| 0..30cm | bd.core | kg/m3 | 1250–1400 | 1020–1620 | 219 |
| 0..30cm | soc | g/kg | 9.4–15.2 | 4–26.4 | 219 |
| 0..30cm | ph.h2o | pH | 5.4–5.9 | 4.3–6.9 | 219 |
| 30..60cm | clay | % | 27–34 | 9–52 | 219 |
| 30..60cm | sand | % | 41–53 | 13–80 | 219 |
| 30..60cm | silt | % | 19–26 | 1–46 | 219 |
| 30..60cm | bd.core | kg/m3 | 1330–1450 | 1090–1640 | 219 |
| 30..60cm | soc | g/kg | 4.9–8 | 2–13.2 | 219 |
| 30..60cm | ph.h2o | pH | 5.5–6 | 4.6–7.1 | 219 |
| 60..100cm | clay | % | 27–35 | 9–53 | 219 |
| 60..100cm | sand | % | 38–51 | 8–82 | 219 |
| 60..100cm | silt | % | 20–29 | 0–49 | 219 |
| 60..100cm | bd.core | kg/m3 | 1290–1480 | 1010–1680 | 219 |
| 60..100cm | soc | g/kg | 4.1–6 | 1.4–10.9 | 219 |
| 60..100cm | ph.h2o | pH | 5.6–6.2 | 4.4–8 | 219 |
