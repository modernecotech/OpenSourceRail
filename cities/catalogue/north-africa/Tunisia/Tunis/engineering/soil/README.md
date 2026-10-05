# Tunis civil soil screening

873 route/station sample locations; 871 complete profiles; 2 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 838 |
| granular-density-and-groundwater-tests | 279 |
| organic-content-and-compressibility-tests | 1 |
| silt-moisture-frost-and-erosion-review | 100 |

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
| 0..30cm | clay | % | 15–38 | 0–47 | 871 |
| 0..30cm | sand | % | 23–66 | 5–92 | 871 |
| 0..30cm | silt | % | 19–38 | 2–52 | 871 |
| 0..30cm | bd.core | kg/m3 | 1250–1470 | 970–1650 | 871 |
| 0..30cm | soc | g/kg | 3.7–13.1 | 1.8–26.2 | 871 |
| 0..30cm | ph.h2o | pH | 7.4–8 | 6.6–8.4 | 871 |
| 30..60cm | clay | % | 15–39 | 0–47 | 871 |
| 30..60cm | sand | % | 24–68 | 4–95 | 871 |
| 30..60cm | silt | % | 17–38 | 0–52 | 871 |
| 30..60cm | bd.core | kg/m3 | 1340–1600 | 1060–1800 | 871 |
| 30..60cm | soc | g/kg | 2.6–9.7 | 0.7–32.9 | 871 |
| 30..60cm | ph.h2o | pH | 7.4–8.1 | 6.2–8.8 | 871 |
| 60..100cm | clay | % | 16–39 | 0–49 | 871 |
| 60..100cm | sand | % | 24–68 | 4–95 | 871 |
| 60..100cm | silt | % | 17–37 | 0–53 | 871 |
| 60..100cm | bd.core | kg/m3 | 1340–1620 | 950–1830 | 871 |
| 60..100cm | soc | g/kg | 1.9–11.9 | 0.4–98.7 | 871 |
| 60..100cm | ph.h2o | pH | 7.5–8.3 | 6.5–9 | 871 |
