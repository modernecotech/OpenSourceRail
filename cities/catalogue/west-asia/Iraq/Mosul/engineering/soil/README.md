# Mosul civil soil screening

386 route/station sample locations; 364 complete profiles; 22 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 22 |
| fine-soil-plasticity-and-shrink-swell-tests | 364 |
| granular-density-and-groundwater-tests | 83 |
| silt-moisture-frost-and-erosion-review | 325 |

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
| 0..30cm | clay | % | 19–39 | 4–49 | 364 |
| 0..30cm | sand | % | 20–50 | 5–78 | 364 |
| 0..30cm | silt | % | 30–45 | 13–61 | 364 |
| 0..30cm | bd.core | kg/m3 | 1360–1460 | 1150–1640 | 364 |
| 0..30cm | soc | g/kg | 2.5–6.4 | 0.9–11.2 | 364 |
| 0..30cm | ph.h2o | pH | 7.3–7.7 | 6.7–8.4 | 364 |
| 30..60cm | clay | % | 22–41 | 3–50 | 364 |
| 30..60cm | sand | % | 24–50 | 7–82 | 364 |
| 30..60cm | silt | % | 24–39 | 7–55 | 364 |
| 30..60cm | bd.core | kg/m3 | 1350–1510 | 1140–1710 | 364 |
| 30..60cm | soc | g/kg | 2.5–4.7 | 0.8–9.7 | 364 |
| 30..60cm | ph.h2o | pH | 7.2–8 | 6.4–9.2 | 364 |
| 60..100cm | clay | % | 24–43 | 7–55 | 364 |
| 60..100cm | sand | % | 25–51 | 8–84 | 364 |
| 60..100cm | silt | % | 21–36 | 1–54 | 364 |
| 60..100cm | bd.core | kg/m3 | 1320–1550 | 1060–1830 | 364 |
| 60..100cm | soc | g/kg | 2–3.3 | 0.5–7.7 | 364 |
| 60..100cm | ph.h2o | pH | 7.2–8 | 6.5–9.4 | 364 |
