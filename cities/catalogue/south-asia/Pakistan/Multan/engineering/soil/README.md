# Multan civil soil screening

236 route/station sample locations; 236 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 40 |
| granular-density-and-groundwater-tests | 236 |

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
| 0..30cm | clay | % | 13–21 | 2–33 | 236 |
| 0..30cm | sand | % | 50–66 | 23–90 | 236 |
| 0..30cm | silt | % | 19–29 | 6–44 | 236 |
| 0..30cm | bd.core | kg/m3 | 1460–1560 | 1270–1700 | 236 |
| 0..30cm | soc | g/kg | 3.2–5.5 | 1–14.3 | 236 |
| 0..30cm | ph.h2o | pH | 7.6–8.4 | 6.8–9 | 236 |
| 30..60cm | clay | % | 14–23 | 2–36 | 236 |
| 30..60cm | sand | % | 49–66 | 18–91 | 236 |
| 30..60cm | silt | % | 20–29 | 3–47 | 236 |
| 30..60cm | bd.core | kg/m3 | 1510–1600 | 1270–1810 | 236 |
| 30..60cm | soc | g/kg | 2–3.3 | 0.3–7.3 | 236 |
| 30..60cm | ph.h2o | pH | 7.8–8.7 | 7–9.5 | 236 |
| 60..100cm | clay | % | 14–22 | 1–35 | 236 |
| 60..100cm | sand | % | 51–66 | 17–92 | 236 |
| 60..100cm | silt | % | 19–28 | 3–45 | 236 |
| 60..100cm | bd.core | kg/m3 | 1520–1630 | 1310–1910 | 236 |
| 60..100cm | soc | g/kg | 1.6–2.8 | 0.2–6 | 236 |
| 60..100cm | ph.h2o | pH | 7.9–8.8 | 7–9.6 | 236 |
