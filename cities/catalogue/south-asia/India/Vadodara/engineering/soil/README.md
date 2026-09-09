# Vadodara civil soil screening

315 route/station sample locations; 315 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 315 |
| granular-density-and-groundwater-tests | 315 |
| silt-moisture-frost-and-erosion-review | 82 |

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
| 0..30cm | clay | % | 23–32 | 1–49 | 315 |
| 0..30cm | sand | % | 38–56 | 8–93 | 315 |
| 0..30cm | silt | % | 20–30 | 0–50 | 315 |
| 0..30cm | bd.core | kg/m3 | 1270–1480 | 990–1680 | 315 |
| 0..30cm | soc | g/kg | 4.2–8 | 1.3–16.6 | 315 |
| 0..30cm | ph.h2o | pH | 6.8–7.5 | 5.7–8.6 | 315 |
| 30..60cm | clay | % | 24–33 | 2–49 | 315 |
| 30..60cm | sand | % | 37–54 | 6–92 | 315 |
| 30..60cm | silt | % | 22–31 | 0–50 | 315 |
| 30..60cm | bd.core | kg/m3 | 1310–1530 | 1010–1710 | 315 |
| 30..60cm | soc | g/kg | 2.7–4.4 | 0.8–10.3 | 315 |
| 30..60cm | ph.h2o | pH | 7.1–7.6 | 5.7–8.8 | 315 |
| 60..100cm | clay | % | 25–33 | 1–49 | 315 |
| 60..100cm | sand | % | 37–53 | 5–92 | 315 |
| 60..100cm | silt | % | 22–31 | 0–54 | 315 |
| 60..100cm | bd.core | kg/m3 | 1370–1560 | 1000–1830 | 315 |
| 60..100cm | soc | g/kg | 2.3–3.5 | 0.6–9 | 315 |
| 60..100cm | ph.h2o | pH | 7.2–7.7 | 5.7–8.8 | 315 |
