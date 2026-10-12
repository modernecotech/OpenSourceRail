# Masaka civil soil screening

580 route/station sample locations; 580 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 580 |
| fine-soil-plasticity-and-shrink-swell-tests | 580 |
| granular-density-and-groundwater-tests | 75 |

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
| 0..30cm | clay | % | 32–45 | 19–55 | 580 |
| 0..30cm | sand | % | 26–48 | 11–71 | 580 |
| 0..30cm | silt | % | 19–29 | 6–40 | 580 |
| 0..30cm | bd.core | kg/m3 | 1100–1270 | 860–1420 | 580 |
| 0..30cm | soc | g/kg | 11.2–23.7 | 6.5–42.1 | 580 |
| 0..30cm | ph.h2o | pH | 5.8–6.2 | 4.8–7.4 | 580 |
| 30..60cm | clay | % | 33–46 | 17–56 | 580 |
| 30..60cm | sand | % | 28–50 | 12–75 | 580 |
| 30..60cm | silt | % | 16–27 | 4–39 | 580 |
| 30..60cm | bd.core | kg/m3 | 1170–1280 | 950–1490 | 580 |
| 30..60cm | soc | g/kg | 7.7–13.1 | 3.9–27.9 | 580 |
| 30..60cm | ph.h2o | pH | 5.8–6.3 | 4.8–7.5 | 580 |
| 60..100cm | clay | % | 33–46 | 16–56 | 580 |
| 60..100cm | sand | % | 28–51 | 12–79 | 580 |
| 60..100cm | silt | % | 16–26 | 3–38 | 580 |
| 60..100cm | bd.core | kg/m3 | 1170–1310 | 880–1570 | 580 |
| 60..100cm | soc | g/kg | 6.4–12.7 | 2.5–29.6 | 580 |
| 60..100cm | ph.h2o | pH | 5.9–6.3 | 5–7.6 | 580 |
