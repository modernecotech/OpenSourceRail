# Coimbatore civil soil screening

8,360 route/station sample locations; 8,356 complete profiles; 4 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1522 |
| coverage-gap | 4 |
| fine-soil-plasticity-and-shrink-swell-tests | 8356 |
| granular-density-and-groundwater-tests | 8097 |
| silt-moisture-frost-and-erosion-review | 13 |

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
| 0..30cm | clay | % | 25–36 | 10–52 | 8356 |
| 0..30cm | sand | % | 38–58 | 5–89 | 8356 |
| 0..30cm | silt | % | 16–28 | 0–47 | 8356 |
| 0..30cm | bd.core | kg/m3 | 1300–1560 | 1080–1740 | 8356 |
| 0..30cm | soc | g/kg | 5–13 | 2.3–27.9 | 8356 |
| 0..30cm | ph.h2o | pH | 6.2–7.9 | 5.3–8.7 | 8356 |
| 30..60cm | clay | % | 26–36 | 9–52 | 8356 |
| 30..60cm | sand | % | 38–56 | 5–87 | 8356 |
| 30..60cm | silt | % | 16–27 | 0–51 | 8356 |
| 30..60cm | bd.core | kg/m3 | 1360–1590 | 1020–1810 | 8356 |
| 30..60cm | soc | g/kg | 3.3–8 | 1.1–18.4 | 8356 |
| 30..60cm | ph.h2o | pH | 6.2–8.1 | 5.3–8.9 | 8356 |
| 60..100cm | clay | % | 26–36 | 9–52 | 8356 |
| 60..100cm | sand | % | 38–55 | 5–87 | 8356 |
| 60..100cm | silt | % | 16–27 | 0–51 | 8356 |
| 60..100cm | bd.core | kg/m3 | 1360–1610 | 900–1860 | 8356 |
| 60..100cm | soc | g/kg | 2–6.1 | 0.3–11.3 | 8356 |
| 60..100cm | ph.h2o | pH | 6.2–8.3 | 4.9–9.4 | 8356 |
