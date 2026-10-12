# Narayanganj civil soil screening

2,286 route/station sample locations; 2,270 complete profiles; 16 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 2270 |
| coverage-gap | 16 |
| fine-soil-plasticity-and-shrink-swell-tests | 2270 |
| granular-density-and-groundwater-tests | 2208 |
| organic-content-and-compressibility-tests | 515 |
| silt-moisture-frost-and-erosion-review | 2 |

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
| 0..30cm | clay | % | 22–29 | 5–48 | 2270 |
| 0..30cm | sand | % | 41–57 | 11–89 | 2270 |
| 0..30cm | silt | % | 20–30 | 1–46 | 2270 |
| 0..30cm | bd.core | kg/m3 | 940–1290 | 630–1540 | 2270 |
| 0..30cm | soc | g/kg | 8.2–23.1 | 2.6–64.2 | 2270 |
| 0..30cm | ph.h2o | pH | 5.8–6.2 | 4.4–7.6 | 2270 |
| 30..60cm | clay | % | 22–30 | 5–50 | 2270 |
| 30..60cm | sand | % | 40–57 | 9–89 | 2270 |
| 30..60cm | silt | % | 19–31 | 0–53 | 2270 |
| 30..60cm | bd.core | kg/m3 | 950–1240 | 550–1600 | 2270 |
| 30..60cm | soc | g/kg | 5–17.3 | 1.2–59.9 | 2270 |
| 30..60cm | ph.h2o | pH | 6.1–6.6 | 4.7–7.9 | 2270 |
| 60..100cm | clay | % | 23–31 | 5–49 | 2270 |
| 60..100cm | sand | % | 40–56 | 8–89 | 2270 |
| 60..100cm | silt | % | 19–30 | 0–53 | 2270 |
| 60..100cm | bd.core | kg/m3 | 920–1160 | 460–1530 | 2270 |
| 60..100cm | soc | g/kg | 3.8–12.5 | 0.9–42.2 | 2270 |
| 60..100cm | ph.h2o | pH | 6.2–6.8 | 4.7–8.1 | 2270 |
