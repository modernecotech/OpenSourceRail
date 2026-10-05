# Lira civil soil screening

70 route/station sample locations; 70 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 35 |
| fine-soil-plasticity-and-shrink-swell-tests | 70 |
| granular-density-and-groundwater-tests | 57 |

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
| 0..30cm | clay | % | 22–33 | 11–44 | 70 |
| 0..30cm | sand | % | 37–57 | 15–80 | 70 |
| 0..30cm | silt | % | 20–29 | 8–43 | 70 |
| 0..30cm | bd.core | kg/m3 | 1230–1320 | 1000–1560 | 70 |
| 0..30cm | soc | g/kg | 7.5–16.7 | 3–28.3 | 70 |
| 0..30cm | ph.h2o | pH | 6.1–6.4 | 5.5–7.1 | 70 |
| 30..60cm | clay | % | 23–35 | 10–48 | 70 |
| 30..60cm | sand | % | 35–55 | 14–80 | 70 |
| 30..60cm | silt | % | 20–30 | 2–47 | 70 |
| 30..60cm | bd.core | kg/m3 | 1280–1360 | 1090–1590 | 70 |
| 30..60cm | soc | g/kg | 4.1–7.7 | 2.1–12.9 | 70 |
| 30..60cm | ph.h2o | pH | 6.1–6.5 | 5.4–7.2 | 70 |
| 60..100cm | clay | % | 24–35 | 9–48 | 70 |
| 60..100cm | sand | % | 35–54 | 12–82 | 70 |
| 60..100cm | silt | % | 20–30 | 3–47 | 70 |
| 60..100cm | bd.core | kg/m3 | 1270–1380 | 1000–1630 | 70 |
| 60..100cm | soc | g/kg | 2.9–5.7 | 1.3–11.8 | 70 |
| 60..100cm | ph.h2o | pH | 6.2–6.8 | 5.2–8 | 70 |
