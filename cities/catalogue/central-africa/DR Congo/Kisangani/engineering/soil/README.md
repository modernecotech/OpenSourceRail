# Kisangani civil soil screening

343 route/station sample locations; 343 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 343 |
| fine-soil-plasticity-and-shrink-swell-tests | 284 |
| granular-density-and-groundwater-tests | 343 |
| organic-content-and-compressibility-tests | 14 |
| silt-moisture-frost-and-erosion-review | 3 |

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
| 0..30cm | clay | % | 13–22 | 4–37 | 343 |
| 0..30cm | sand | % | 47–66 | 23–86 | 343 |
| 0..30cm | silt | % | 20–31 | 8–45 | 343 |
| 0..30cm | bd.core | kg/m3 | 990–1280 | 510–1520 | 343 |
| 0..30cm | soc | g/kg | 9–24.4 | 4.3–65.8 | 343 |
| 0..30cm | ph.h2o | pH | 5–6 | 4.2–7.2 | 343 |
| 30..60cm | clay | % | 18–26 | 4–43 | 343 |
| 30..60cm | sand | % | 46–60 | 19–85 | 343 |
| 30..60cm | silt | % | 22–29 | 6–45 | 343 |
| 30..60cm | bd.core | kg/m3 | 1060–1330 | 670–1600 | 343 |
| 30..60cm | soc | g/kg | 4.5–12.2 | 1.4–48.3 | 343 |
| 30..60cm | ph.h2o | pH | 5.1–6 | 4.3–7.4 | 343 |
| 60..100cm | clay | % | 19–27 | 4–44 | 343 |
| 60..100cm | sand | % | 43–59 | 8–85 | 343 |
| 60..100cm | silt | % | 22–30 | 3–51 | 343 |
| 60..100cm | bd.core | kg/m3 | 1080–1330 | 590–1680 | 343 |
| 60..100cm | soc | g/kg | 3.2–7.1 | 1.3–26.7 | 343 |
| 60..100cm | ph.h2o | pH | 5.2–6.1 | 4.3–7.4 | 343 |
