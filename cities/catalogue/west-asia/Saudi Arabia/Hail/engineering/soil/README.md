# Hail civil soil screening

97 route/station sample locations; 64 complete profiles; 33 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 33 |
| fine-soil-plasticity-and-shrink-swell-tests | 29 |
| granular-density-and-groundwater-tests | 64 |

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
| 0..30cm | clay | % | 14–25 | 2–38 | 64 |
| 0..30cm | sand | % | 40–62 | 14–84 | 64 |
| 0..30cm | silt | % | 24–34 | 10–47 | 64 |
| 0..30cm | bd.core | kg/m3 | 1450–1520 | 1280–1670 | 64 |
| 0..30cm | soc | g/kg | 1.7–3.7 | 0.3–9.1 | 64 |
| 0..30cm | ph.h2o | pH | 8.2–8.6 | 7.5–9.5 | 64 |
| 30..60cm | clay | % | 16–27 | 2–40 | 64 |
| 30..60cm | sand | % | 42–62 | 16–91 | 64 |
| 30..60cm | silt | % | 22–32 | 5–45 | 64 |
| 30..60cm | bd.core | kg/m3 | 1430–1570 | 1230–1800 | 64 |
| 30..60cm | soc | g/kg | 1.2–2.5 | 0–6 | 64 |
| 30..60cm | ph.h2o | pH | 8.4–8.9 | 7.6–9.9 | 64 |
| 60..100cm | clay | % | 15–26 | 1–39 | 64 |
| 60..100cm | sand | % | 42–63 | 17–91 | 64 |
| 60..100cm | silt | % | 22–32 | 6–47 | 64 |
| 60..100cm | bd.core | kg/m3 | 1470–1620 | 1240–1820 | 64 |
| 60..100cm | soc | g/kg | 1–1.9 | 0–5.4 | 64 |
| 60..100cm | ph.h2o | pH | 8.4–9 | 7.7–10.1 | 64 |
