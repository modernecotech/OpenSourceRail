# Dar-Es-Salaam civil soil screening

3,366 route/station sample locations; 3,365 complete profiles; 1 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 2071 |
| coverage-gap | 1 |
| fine-soil-plasticity-and-shrink-swell-tests | 1306 |
| granular-density-and-groundwater-tests | 3365 |
| organic-content-and-compressibility-tests | 34 |

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
| 0..30cm | clay | % | 10–33 | 1–49 | 3365 |
| 0..30cm | sand | % | 42–82 | 4–96 | 3365 |
| 0..30cm | silt | % | 7–27 | 0–48 | 3365 |
| 0..30cm | bd.core | kg/m3 | 900–1470 | 510–1620 | 3365 |
| 0..30cm | soc | g/kg | 3.3–40.4 | 1.3–83.8 | 3365 |
| 0..30cm | ph.h2o | pH | 5.7–7 | 4.9–8.1 | 3365 |
| 30..60cm | clay | % | 10–36 | 1–51 | 3365 |
| 30..60cm | sand | % | 40–85 | 6–95 | 3365 |
| 30..60cm | silt | % | 5–27 | 0–47 | 3365 |
| 30..60cm | bd.core | kg/m3 | 910–1520 | 560–1730 | 3365 |
| 30..60cm | soc | g/kg | 2.7–30.8 | 1.2–61.1 | 3365 |
| 30..60cm | ph.h2o | pH | 5.7–7.1 | 5–8.2 | 3365 |
| 60..100cm | clay | % | 10–36 | 1–52 | 3365 |
| 60..100cm | sand | % | 37–85 | 6–95 | 3365 |
| 60..100cm | silt | % | 5–27 | 0–47 | 3365 |
| 60..100cm | bd.core | kg/m3 | 930–1540 | 580–1770 | 3365 |
| 60..100cm | soc | g/kg | 2.2–27.4 | 0.9–64.1 | 3365 |
| 60..100cm | ph.h2o | pH | 5.7–7.2 | 4.7–8.6 | 3365 |
