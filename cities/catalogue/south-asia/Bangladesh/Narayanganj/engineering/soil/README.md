# Narayanganj civil soil screening

449 route/station sample locations; 434 complete profiles; 15 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 434 |
| coverage-gap | 15 |
| fine-soil-plasticity-and-shrink-swell-tests | 434 |
| granular-density-and-groundwater-tests | 415 |
| organic-content-and-compressibility-tests | 92 |
| silt-moisture-frost-and-erosion-review | 4 |

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
| 0..30cm | clay | % | 22–29 | 7–47 | 434 |
| 0..30cm | sand | % | 42–56 | 13–89 | 434 |
| 0..30cm | silt | % | 21–30 | 1–46 | 434 |
| 0..30cm | bd.core | kg/m3 | 960–1290 | 650–1540 | 434 |
| 0..30cm | soc | g/kg | 8.6–22.1 | 2.8–59.5 | 434 |
| 0..30cm | ph.h2o | pH | 5.8–6.1 | 4.4–7.5 | 434 |
| 30..60cm | clay | % | 24–29 | 5–48 | 434 |
| 30..60cm | sand | % | 40–55 | 9–89 | 434 |
| 30..60cm | silt | % | 19–31 | 0–53 | 434 |
| 30..60cm | bd.core | kg/m3 | 960–1240 | 620–1600 | 434 |
| 30..60cm | soc | g/kg | 5.3–14.3 | 1.2–53.6 | 434 |
| 30..60cm | ph.h2o | pH | 6.1–6.5 | 4.7–7.9 | 434 |
| 60..100cm | clay | % | 25–30 | 5–48 | 434 |
| 60..100cm | sand | % | 39–54 | 9–89 | 434 |
| 60..100cm | silt | % | 19–31 | 0–53 | 434 |
| 60..100cm | bd.core | kg/m3 | 930–1160 | 460–1530 | 434 |
| 60..100cm | soc | g/kg | 4–10.8 | 0.9–37.3 | 434 |
| 60..100cm | ph.h2o | pH | 6.2–6.8 | 4.8–8.1 | 434 |
