# Hebron civil soil screening

2,426 route/station sample locations; 2,418 complete profiles; 8 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 8 |
| fine-soil-plasticity-and-shrink-swell-tests | 2417 |
| granular-density-and-groundwater-tests | 1262 |
| silt-moisture-frost-and-erosion-review | 271 |

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
| 0..30cm | clay | % | 20–30 | 6–42 | 2418 |
| 0..30cm | sand | % | 34–54 | 10–74 | 2418 |
| 0..30cm | silt | % | 26–36 | 12–51 | 2418 |
| 0..30cm | bd.core | kg/m3 | 1360–1450 | 1150–1640 | 2418 |
| 0..30cm | soc | g/kg | 2.7–13.9 | 1.2–34.3 | 2418 |
| 0..30cm | ph.h2o | pH | 7.5–7.9 | 6.8–8.5 | 2418 |
| 30..60cm | clay | % | 21–31 | 5–44 | 2418 |
| 30..60cm | sand | % | 35–55 | 10–86 | 2418 |
| 30..60cm | silt | % | 24–35 | 7–51 | 2418 |
| 30..60cm | bd.core | kg/m3 | 1450–1580 | 1260–1800 | 2418 |
| 30..60cm | soc | g/kg | 2.8–5.9 | 1.1–12.2 | 2418 |
| 30..60cm | ph.h2o | pH | 7.5–7.9 | 6.8–8.7 | 2418 |
| 60..100cm | clay | % | 21–31 | 5–45 | 2418 |
| 60..100cm | sand | % | 34–55 | 9–84 | 2418 |
| 60..100cm | silt | % | 24–35 | 5–52 | 2418 |
| 60..100cm | bd.core | kg/m3 | 1460–1620 | 1250–1830 | 2418 |
| 60..100cm | soc | g/kg | 2.2–4.3 | 0.4–8.8 | 2418 |
| 60..100cm | ph.h2o | pH | 7.5–8 | 6.6–9.1 | 2418 |
