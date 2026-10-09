# Ramadi civil soil screening

590 route/station sample locations; 518 complete profiles; 72 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 72 |
| fine-soil-plasticity-and-shrink-swell-tests | 323 |
| granular-density-and-groundwater-tests | 471 |
| silt-moisture-frost-and-erosion-review | 75 |

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
| 0..30cm | clay | % | 16–29 | 2–39 | 518 |
| 0..30cm | sand | % | 32–60 | 9–87 | 518 |
| 0..30cm | silt | % | 23–39 | 8–54 | 518 |
| 0..30cm | bd.core | kg/m3 | 1450–1510 | 1270–1710 | 518 |
| 0..30cm | soc | g/kg | 2.2–5.7 | 0.5–13.6 | 518 |
| 0..30cm | ph.h2o | pH | 8–8.5 | 7.2–9.6 | 518 |
| 30..60cm | clay | % | 17–29 | 2–42 | 518 |
| 30..60cm | sand | % | 34–58 | 8–92 | 518 |
| 30..60cm | silt | % | 24–37 | 4–56 | 518 |
| 30..60cm | bd.core | kg/m3 | 1410–1550 | 1180–1760 | 518 |
| 30..60cm | soc | g/kg | 2–3.7 | 0–12.7 | 518 |
| 30..60cm | ph.h2o | pH | 8–8.9 | 7–10.2 | 518 |
| 60..100cm | clay | % | 17–29 | 2–43 | 518 |
| 60..100cm | sand | % | 34–57 | 7–91 | 518 |
| 60..100cm | silt | % | 25–37 | 4–59 | 518 |
| 60..100cm | bd.core | kg/m3 | 1420–1580 | 1210–1880 | 518 |
| 60..100cm | soc | g/kg | 1.6–2.9 | 0–8.2 | 518 |
| 60..100cm | ph.h2o | pH | 7.9–9 | 6.8–10.2 | 518 |
