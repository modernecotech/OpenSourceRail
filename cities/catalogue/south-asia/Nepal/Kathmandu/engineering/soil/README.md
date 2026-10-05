# Kathmandu civil soil screening

1,411 route/station sample locations; 1,411 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1411 |
| fine-soil-plasticity-and-shrink-swell-tests | 1074 |
| granular-density-and-groundwater-tests | 290 |
| organic-content-and-compressibility-tests | 18 |
| silt-moisture-frost-and-erosion-review | 70 |

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
| 0..30cm | clay | % | 19–33 | 8–47 | 1411 |
| 0..30cm | sand | % | 31–57 | 10–78 | 1411 |
| 0..30cm | silt | % | 22–37 | 8–56 | 1411 |
| 0..30cm | bd.core | kg/m3 | 830–1210 | 510–1450 | 1411 |
| 0..30cm | soc | g/kg | 8.7–23.2 | 2.7–68.2 | 1411 |
| 0..30cm | ph.h2o | pH | 5.3–6.1 | 4.5–7.1 | 1411 |
| 30..60cm | clay | % | 19–34 | 8–47 | 1411 |
| 30..60cm | sand | % | 31–57 | 9–79 | 1411 |
| 30..60cm | silt | % | 22–36 | 8–54 | 1411 |
| 30..60cm | bd.core | kg/m3 | 980–1280 | 640–1550 | 1411 |
| 30..60cm | soc | g/kg | 3.7–7.9 | 1.4–18.8 | 1411 |
| 30..60cm | ph.h2o | pH | 5.4–6.4 | 4.7–7.4 | 1411 |
| 60..100cm | clay | % | 19–33 | 9–47 | 1411 |
| 60..100cm | sand | % | 31–56 | 8–81 | 1411 |
| 60..100cm | silt | % | 23–36 | 8–52 | 1411 |
| 60..100cm | bd.core | kg/m3 | 1110–1330 | 770–1610 | 1411 |
| 60..100cm | soc | g/kg | 2.2–5.2 | 0.7–14.2 | 1411 |
| 60..100cm | ph.h2o | pH | 5.5–6.5 | 4.5–7.6 | 1411 |
