# Suez civil soil screening

136 route/station sample locations; 63 complete profiles; 73 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 73 |
| fine-soil-plasticity-and-shrink-swell-tests | 13 |
| granular-density-and-groundwater-tests | 63 |

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
| 0..30cm | clay | % | 11–21 | 0–38 | 63 |
| 0..30cm | sand | % | 52–74 | 20–94 | 63 |
| 0..30cm | silt | % | 15–26 | 3–42 | 63 |
| 0..30cm | bd.core | kg/m3 | 1460–1520 | 1230–1690 | 63 |
| 0..30cm | soc | g/kg | 1.6–5 | 0.5–16.4 | 63 |
| 0..30cm | ph.h2o | pH | 7.9–8.6 | 6.9–9.4 | 63 |
| 30..60cm | clay | % | 10–22 | 0–39 | 63 |
| 30..60cm | sand | % | 51–76 | 19–97 | 63 |
| 30..60cm | silt | % | 13–27 | 2–44 | 63 |
| 30..60cm | bd.core | kg/m3 | 1470–1560 | 1300–1700 | 63 |
| 30..60cm | soc | g/kg | 1.4–6.6 | 0–42 | 63 |
| 30..60cm | ph.h2o | pH | 8.1–8.8 | 7.2–9.7 | 63 |
| 60..100cm | clay | % | 10–22 | 0–38 | 63 |
| 60..100cm | sand | % | 52–77 | 22–97 | 63 |
| 60..100cm | silt | % | 13–26 | 1–45 | 63 |
| 60..100cm | bd.core | kg/m3 | 1480–1610 | 1260–1880 | 63 |
| 60..100cm | soc | g/kg | 1.2–4.7 | 0–31.5 | 63 |
| 60..100cm | ph.h2o | pH | 8–8.8 | 6.9–9.8 | 63 |
