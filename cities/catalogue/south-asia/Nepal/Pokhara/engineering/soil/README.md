# Pokhara civil soil screening

560 route/station sample locations; 555 complete profiles; 5 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 555 |
| coverage-gap | 5 |
| fine-soil-plasticity-and-shrink-swell-tests | 371 |
| granular-density-and-groundwater-tests | 497 |

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
| 0..30cm | clay | % | 16–26 | 7–39 | 555 |
| 0..30cm | sand | % | 44–61 | 18–80 | 555 |
| 0..30cm | silt | % | 23–31 | 9–46 | 555 |
| 0..30cm | bd.core | kg/m3 | 920–1190 | 650–1540 | 555 |
| 0..30cm | soc | g/kg | 10.2–15.7 | 3.1–43.8 | 555 |
| 0..30cm | ph.h2o | pH | 5.4–5.8 | 4.6–6.9 | 555 |
| 30..60cm | clay | % | 16–26 | 6–39 | 555 |
| 30..60cm | sand | % | 45–61 | 19–82 | 555 |
| 30..60cm | silt | % | 22–30 | 9–46 | 555 |
| 30..60cm | bd.core | kg/m3 | 1000–1240 | 690–1600 | 555 |
| 30..60cm | soc | g/kg | 5–10.7 | 1.7–29.5 | 555 |
| 30..60cm | ph.h2o | pH | 5.5–5.9 | 4.7–7 | 555 |
| 60..100cm | clay | % | 16–27 | 7–41 | 555 |
| 60..100cm | sand | % | 44–61 | 19–83 | 555 |
| 60..100cm | silt | % | 22–30 | 7–45 | 555 |
| 60..100cm | bd.core | kg/m3 | 1050–1280 | 680–1600 | 555 |
| 60..100cm | soc | g/kg | 2.8–8.5 | 0.9–26.4 | 555 |
| 60..100cm | ph.h2o | pH | 5.5–6 | 4.7–7.2 | 555 |
