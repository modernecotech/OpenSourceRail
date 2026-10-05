# Kumba civil soil screening

100 route/station sample locations; 100 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 100 |
| fine-soil-plasticity-and-shrink-swell-tests | 100 |
| granular-density-and-groundwater-tests | 98 |
| organic-content-and-compressibility-tests | 54 |

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
| 0..30cm | clay | % | 21–34 | 10–52 | 100 |
| 0..30cm | sand | % | 39–64 | 10–82 | 100 |
| 0..30cm | silt | % | 15–27 | 2–43 | 100 |
| 0..30cm | bd.core | kg/m3 | 980–1190 | 670–1470 | 100 |
| 0..30cm | soc | g/kg | 9.8–40.2 | 3.6–84.1 | 100 |
| 0..30cm | ph.h2o | pH | 5.4–5.8 | 4.7–6.4 | 100 |
| 30..60cm | clay | % | 23–36 | 12–53 | 100 |
| 30..60cm | sand | % | 37–59 | 2–77 | 100 |
| 30..60cm | silt | % | 18–29 | 4–45 | 100 |
| 30..60cm | bd.core | kg/m3 | 1030–1210 | 750–1490 | 100 |
| 30..60cm | soc | g/kg | 6.1–20.5 | 2.1–41.5 | 100 |
| 30..60cm | ph.h2o | pH | 5.5–5.8 | 4.9–6.4 | 100 |
| 60..100cm | clay | % | 24–38 | 13–57 | 100 |
| 60..100cm | sand | % | 34–57 | 0–76 | 100 |
| 60..100cm | silt | % | 19–29 | 4–46 | 100 |
| 60..100cm | bd.core | kg/m3 | 1070–1220 | 750–1530 | 100 |
| 60..100cm | soc | g/kg | 5.4–12.4 | 2.5–27.7 | 100 |
| 60..100cm | ph.h2o | pH | 5.5–5.9 | 4.9–6.4 | 100 |
