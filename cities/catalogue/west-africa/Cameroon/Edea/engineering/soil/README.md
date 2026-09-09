# Edea civil soil screening

23 route/station sample locations; 21 complete profiles; 2 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 21 |
| coverage-gap | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 21 |
| granular-density-and-groundwater-tests | 6 |
| organic-content-and-compressibility-tests | 1 |
| silt-moisture-frost-and-erosion-review | 2 |

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
| 0..30cm | clay | % | 28–32 | 13–43 | 21 |
| 0..30cm | sand | % | 38–45 | 19–71 | 21 |
| 0..30cm | silt | % | 25–31 | 10–45 | 21 |
| 0..30cm | bd.core | kg/m3 | 900–1100 | 520–1390 | 21 |
| 0..30cm | soc | g/kg | 11.7–21.5 | 4.9–59.5 | 21 |
| 0..30cm | ph.h2o | pH | 5.5–5.8 | 4.3–7 | 21 |
| 30..60cm | clay | % | 29–35 | 10–48 | 21 |
| 30..60cm | sand | % | 35–43 | 16–68 | 21 |
| 30..60cm | silt | % | 24–32 | 7–50 | 21 |
| 30..60cm | bd.core | kg/m3 | 860–1180 | 420–1480 | 21 |
| 30..60cm | soc | g/kg | 5.7–10.2 | 1.5–17.5 | 21 |
| 30..60cm | ph.h2o | pH | 5.5–5.8 | 4.3–7 | 21 |
| 60..100cm | clay | % | 30–36 | 12–49 | 21 |
| 60..100cm | sand | % | 34–43 | 10–71 | 21 |
| 60..100cm | silt | % | 25–32 | 7–51 | 21 |
| 60..100cm | bd.core | kg/m3 | 840–1240 | 280–1530 | 21 |
| 60..100cm | soc | g/kg | 5–6.9 | 1.9–16.7 | 21 |
| 60..100cm | ph.h2o | pH | 5.5–5.9 | 4.4–7.2 | 21 |
