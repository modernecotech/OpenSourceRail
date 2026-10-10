# Dar-Es-Salaam civil soil screening

9,023 route/station sample locations; 9,021 complete profiles; 2 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 6048 |
| coverage-gap | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 4391 |
| granular-density-and-groundwater-tests | 9021 |
| organic-content-and-compressibility-tests | 50 |

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
| 0..30cm | clay | % | 10–34 | 1–51 | 9021 |
| 0..30cm | sand | % | 40–82 | 4–97 | 9021 |
| 0..30cm | silt | % | 7–27 | 0–48 | 9021 |
| 0..30cm | bd.core | kg/m3 | 900–1480 | 510–1620 | 9021 |
| 0..30cm | soc | g/kg | 3.5–40.4 | 1.3–83.8 | 9021 |
| 0..30cm | ph.h2o | pH | 5.7–7.2 | 4.9–8.2 | 9021 |
| 30..60cm | clay | % | 10–36 | 1–53 | 9021 |
| 30..60cm | sand | % | 37–86 | 5–96 | 9021 |
| 30..60cm | silt | % | 4–27 | 0–47 | 9021 |
| 30..60cm | bd.core | kg/m3 | 910–1540 | 560–1730 | 9021 |
| 30..60cm | soc | g/kg | 2.7–30.8 | 1–65.1 | 9021 |
| 30..60cm | ph.h2o | pH | 5.6–7.2 | 4.9–8.4 | 9021 |
| 60..100cm | clay | % | 10–37 | 1–55 | 9021 |
| 60..100cm | sand | % | 35–87 | 5–96 | 9021 |
| 60..100cm | silt | % | 4–29 | 0–48 | 9021 |
| 60..100cm | bd.core | kg/m3 | 930–1550 | 580–1770 | 9021 |
| 60..100cm | soc | g/kg | 2.2–27.4 | 0.9–65.1 | 9021 |
| 60..100cm | ph.h2o | pH | 5.6–7.3 | 4.6–8.6 | 9021 |
