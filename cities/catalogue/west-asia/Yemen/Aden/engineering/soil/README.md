# Aden civil soil screening

89 route/station sample locations; 37 complete profiles; 52 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 52 |
| fine-soil-plasticity-and-shrink-swell-tests | 3 |
| granular-density-and-groundwater-tests | 37 |

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
| 0..30cm | clay | % | 12–16 | 0–32 | 37 |
| 0..30cm | sand | % | 62–70 | 28–94 | 37 |
| 0..30cm | silt | % | 18–22 | 3–40 | 37 |
| 0..30cm | bd.core | kg/m3 | 1370–1480 | 1020–1710 | 37 |
| 0..30cm | soc | g/kg | 2.8–8 | 0.6–23.9 | 37 |
| 0..30cm | ph.h2o | pH | 8.3–8.8 | 7.6–9.5 | 37 |
| 30..60cm | clay | % | 12–18 | 0–35 | 37 |
| 30..60cm | sand | % | 59–71 | 27–94 | 37 |
| 30..60cm | silt | % | 17–23 | 0–43 | 37 |
| 30..60cm | bd.core | kg/m3 | 1460–1540 | 1260–1710 | 37 |
| 30..60cm | soc | g/kg | 1.6–7.3 | 0–42 | 37 |
| 30..60cm | ph.h2o | pH | 8.2–8.8 | 7.4–9.5 | 37 |
| 60..100cm | clay | % | 12–19 | 0–35 | 37 |
| 60..100cm | sand | % | 58–70 | 24–96 | 37 |
| 60..100cm | silt | % | 17–23 | 0–43 | 37 |
| 60..100cm | bd.core | kg/m3 | 1510–1560 | 1280–1790 | 37 |
| 60..100cm | soc | g/kg | 1.3–5.3 | 0.1–34 | 37 |
| 60..100cm | ph.h2o | pH | 8.3–8.9 | 7.5–9.5 | 37 |
