# Fez civil soil screening

220 route/station sample locations; 220 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 217 |
| granular-density-and-groundwater-tests | 46 |
| silt-moisture-frost-and-erosion-review | 4 |

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
| 0..30cm | clay | % | 21–30 | 9–41 | 220 |
| 0..30cm | sand | % | 36–53 | 12–78 | 220 |
| 0..30cm | silt | % | 25–35 | 12–51 | 220 |
| 0..30cm | bd.core | kg/m3 | 1340–1480 | 1140–1620 | 220 |
| 0..30cm | soc | g/kg | 4.9–11.5 | 2.6–20.5 | 220 |
| 0..30cm | ph.h2o | pH | 7.2–7.7 | 6.4–8.2 | 220 |
| 30..60cm | clay | % | 24–32 | 13–42 | 220 |
| 30..60cm | sand | % | 36–52 | 13–75 | 220 |
| 30..60cm | silt | % | 24–33 | 9–49 | 220 |
| 30..60cm | bd.core | kg/m3 | 1460–1570 | 1270–1740 | 220 |
| 30..60cm | soc | g/kg | 2.9–5.6 | 1.1–8.6 | 220 |
| 30..60cm | ph.h2o | pH | 7.4–7.8 | 6.6–8.5 | 220 |
| 60..100cm | clay | % | 24–33 | 13–44 | 220 |
| 60..100cm | sand | % | 37–54 | 11–78 | 220 |
| 60..100cm | silt | % | 22–32 | 5–46 | 220 |
| 60..100cm | bd.core | kg/m3 | 1500–1620 | 1290–1830 | 220 |
| 60..100cm | soc | g/kg | 2.1–3.5 | 0.8–7.2 | 220 |
| 60..100cm | ph.h2o | pH | 7.4–8 | 6.4–8.8 | 220 |
