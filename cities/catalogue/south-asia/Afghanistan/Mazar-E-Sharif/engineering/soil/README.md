# Mazar-E-Sharif civil soil screening

135 route/station sample locations; 127 complete profiles; 8 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 8 |
| fine-soil-plasticity-and-shrink-swell-tests | 90 |
| granular-density-and-groundwater-tests | 47 |
| silt-moisture-frost-and-erosion-review | 93 |

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
| 0..30cm | clay | % | 18–24 | 7–36 | 127 |
| 0..30cm | sand | % | 37–56 | 12–78 | 127 |
| 0..30cm | silt | % | 26–41 | 11–58 | 127 |
| 0..30cm | bd.core | kg/m3 | 1370–1470 | 1180–1640 | 127 |
| 0..30cm | soc | g/kg | 2.4–7.4 | 1–14.4 | 127 |
| 0..30cm | ph.h2o | pH | 7.6–8.4 | 7–9 | 127 |
| 30..60cm | clay | % | 18–26 | 2–40 | 127 |
| 30..60cm | sand | % | 38–59 | 9–90 | 127 |
| 30..60cm | silt | % | 24–38 | 6–56 | 127 |
| 30..60cm | bd.core | kg/m3 | 1390–1530 | 1130–1720 | 127 |
| 30..60cm | soc | g/kg | 1.8–4.4 | 0.3–8.4 | 127 |
| 30..60cm | ph.h2o | pH | 7.8–8.7 | 6.8–9.8 | 127 |
| 60..100cm | clay | % | 18–27 | 3–42 | 127 |
| 60..100cm | sand | % | 39–57 | 10–90 | 127 |
| 60..100cm | silt | % | 24–37 | 4–56 | 127 |
| 60..100cm | bd.core | kg/m3 | 1420–1600 | 1110–1830 | 127 |
| 60..100cm | soc | g/kg | 1.5–3 | 0.4–6.3 | 127 |
| 60..100cm | ph.h2o | pH | 7.8–8.9 | 6.9–10.1 | 127 |
