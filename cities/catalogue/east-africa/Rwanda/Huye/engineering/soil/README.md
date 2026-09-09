# Huye civil soil screening

105 route/station sample locations; 105 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 105 |
| fine-soil-plasticity-and-shrink-swell-tests | 105 |
| granular-density-and-groundwater-tests | 3 |

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
| 0..30cm | clay | % | 29–38 | 19–46 | 105 |
| 0..30cm | sand | % | 32–46 | 18–69 | 105 |
| 0..30cm | silt | % | 25–31 | 9–42 | 105 |
| 0..30cm | bd.core | kg/m3 | 1180–1320 | 990–1470 | 105 |
| 0..30cm | soc | g/kg | 13.7–22 | 8.8–38.2 | 105 |
| 0..30cm | ph.h2o | pH | 5.4–5.8 | 4.7–6.8 | 105 |
| 30..60cm | clay | % | 30–39 | 19–49 | 105 |
| 30..60cm | sand | % | 33–46 | 16–70 | 105 |
| 30..60cm | silt | % | 23–29 | 5–44 | 105 |
| 30..60cm | bd.core | kg/m3 | 1260–1360 | 1070–1540 | 105 |
| 30..60cm | soc | g/kg | 7.2–12.3 | 3.5–28.2 | 105 |
| 30..60cm | ph.h2o | pH | 5.7–6.2 | 5–7.3 | 105 |
| 60..100cm | clay | % | 30–39 | 17–49 | 105 |
| 60..100cm | sand | % | 33–47 | 15–71 | 105 |
| 60..100cm | silt | % | 22–29 | 5–43 | 105 |
| 60..100cm | bd.core | kg/m3 | 1260–1350 | 1000–1590 | 105 |
| 60..100cm | soc | g/kg | 5.4–14.6 | 2.3–48.9 | 105 |
| 60..100cm | ph.h2o | pH | 6.1–6.7 | 5.1–8.1 | 105 |
