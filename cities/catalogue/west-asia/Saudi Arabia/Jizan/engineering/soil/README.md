# Jizan civil soil screening

88 route/station sample locations; 73 complete profiles; 15 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 15 |
| fine-soil-plasticity-and-shrink-swell-tests | 1 |
| granular-density-and-groundwater-tests | 73 |

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
| 0..30cm | clay | % | 10–16 | 1–31 | 73 |
| 0..30cm | sand | % | 62–77 | 31–90 | 73 |
| 0..30cm | silt | % | 14–22 | 3–40 | 73 |
| 0..30cm | bd.core | kg/m3 | 1400–1480 | 1080–1710 | 73 |
| 0..30cm | soc | g/kg | 2.9–8.9 | 0.9–29.6 | 73 |
| 0..30cm | ph.h2o | pH | 8.3–8.7 | 7.6–9.6 | 73 |
| 30..60cm | clay | % | 11–19 | 1–35 | 73 |
| 30..60cm | sand | % | 59–76 | 28–92 | 73 |
| 30..60cm | silt | % | 13–24 | 0–40 | 73 |
| 30..60cm | bd.core | kg/m3 | 1470–1540 | 1260–1720 | 73 |
| 30..60cm | soc | g/kg | 1.8–8.9 | 0.3–49 | 73 |
| 30..60cm | ph.h2o | pH | 8.3–8.7 | 7.7–9.4 | 73 |
| 60..100cm | clay | % | 11–19 | 0–34 | 73 |
| 60..100cm | sand | % | 58–75 | 30–92 | 73 |
| 60..100cm | silt | % | 14–25 | 0–39 | 73 |
| 60..100cm | bd.core | kg/m3 | 1510–1580 | 1280–1790 | 73 |
| 60..100cm | soc | g/kg | 1.5–5.7 | 0.1–38.3 | 73 |
| 60..100cm | ph.h2o | pH | 8.3–8.8 | 7.8–9.6 | 73 |
