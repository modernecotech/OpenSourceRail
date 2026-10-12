# Malindi civil soil screening

461 route/station sample locations; 461 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 404 |
| fine-soil-plasticity-and-shrink-swell-tests | 70 |
| granular-density-and-groundwater-tests | 461 |

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
| 0..30cm | clay | % | 10–26 | 3–41 | 461 |
| 0..30cm | sand | % | 50–82 | 9–90 | 461 |
| 0..30cm | silt | % | 8–25 | 0–48 | 461 |
| 0..30cm | bd.core | kg/m3 | 1190–1430 | 870–1590 | 461 |
| 0..30cm | soc | g/kg | 5.5–18.4 | 2.2–34.8 | 461 |
| 0..30cm | ph.h2o | pH | 6.4–7.1 | 5.3–8.3 | 461 |
| 30..60cm | clay | % | 10–28 | 3–45 | 461 |
| 30..60cm | sand | % | 47–85 | 9–93 | 461 |
| 30..60cm | silt | % | 5–26 | 0–47 | 461 |
| 30..60cm | bd.core | kg/m3 | 1190–1440 | 910–1670 | 461 |
| 30..60cm | soc | g/kg | 3.6–7.9 | 1.6–15.1 | 461 |
| 30..60cm | ph.h2o | pH | 6.5–7.2 | 5.5–8.5 | 461 |
| 60..100cm | clay | % | 10–29 | 3–47 | 461 |
| 60..100cm | sand | % | 45–84 | 9–94 | 461 |
| 60..100cm | silt | % | 6–26 | 0–47 | 461 |
| 60..100cm | bd.core | kg/m3 | 1120–1470 | 650–1750 | 461 |
| 60..100cm | soc | g/kg | 3–6.7 | 1.1–17.1 | 461 |
| 60..100cm | ph.h2o | pH | 6.5–7.3 | 5.2–8.6 | 461 |
