# Kumba civil soil screening

141 route/station sample locations; 141 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 141 |
| fine-soil-plasticity-and-shrink-swell-tests | 141 |
| granular-density-and-groundwater-tests | 139 |
| organic-content-and-compressibility-tests | 92 |

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
| 0..30cm | clay | % | 21–34 | 10–52 | 141 |
| 0..30cm | sand | % | 39–64 | 10–82 | 141 |
| 0..30cm | silt | % | 15–27 | 2–43 | 141 |
| 0..30cm | bd.core | kg/m3 | 980–1190 | 670–1470 | 141 |
| 0..30cm | soc | g/kg | 10.4–40.9 | 3.6–84.1 | 141 |
| 0..30cm | ph.h2o | pH | 5.4–5.8 | 4.7–6.4 | 141 |
| 30..60cm | clay | % | 24–36 | 12–53 | 141 |
| 30..60cm | sand | % | 37–58 | 2–77 | 141 |
| 30..60cm | silt | % | 19–29 | 4–45 | 141 |
| 30..60cm | bd.core | kg/m3 | 1030–1210 | 750–1490 | 141 |
| 30..60cm | soc | g/kg | 6.2–21.5 | 2.6–41.4 | 141 |
| 30..60cm | ph.h2o | pH | 5.5–5.8 | 4.9–6.4 | 141 |
| 60..100cm | clay | % | 25–38 | 13–57 | 141 |
| 60..100cm | sand | % | 34–54 | 0–76 | 141 |
| 60..100cm | silt | % | 20–29 | 4–46 | 141 |
| 60..100cm | bd.core | kg/m3 | 1070–1220 | 750–1530 | 141 |
| 60..100cm | soc | g/kg | 5.4–12.4 | 2.5–27.7 | 141 |
| 60..100cm | ph.h2o | pH | 5.5–5.9 | 4.9–6.4 | 141 |
