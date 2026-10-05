# Taif civil soil screening

138 route/station sample locations; 91 complete profiles; 47 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 47 |
| fine-soil-plasticity-and-shrink-swell-tests | 89 |
| granular-density-and-groundwater-tests | 91 |

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
| 0..30cm | clay | % | 18–26 | 6–39 | 91 |
| 0..30cm | sand | % | 49–63 | 25–87 | 91 |
| 0..30cm | silt | % | 19–25 | 5–39 | 91 |
| 0..30cm | bd.core | kg/m3 | 1440–1500 | 1300–1630 | 91 |
| 0..30cm | soc | g/kg | 2.3–4.8 | 0.7–10.5 | 91 |
| 0..30cm | ph.h2o | pH | 8–8.6 | 7.6–9.3 | 91 |
| 30..60cm | clay | % | 20–27 | 5–42 | 91 |
| 30..60cm | sand | % | 47–62 | 17–92 | 91 |
| 30..60cm | silt | % | 19–27 | 3–41 | 91 |
| 30..60cm | bd.core | kg/m3 | 1470–1540 | 1290–1720 | 91 |
| 30..60cm | soc | g/kg | 1.6–3.4 | 0.3–6.4 | 91 |
| 30..60cm | ph.h2o | pH | 8.3–8.8 | 7.7–9.4 | 91 |
| 60..100cm | clay | % | 20–27 | 5–42 | 91 |
| 60..100cm | sand | % | 47–62 | 16–91 | 91 |
| 60..100cm | silt | % | 18–27 | 2–44 | 91 |
| 60..100cm | bd.core | kg/m3 | 1460–1580 | 1240–1770 | 91 |
| 60..100cm | soc | g/kg | 1.3–2.6 | 0–4.8 | 91 |
| 60..100cm | ph.h2o | pH | 8.3–8.8 | 7.8–9.7 | 91 |
