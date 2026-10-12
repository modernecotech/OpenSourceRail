# Mazar-E-Sharif civil soil screening

1,177 route/station sample locations; 1,107 complete profiles; 70 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 70 |
| fine-soil-plasticity-and-shrink-swell-tests | 925 |
| granular-density-and-groundwater-tests | 503 |
| silt-moisture-frost-and-erosion-review | 637 |

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
| 0..30cm | clay | % | 19–25 | 7–36 | 1107 |
| 0..30cm | sand | % | 38–55 | 12–78 | 1107 |
| 0..30cm | silt | % | 27–40 | 12–59 | 1107 |
| 0..30cm | bd.core | kg/m3 | 1370–1470 | 1180–1650 | 1107 |
| 0..30cm | soc | g/kg | 2.6–7.9 | 1–18.5 | 1107 |
| 0..30cm | ph.h2o | pH | 7.5–8.3 | 6.8–9 | 1107 |
| 30..60cm | clay | % | 18–26 | 2–42 | 1107 |
| 30..60cm | sand | % | 37–57 | 9–90 | 1107 |
| 30..60cm | silt | % | 25–39 | 5–61 | 1107 |
| 30..60cm | bd.core | kg/m3 | 1390–1540 | 1140–1750 | 1107 |
| 30..60cm | soc | g/kg | 1.6–4.6 | 0.2–12.6 | 1107 |
| 30..60cm | ph.h2o | pH | 7.7–8.7 | 6.6–9.8 | 1107 |
| 60..100cm | clay | % | 19–28 | 2–46 | 1107 |
| 60..100cm | sand | % | 37–56 | 8–90 | 1107 |
| 60..100cm | silt | % | 23–38 | 4–56 | 1107 |
| 60..100cm | bd.core | kg/m3 | 1420–1610 | 1110–1890 | 1107 |
| 60..100cm | soc | g/kg | 1.5–2.9 | 0.3–6.3 | 1107 |
| 60..100cm | ph.h2o | pH | 7.8–8.9 | 7–10.1 | 1107 |
