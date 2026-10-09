# Fort-Portal civil soil screening

384 route/station sample locations; 384 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 384 |
| fine-soil-plasticity-and-shrink-swell-tests | 384 |
| granular-density-and-groundwater-tests | 3 |
| organic-content-and-compressibility-tests | 3 |

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
| 0..30cm | clay | % | 31–39 | 19–52 | 384 |
| 0..30cm | sand | % | 34–46 | 12–69 | 384 |
| 0..30cm | silt | % | 21–28 | 7–40 | 384 |
| 0..30cm | bd.core | kg/m3 | 1060–1220 | 790–1460 | 384 |
| 0..30cm | soc | g/kg | 12.5–28.2 | 8–47.6 | 384 |
| 0..30cm | ph.h2o | pH | 5.5–6.2 | 4.9–7.5 | 384 |
| 30..60cm | clay | % | 33–42 | 19–56 | 384 |
| 30..60cm | sand | % | 34–47 | 13–74 | 384 |
| 30..60cm | silt | % | 19–25 | 5–38 | 384 |
| 30..60cm | bd.core | kg/m3 | 1050–1310 | 670–1550 | 384 |
| 30..60cm | soc | g/kg | 7.7–15.1 | 4.7–30.6 | 384 |
| 30..60cm | ph.h2o | pH | 5.7–6.4 | 4.8–7.9 | 384 |
| 60..100cm | clay | % | 33–43 | 16–57 | 384 |
| 60..100cm | sand | % | 32–47 | 13–73 | 384 |
| 60..100cm | silt | % | 18–25 | 3–39 | 384 |
| 60..100cm | bd.core | kg/m3 | 1040–1300 | 670–1620 | 384 |
| 60..100cm | soc | g/kg | 6–17.3 | 2.8–87.6 | 384 |
| 60..100cm | ph.h2o | pH | 5.8–6.6 | 4.7–7.9 | 384 |
