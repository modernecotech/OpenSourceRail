# Erbil civil soil screening

313 route/station sample locations; 313 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 313 |
| granular-density-and-groundwater-tests | 70 |
| silt-moisture-frost-and-erosion-review | 139 |

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
| 0..30cm | clay | % | 23–40 | 8–50 | 313 |
| 0..30cm | sand | % | 19–49 | 4–71 | 313 |
| 0..30cm | silt | % | 29–42 | 13–57 | 313 |
| 0..30cm | bd.core | kg/m3 | 1340–1450 | 1140–1630 | 313 |
| 0..30cm | soc | g/kg | 2.4–7.2 | 0.8–12.9 | 313 |
| 0..30cm | ph.h2o | pH | 7.2–7.6 | 5.9–8.2 | 313 |
| 30..60cm | clay | % | 24–42 | 6–53 | 313 |
| 30..60cm | sand | % | 23–51 | 5–85 | 313 |
| 30..60cm | silt | % | 23–37 | 4–53 | 313 |
| 30..60cm | bd.core | kg/m3 | 1400–1520 | 1170–1700 | 313 |
| 30..60cm | soc | g/kg | 2.5–4.9 | 0.9–9 | 313 |
| 30..60cm | ph.h2o | pH | 7.1–7.5 | 6–8.3 | 313 |
| 60..100cm | clay | % | 25–44 | 7–56 | 313 |
| 60..100cm | sand | % | 24–55 | 7–85 | 313 |
| 60..100cm | silt | % | 18–34 | 0–53 | 313 |
| 60..100cm | bd.core | kg/m3 | 1390–1560 | 1170–1830 | 313 |
| 60..100cm | soc | g/kg | 2–3.2 | 0.6–6.7 | 313 |
| 60..100cm | ph.h2o | pH | 7–7.5 | 5.9–8.2 | 313 |
