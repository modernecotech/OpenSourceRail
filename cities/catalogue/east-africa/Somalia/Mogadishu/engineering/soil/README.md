# Mogadishu civil soil screening

2,413 route/station sample locations; 2,404 complete profiles; 9 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 5 |
| coverage-gap | 9 |
| fine-soil-plasticity-and-shrink-swell-tests | 48 |
| granular-density-and-groundwater-tests | 2399 |
| silt-moisture-frost-and-erosion-review | 3 |

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
| 0..30cm | clay | % | 6–33 | 2–40 | 2404 |
| 0..30cm | sand | % | 35–85 | 18–92 | 2404 |
| 0..30cm | silt | % | 8–32 | 2–45 | 2404 |
| 0..30cm | bd.core | kg/m3 | 1370–1480 | 1170–1630 | 2404 |
| 0..30cm | soc | g/kg | 3.3–7.5 | 1.3–21 | 2404 |
| 0..30cm | ph.h2o | pH | 6.9–8.3 | 5.1–9.1 | 2404 |
| 30..60cm | clay | % | 6–34 | 1–43 | 2404 |
| 30..60cm | sand | % | 32–84 | 13–93 | 2404 |
| 30..60cm | silt | % | 10–34 | 1–48 | 2404 |
| 30..60cm | bd.core | kg/m3 | 1440–1560 | 1160–1770 | 2404 |
| 30..60cm | soc | g/kg | 2.6–5.6 | 0.7–39.1 | 2404 |
| 30..60cm | ph.h2o | pH | 6.9–8.6 | 4.7–9.3 | 2404 |
| 60..100cm | clay | % | 6–32 | 0–40 | 2404 |
| 60..100cm | sand | % | 32–84 | 14–93 | 2404 |
| 60..100cm | silt | % | 10–36 | 2–52 | 2404 |
| 60..100cm | bd.core | kg/m3 | 1430–1570 | 1150–1790 | 2404 |
| 60..100cm | soc | g/kg | 2.4–4.6 | 0.5–13.5 | 2404 |
| 60..100cm | ph.h2o | pH | 6.9–8.6 | 4.7–9.4 | 2404 |
