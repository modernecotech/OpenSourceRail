# Hail civil soil screening

2,359 route/station sample locations; 1,563 complete profiles; 796 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 796 |
| fine-soil-plasticity-and-shrink-swell-tests | 795 |
| granular-density-and-groundwater-tests | 1562 |

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
| 0..30cm | clay | % | 13–25 | 2–38 | 1563 |
| 0..30cm | sand | % | 40–64 | 14–85 | 1563 |
| 0..30cm | silt | % | 22–35 | 9–48 | 1563 |
| 0..30cm | bd.core | kg/m3 | 1420–1520 | 1160–1680 | 1563 |
| 0..30cm | soc | g/kg | 1.6–4.9 | 0.3–9.5 | 1563 |
| 0..30cm | ph.h2o | pH | 8.1–8.6 | 7.4–9.7 | 1563 |
| 30..60cm | clay | % | 15–26 | 2–42 | 1563 |
| 30..60cm | sand | % | 40–65 | 15–92 | 1563 |
| 30..60cm | silt | % | 20–34 | 4–45 | 1563 |
| 30..60cm | bd.core | kg/m3 | 1430–1580 | 1230–1800 | 1563 |
| 30..60cm | soc | g/kg | 1.1–2.8 | 0–6.5 | 1563 |
| 30..60cm | ph.h2o | pH | 8.3–8.9 | 7.5–10 | 1563 |
| 60..100cm | clay | % | 15–26 | 1–41 | 1563 |
| 60..100cm | sand | % | 40–65 | 15–91 | 1563 |
| 60..100cm | silt | % | 20–34 | 5–49 | 1563 |
| 60..100cm | bd.core | kg/m3 | 1470–1630 | 1240–1840 | 1563 |
| 60..100cm | soc | g/kg | 1–2.1 | 0–7.3 | 1563 |
| 60..100cm | ph.h2o | pH | 8.3–9 | 7.5–10.1 | 1563 |
