# Medina civil soil screening

359 route/station sample locations; 328 complete profiles; 31 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 31 |
| fine-soil-plasticity-and-shrink-swell-tests | 11 |
| granular-density-and-groundwater-tests | 328 |
| silt-moisture-frost-and-erosion-review | 21 |

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
| 0..30cm | clay | % | 12–21 | 0–34 | 328 |
| 0..30cm | sand | % | 48–65 | 18–89 | 328 |
| 0..30cm | silt | % | 22–31 | 7–46 | 328 |
| 0..30cm | bd.core | kg/m3 | 1330–1490 | 1080–1720 | 328 |
| 0..30cm | soc | g/kg | 2–5.2 | 0.4–12.9 | 328 |
| 0..30cm | ph.h2o | pH | 7.9–9 | 6.3–9.7 | 328 |
| 30..60cm | clay | % | 13–21 | 0–36 | 328 |
| 30..60cm | sand | % | 48–65 | 12–92 | 328 |
| 30..60cm | silt | % | 22–31 | 4–50 | 328 |
| 30..60cm | bd.core | kg/m3 | 1420–1570 | 1180–1760 | 328 |
| 30..60cm | soc | g/kg | 1.3–3.4 | 0–9.9 | 328 |
| 30..60cm | ph.h2o | pH | 8–9.1 | 6.7–9.9 | 328 |
| 60..100cm | clay | % | 13–21 | 0–39 | 328 |
| 60..100cm | sand | % | 48–63 | 11–92 | 328 |
| 60..100cm | silt | % | 23–31 | 4–54 | 328 |
| 60..100cm | bd.core | kg/m3 | 1460–1600 | 1230–1890 | 328 |
| 60..100cm | soc | g/kg | 1.4–3.3 | 0.1–7.9 | 328 |
| 60..100cm | ph.h2o | pH | 8.1–9.1 | 6.8–10.1 | 328 |
