# Rubavu civil soil screening

125 route/station sample locations; 118 complete profiles; 7 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 69 |
| coverage-gap | 7 |
| fine-soil-plasticity-and-shrink-swell-tests | 118 |
| granular-density-and-groundwater-tests | 63 |
| organic-content-and-compressibility-tests | 15 |

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
| 0..30cm | clay | % | 29–37 | 16–48 | 118 |
| 0..30cm | sand | % | 37–53 | 17–73 | 118 |
| 0..30cm | silt | % | 18–28 | 5–43 | 118 |
| 0..30cm | bd.core | kg/m3 | 960–1170 | 740–1390 | 118 |
| 0..30cm | soc | g/kg | 10.9–42 | 4.3–91.5 | 118 |
| 0..30cm | ph.h2o | pH | 5.7–6.6 | 5–7.7 | 118 |
| 30..60cm | clay | % | 31–41 | 14–54 | 118 |
| 30..60cm | sand | % | 37–50 | 10–74 | 118 |
| 30..60cm | silt | % | 18–27 | 1–44 | 118 |
| 30..60cm | bd.core | kg/m3 | 1040–1180 | 790–1400 | 118 |
| 30..60cm | soc | g/kg | 7.2–17.7 | 1.9–30.8 | 118 |
| 30..60cm | ph.h2o | pH | 5.7–6.6 | 5–7.7 | 118 |
| 60..100cm | clay | % | 31–41 | 14–56 | 118 |
| 60..100cm | sand | % | 37–50 | 11–74 | 118 |
| 60..100cm | silt | % | 18–27 | 0–43 | 118 |
| 60..100cm | bd.core | kg/m3 | 1040–1180 | 650–1500 | 118 |
| 60..100cm | soc | g/kg | 4.9–12.1 | 1.6–30 | 118 |
| 60..100cm | ph.h2o | pH | 5.7–6.7 | 5.1–7.8 | 118 |
