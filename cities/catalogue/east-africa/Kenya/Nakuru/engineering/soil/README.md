# Nakuru civil soil screening

1,007 route/station sample locations; 1,007 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 73 |
| fine-soil-plasticity-and-shrink-swell-tests | 853 |
| granular-density-and-groundwater-tests | 452 |

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
| 0..30cm | clay | % | 20–40 | 9–51 | 1007 |
| 0..30cm | sand | % | 26–64 | 9–83 | 1007 |
| 0..30cm | silt | % | 15–35 | 5–46 | 1007 |
| 0..30cm | bd.core | kg/m3 | 1160–1360 | 970–1510 | 1007 |
| 0..30cm | soc | g/kg | 7.1–24.1 | 3–46.3 | 1007 |
| 0..30cm | ph.h2o | pH | 5.9–7.4 | 5–8.3 | 1007 |
| 30..60cm | clay | % | 18–41 | 10–53 | 1007 |
| 30..60cm | sand | % | 26–65 | 8–83 | 1007 |
| 30..60cm | silt | % | 15–34 | 1–48 | 1007 |
| 30..60cm | bd.core | kg/m3 | 1200–1370 | 990–1550 | 1007 |
| 30..60cm | soc | g/kg | 4.8–11.2 | 2.5–18.8 | 1007 |
| 30..60cm | ph.h2o | pH | 6–7.5 | 5.3–8.4 | 1007 |
| 60..100cm | clay | % | 14–41 | 7–52 | 1007 |
| 60..100cm | sand | % | 26–74 | 7–85 | 1007 |
| 60..100cm | silt | % | 12–34 | 0–49 | 1007 |
| 60..100cm | bd.core | kg/m3 | 1200–1390 | 920–1600 | 1007 |
| 60..100cm | soc | g/kg | 3.3–8.1 | 1.4–15.8 | 1007 |
| 60..100cm | ph.h2o | pH | 6.3–7.7 | 5.3–8.5 | 1007 |
