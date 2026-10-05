# Kampala civil soil screening

1,190 route/station sample locations; 1,190 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 642 |
| fine-soil-plasticity-and-shrink-swell-tests | 1190 |
| granular-density-and-groundwater-tests | 74 |

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
| 0..30cm | clay | % | 30–44 | 15–53 | 1190 |
| 0..30cm | sand | % | 26–49 | 9–79 | 1190 |
| 0..30cm | silt | % | 18–34 | 4–47 | 1190 |
| 0..30cm | bd.core | kg/m3 | 1100–1330 | 880–1550 | 1190 |
| 0..30cm | soc | g/kg | 8.9–24.6 | 4.3–45.9 | 1190 |
| 0..30cm | ph.h2o | pH | 5.8–6.4 | 5.1–7.1 | 1190 |
| 30..60cm | clay | % | 32–47 | 16–57 | 1190 |
| 30..60cm | sand | % | 23–47 | 10–81 | 1190 |
| 30..60cm | silt | % | 18–30 | 1–45 | 1190 |
| 30..60cm | bd.core | kg/m3 | 1130–1360 | 880–1600 | 1190 |
| 30..60cm | soc | g/kg | 5.2–12.3 | 2.3–27.2 | 1190 |
| 30..60cm | ph.h2o | pH | 5.7–6.4 | 5–7.5 | 1190 |
| 60..100cm | clay | % | 32–48 | 16–58 | 1190 |
| 60..100cm | sand | % | 23–48 | 7–80 | 1190 |
| 60..100cm | silt | % | 18–30 | 0–45 | 1190 |
| 60..100cm | bd.core | kg/m3 | 1160–1420 | 840–1650 | 1190 |
| 60..100cm | soc | g/kg | 4.8–11 | 1.2–32.6 | 1190 |
| 60..100cm | ph.h2o | pH | 5.7–6.5 | 4.8–7.7 | 1190 |
