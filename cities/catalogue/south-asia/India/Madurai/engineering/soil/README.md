# Madurai civil soil screening

410 route/station sample locations; 410 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 12 |
| fine-soil-plasticity-and-shrink-swell-tests | 410 |
| granular-density-and-groundwater-tests | 145 |
| silt-moisture-frost-and-erosion-review | 3 |

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
| 0..30cm | clay | % | 25–38 | 8–53 | 410 |
| 0..30cm | sand | % | 34–57 | 8–87 | 410 |
| 0..30cm | silt | % | 17–30 | 1–46 | 410 |
| 0..30cm | bd.core | kg/m3 | 1340–1550 | 1080–1730 | 410 |
| 0..30cm | soc | g/kg | 3.9–12.1 | 1.7–23.9 | 410 |
| 0..30cm | ph.h2o | pH | 6.3–7.8 | 5.3–9.2 | 410 |
| 30..60cm | clay | % | 27–38 | 8–54 | 410 |
| 30..60cm | sand | % | 35–56 | 7–86 | 410 |
| 30..60cm | silt | % | 16–28 | 0–51 | 410 |
| 30..60cm | bd.core | kg/m3 | 1390–1560 | 1060–1800 | 410 |
| 30..60cm | soc | g/kg | 2.9–6.7 | 1.2–14.7 | 410 |
| 30..60cm | ph.h2o | pH | 6.3–8.2 | 5.4–9.1 | 410 |
| 60..100cm | clay | % | 28–39 | 9–54 | 410 |
| 60..100cm | sand | % | 34–53 | 7–85 | 410 |
| 60..100cm | silt | % | 18–28 | 0–50 | 410 |
| 60..100cm | bd.core | kg/m3 | 1410–1570 | 980–1850 | 410 |
| 60..100cm | soc | g/kg | 2.4–5.1 | 0–13.4 | 410 |
| 60..100cm | ph.h2o | pH | 6.5–8.2 | 4.9–9.1 | 410 |
