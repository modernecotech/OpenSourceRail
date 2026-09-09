# Entebbe civil soil screening

74 route/station sample locations; 68 complete profiles; 6 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 68 |
| coverage-gap | 6 |
| fine-soil-plasticity-and-shrink-swell-tests | 68 |
| granular-density-and-groundwater-tests | 59 |
| organic-content-and-compressibility-tests | 4 |

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
| 0..30cm | clay | % | 27–38 | 12–49 | 68 |
| 0..30cm | sand | % | 37–52 | 13–84 | 68 |
| 0..30cm | silt | % | 20–27 | 3–44 | 68 |
| 0..30cm | bd.core | kg/m3 | 890–1220 | 210–1440 | 68 |
| 0..30cm | soc | g/kg | 10.5–32.9 | 5.3–79.4 | 68 |
| 0..30cm | ph.h2o | pH | 5.7–6.2 | 5–7.3 | 68 |
| 30..60cm | clay | % | 30–41 | 12–55 | 68 |
| 30..60cm | sand | % | 34–49 | 10–85 | 68 |
| 30..60cm | silt | % | 20–26 | 0–45 | 68 |
| 30..60cm | bd.core | kg/m3 | 900–1280 | 210–1480 | 68 |
| 30..60cm | soc | g/kg | 6.8–14.5 | 3.7–30.5 | 68 |
| 30..60cm | ph.h2o | pH | 5.6–6.3 | 4.9–7.4 | 68 |
| 60..100cm | clay | % | 31–42 | 10–55 | 68 |
| 60..100cm | sand | % | 33–49 | 8–84 | 68 |
| 60..100cm | silt | % | 20–27 | 0–49 | 68 |
| 60..100cm | bd.core | kg/m3 | 890–1280 | 200–1500 | 68 |
| 60..100cm | soc | g/kg | 6.2–10.4 | 2–25.7 | 68 |
| 60..100cm | ph.h2o | pH | 5.6–6.3 | 4.8–7.4 | 68 |
