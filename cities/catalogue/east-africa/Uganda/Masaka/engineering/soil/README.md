# Masaka civil soil screening

70 route/station sample locations; 70 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 70 |
| fine-soil-plasticity-and-shrink-swell-tests | 70 |
| granular-density-and-groundwater-tests | 8 |

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
| 0..30cm | clay | % | 33–42 | 20–53 | 70 |
| 0..30cm | sand | % | 31–47 | 12–70 | 70 |
| 0..30cm | silt | % | 19–29 | 7–39 | 70 |
| 0..30cm | bd.core | kg/m3 | 1080–1250 | 880–1420 | 70 |
| 0..30cm | soc | g/kg | 11–23.2 | 6.9–37.4 | 70 |
| 0..30cm | ph.h2o | pH | 5.8–6.2 | 4.8–7.2 | 70 |
| 30..60cm | clay | % | 33–44 | 17–55 | 70 |
| 30..60cm | sand | % | 31–48 | 12–75 | 70 |
| 30..60cm | silt | % | 18–27 | 4–37 | 70 |
| 30..60cm | bd.core | kg/m3 | 1120–1270 | 940–1450 | 70 |
| 30..60cm | soc | g/kg | 8–13.3 | 4.2–28.5 | 70 |
| 30..60cm | ph.h2o | pH | 5.8–6.3 | 4.8–7.3 | 70 |
| 60..100cm | clay | % | 33–45 | 16–55 | 70 |
| 60..100cm | sand | % | 30–49 | 12–79 | 70 |
| 60..100cm | silt | % | 17–26 | 4–37 | 70 |
| 60..100cm | bd.core | kg/m3 | 1150–1300 | 890–1570 | 70 |
| 60..100cm | soc | g/kg | 6.5–13.1 | 3–29.4 | 70 |
| 60..100cm | ph.h2o | pH | 5.9–6.4 | 5–7.5 | 70 |
