# Taiz civil soil screening

1,357 route/station sample locations; 1,356 complete profiles; 1 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 2 |
| coverage-gap | 1 |
| fine-soil-plasticity-and-shrink-swell-tests | 1356 |
| granular-density-and-groundwater-tests | 790 |
| organic-content-and-compressibility-tests | 10 |
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
| 0..30cm | clay | % | 22–35 | 7–47 | 1356 |
| 0..30cm | sand | % | 35–57 | 11–83 | 1356 |
| 0..30cm | silt | % | 19–32 | 3–47 | 1356 |
| 0..30cm | bd.core | kg/m3 | 1060–1510 | 780–1680 | 1356 |
| 0..30cm | soc | g/kg | 4.4–22.4 | 2.3–59.2 | 1356 |
| 0..30cm | ph.h2o | pH | 6.9–8.2 | 5.6–9 | 1356 |
| 30..60cm | clay | % | 24–36 | 8–52 | 1356 |
| 30..60cm | sand | % | 34–55 | 10–89 | 1356 |
| 30..60cm | silt | % | 19–31 | 2–47 | 1356 |
| 30..60cm | bd.core | kg/m3 | 1110–1490 | 800–1690 | 1356 |
| 30..60cm | soc | g/kg | 3.4–9.7 | 1.2–21.9 | 1356 |
| 30..60cm | ph.h2o | pH | 7.1–8.4 | 5.1–9.3 | 1356 |
| 60..100cm | clay | % | 25–37 | 7–53 | 1356 |
| 60..100cm | sand | % | 33–55 | 9–89 | 1356 |
| 60..100cm | silt | % | 20–32 | 2–50 | 1356 |
| 60..100cm | bd.core | kg/m3 | 1120–1500 | 620–1750 | 1356 |
| 60..100cm | soc | g/kg | 2.4–6.9 | 0.7–15.8 | 1356 |
| 60..100cm | ph.h2o | pH | 7.3–8.5 | 5.1–9.3 | 1356 |
