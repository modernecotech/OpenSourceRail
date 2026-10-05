# Machakos civil soil screening

47 route/station sample locations; 47 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 35 |
| fine-soil-plasticity-and-shrink-swell-tests | 47 |
| granular-density-and-groundwater-tests | 10 |

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
| 0..30cm | clay | % | 28–35 | 16–45 | 47 |
| 0..30cm | sand | % | 32–47 | 12–76 | 47 |
| 0..30cm | silt | % | 25–34 | 9–44 | 47 |
| 0..30cm | bd.core | kg/m3 | 1270–1360 | 1080–1520 | 47 |
| 0..30cm | soc | g/kg | 7.5–18.9 | 3.9–33.7 | 47 |
| 0..30cm | ph.h2o | pH | 6–7.3 | 4.8–8.2 | 47 |
| 30..60cm | clay | % | 26–36 | 14–46 | 47 |
| 30..60cm | sand | % | 27–48 | 8–75 | 47 |
| 30..60cm | silt | % | 26–37 | 10–48 | 47 |
| 30..60cm | bd.core | kg/m3 | 1280–1350 | 1080–1530 | 47 |
| 30..60cm | soc | g/kg | 5.6–9.9 | 2.9–18.1 | 47 |
| 30..60cm | ph.h2o | pH | 5.9–7.4 | 5–8.2 | 47 |
| 60..100cm | clay | % | 25–36 | 13–46 | 47 |
| 60..100cm | sand | % | 27–50 | 8–76 | 47 |
| 60..100cm | silt | % | 25–37 | 10–49 | 47 |
| 60..100cm | bd.core | kg/m3 | 1270–1360 | 970–1600 | 47 |
| 60..100cm | soc | g/kg | 4.8–9.3 | 2.2–16 | 47 |
| 60..100cm | ph.h2o | pH | 5.9–7.4 | 4.9–8.2 | 47 |
