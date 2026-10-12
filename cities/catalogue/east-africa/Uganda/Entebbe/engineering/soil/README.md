# Entebbe civil soil screening

1,167 route/station sample locations; 1,167 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1167 |
| fine-soil-plasticity-and-shrink-swell-tests | 1167 |
| granular-density-and-groundwater-tests | 791 |
| organic-content-and-compressibility-tests | 111 |

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
| 0..30cm | clay | % | 27–40 | 12–52 | 1167 |
| 0..30cm | sand | % | 33–54 | 11–84 | 1167 |
| 0..30cm | silt | % | 18–28 | 1–45 | 1167 |
| 0..30cm | bd.core | kg/m3 | 820–1230 | 190–1460 | 1167 |
| 0..30cm | soc | g/kg | 10.8–36.7 | 4.6–94.9 | 1167 |
| 0..30cm | ph.h2o | pH | 5.7–6.3 | 4.9–7.4 | 1167 |
| 30..60cm | clay | % | 29–43 | 10–56 | 1167 |
| 30..60cm | sand | % | 31–52 | 5–85 | 1167 |
| 30..60cm | silt | % | 19–27 | 1–48 | 1167 |
| 30..60cm | bd.core | kg/m3 | 880–1280 | 190–1490 | 1167 |
| 30..60cm | soc | g/kg | 5.9–20.8 | 1.9–70.2 | 1167 |
| 30..60cm | ph.h2o | pH | 5.6–6.3 | 4.8–7.4 | 1167 |
| 60..100cm | clay | % | 30–43 | 9–56 | 1167 |
| 60..100cm | sand | % | 30–51 | 6–87 | 1167 |
| 60..100cm | silt | % | 18–28 | 0–49 | 1167 |
| 60..100cm | bd.core | kg/m3 | 870–1280 | 180–1520 | 1167 |
| 60..100cm | soc | g/kg | 4.4–18.8 | 1.7–78.8 | 1167 |
| 60..100cm | ph.h2o | pH | 5.6–6.3 | 4.7–7.4 | 1167 |
