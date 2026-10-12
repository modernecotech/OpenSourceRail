# Tunis civil soil screening

7,502 route/station sample locations; 7,501 complete profiles; 1 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 1 |
| fine-soil-plasticity-and-shrink-swell-tests | 7397 |
| granular-density-and-groundwater-tests | 2699 |
| organic-content-and-compressibility-tests | 2 |
| silt-moisture-frost-and-erosion-review | 1017 |

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
| 0..30cm | clay | % | 16–38 | 0–48 | 7501 |
| 0..30cm | sand | % | 23–66 | 5–92 | 7501 |
| 0..30cm | silt | % | 18–38 | 2–53 | 7501 |
| 0..30cm | bd.core | kg/m3 | 1250–1470 | 970–1650 | 7501 |
| 0..30cm | soc | g/kg | 3.6–16.5 | 1.7–44.7 | 7501 |
| 0..30cm | ph.h2o | pH | 7.4–8 | 6.7–8.5 | 7501 |
| 30..60cm | clay | % | 15–39 | 0–48 | 7501 |
| 30..60cm | sand | % | 24–66 | 5–95 | 7501 |
| 30..60cm | silt | % | 18–38 | 1–53 | 7501 |
| 30..60cm | bd.core | kg/m3 | 1340–1600 | 1070–1810 | 7501 |
| 30..60cm | soc | g/kg | 2.5–11.7 | 0.5–41 | 7501 |
| 30..60cm | ph.h2o | pH | 7.4–8.2 | 6.2–8.8 | 7501 |
| 60..100cm | clay | % | 15–39 | 0–49 | 7501 |
| 60..100cm | sand | % | 24–66 | 5–94 | 7501 |
| 60..100cm | silt | % | 19–37 | 0–54 | 7501 |
| 60..100cm | bd.core | kg/m3 | 1340–1640 | 950–1830 | 7501 |
| 60..100cm | soc | g/kg | 1.8–11.9 | 0.4–98.7 | 7501 |
| 60..100cm | ph.h2o | pH | 7.6–8.3 | 6.6–9 | 7501 |
