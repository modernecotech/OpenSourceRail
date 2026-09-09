# Machakos civil soil screening

56 route/station sample locations; 56 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 38 |
| fine-soil-plasticity-and-shrink-swell-tests | 56 |
| granular-density-and-groundwater-tests | 16 |

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
| 0..30cm | clay | % | 26–34 | 14–47 | 56 |
| 0..30cm | sand | % | 35–50 | 11–75 | 56 |
| 0..30cm | silt | % | 23–32 | 10–45 | 56 |
| 0..30cm | bd.core | kg/m3 | 1260–1350 | 1070–1520 | 56 |
| 0..30cm | soc | g/kg | 7–14.7 | 3.9–21.2 | 56 |
| 0..30cm | ph.h2o | pH | 6–7.3 | 4.9–8.2 | 56 |
| 30..60cm | clay | % | 24–35 | 11–47 | 56 |
| 30..60cm | sand | % | 31–54 | 7–78 | 56 |
| 30..60cm | silt | % | 23–35 | 9–48 | 56 |
| 30..60cm | bd.core | kg/m3 | 1260–1350 | 1080–1530 | 56 |
| 30..60cm | soc | g/kg | 5.4–10 | 2.5–16.7 | 56 |
| 30..60cm | ph.h2o | pH | 5.9–7.4 | 5–8.2 | 56 |
| 60..100cm | clay | % | 23–35 | 9–46 | 56 |
| 60..100cm | sand | % | 31–55 | 7–81 | 56 |
| 60..100cm | silt | % | 22–35 | 8–49 | 56 |
| 60..100cm | bd.core | kg/m3 | 1260–1360 | 970–1600 | 56 |
| 60..100cm | soc | g/kg | 4.8–9.4 | 2–17.4 | 56 |
| 60..100cm | ph.h2o | pH | 6–7.3 | 4.9–8.2 | 56 |
