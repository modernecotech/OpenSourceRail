# Conakry civil soil screening

233 route/station sample locations; 194 complete profiles; 39 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 194 |
| coverage-gap | 39 |
| fine-soil-plasticity-and-shrink-swell-tests | 194 |
| granular-density-and-groundwater-tests | 194 |
| organic-content-and-compressibility-tests | 6 |
| silt-moisture-frost-and-erosion-review | 3 |

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
| 0..30cm | clay | % | 19–27 | 3–43 | 194 |
| 0..30cm | sand | % | 42–63 | 10–94 | 194 |
| 0..30cm | silt | % | 17–30 | 0–48 | 194 |
| 0..30cm | bd.core | kg/m3 | 790–1180 | 450–1510 | 194 |
| 0..30cm | soc | g/kg | 7.2–21 | 2.1–53.7 | 194 |
| 0..30cm | ph.h2o | pH | 5.4–5.9 | 4.6–6.9 | 194 |
| 30..60cm | clay | % | 18–28 | 0–46 | 194 |
| 30..60cm | sand | % | 40–66 | 7–94 | 194 |
| 30..60cm | silt | % | 16–32 | 0–50 | 194 |
| 30..60cm | bd.core | kg/m3 | 750–1220 | 330–1570 | 194 |
| 30..60cm | soc | g/kg | 4.9–13.8 | 1–55.5 | 194 |
| 30..60cm | ph.h2o | pH | 5.5–6.1 | 4.4–7.7 | 194 |
| 60..100cm | clay | % | 19–30 | 0–48 | 194 |
| 60..100cm | sand | % | 38–66 | 7–94 | 194 |
| 60..100cm | silt | % | 16–32 | 0–52 | 194 |
| 60..100cm | bd.core | kg/m3 | 760–1240 | 330–1600 | 194 |
| 60..100cm | soc | g/kg | 4.6–12.8 | 0.9–69.9 | 194 |
| 60..100cm | ph.h2o | pH | 5.5–6.2 | 4.6–7.9 | 194 |
