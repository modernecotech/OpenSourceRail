# Amman civil soil screening

2,594 route/station sample locations; 2,531 complete profiles; 63 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 63 |
| fine-soil-plasticity-and-shrink-swell-tests | 2525 |
| granular-density-and-groundwater-tests | 1761 |
| silt-moisture-frost-and-erosion-review | 499 |

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
| 0..30cm | clay | % | 18–31 | 5–44 | 2531 |
| 0..30cm | sand | % | 33–56 | 8–85 | 2531 |
| 0..30cm | silt | % | 24–37 | 7–54 | 2531 |
| 0..30cm | bd.core | kg/m3 | 1340–1460 | 1130–1630 | 2531 |
| 0..30cm | soc | g/kg | 2.3–12.5 | 0.8–28.1 | 2531 |
| 0..30cm | ph.h2o | pH | 7.4–8 | 6.8–8.8 | 2531 |
| 30..60cm | clay | % | 19–32 | 3–47 | 2531 |
| 30..60cm | sand | % | 32–57 | 9–87 | 2531 |
| 30..60cm | silt | % | 21–36 | 3–52 | 2531 |
| 30..60cm | bd.core | kg/m3 | 1420–1580 | 1230–1790 | 2531 |
| 30..60cm | soc | g/kg | 1.5–5.2 | 0.2–13 | 2531 |
| 30..60cm | ph.h2o | pH | 7.4–8.3 | 6.6–9.3 | 2531 |
| 60..100cm | clay | % | 19–34 | 3–48 | 2531 |
| 60..100cm | sand | % | 32–58 | 8–89 | 2531 |
| 60..100cm | silt | % | 20–36 | 0–54 | 2531 |
| 60..100cm | bd.core | kg/m3 | 1430–1610 | 1230–1840 | 2531 |
| 60..100cm | soc | g/kg | 1.3–3.7 | 0.1–8.2 | 2531 |
| 60..100cm | ph.h2o | pH | 7.4–8.4 | 6.5–9.5 | 2531 |
