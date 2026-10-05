# Jizan civil soil screening

91 route/station sample locations; 62 complete profiles; 29 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 29 |
| fine-soil-plasticity-and-shrink-swell-tests | 1 |
| granular-density-and-groundwater-tests | 62 |

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
| 0..30cm | clay | % | 9–16 | 0–31 | 62 |
| 0..30cm | sand | % | 63–78 | 32–91 | 62 |
| 0..30cm | silt | % | 13–22 | 1–40 | 62 |
| 0..30cm | bd.core | kg/m3 | 1410–1480 | 1080–1710 | 62 |
| 0..30cm | soc | g/kg | 2.9–9 | 1–27.8 | 62 |
| 0..30cm | ph.h2o | pH | 8.3–8.6 | 7.6–9.6 | 62 |
| 30..60cm | clay | % | 10–19 | 0–34 | 62 |
| 30..60cm | sand | % | 59–77 | 26–92 | 62 |
| 30..60cm | silt | % | 12–23 | 0–39 | 62 |
| 30..60cm | bd.core | kg/m3 | 1470–1540 | 1250–1720 | 62 |
| 30..60cm | soc | g/kg | 1.9–8.5 | 0.3–48.4 | 62 |
| 30..60cm | ph.h2o | pH | 8.3–8.6 | 7.7–9.4 | 62 |
| 60..100cm | clay | % | 10–19 | 0–35 | 62 |
| 60..100cm | sand | % | 58–76 | 30–93 | 62 |
| 60..100cm | silt | % | 13–23 | 0–39 | 62 |
| 60..100cm | bd.core | kg/m3 | 1470–1580 | 1250–1790 | 62 |
| 60..100cm | soc | g/kg | 1.5–5.5 | 0.1–33.9 | 62 |
| 60..100cm | ph.h2o | pH | 8.3–8.7 | 7.9–9.5 | 62 |
