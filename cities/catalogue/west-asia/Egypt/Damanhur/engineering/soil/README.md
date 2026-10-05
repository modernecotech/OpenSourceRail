# Damanhur civil soil screening

102 route/station sample locations; 102 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 12 |
| fine-soil-plasticity-and-shrink-swell-tests | 99 |
| granular-density-and-groundwater-tests | 102 |
| organic-content-and-compressibility-tests | 7 |

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
| 0..30cm | clay | % | 17–25 | 5–39 | 102 |
| 0..30cm | sand | % | 48–64 | 16–89 | 102 |
| 0..30cm | silt | % | 18–28 | 6–43 | 102 |
| 0..30cm | bd.core | kg/m3 | 1290–1460 | 1110–1650 | 102 |
| 0..30cm | soc | g/kg | 3.4–15.4 | 1.6–43.4 | 102 |
| 0..30cm | ph.h2o | pH | 7.6–8.4 | 6.8–9.1 | 102 |
| 30..60cm | clay | % | 20–27 | 6–43 | 102 |
| 30..60cm | sand | % | 47–61 | 16–87 | 102 |
| 30..60cm | silt | % | 19–26 | 2–42 | 102 |
| 30..60cm | bd.core | kg/m3 | 1400–1570 | 1130–1800 | 102 |
| 30..60cm | soc | g/kg | 1.9–10.1 | 0.6–44.3 | 102 |
| 30..60cm | ph.h2o | pH | 7.3–8.5 | 5.7–9.4 | 102 |
| 60..100cm | clay | % | 20–27 | 6–43 | 102 |
| 60..100cm | sand | % | 47–62 | 15–87 | 102 |
| 60..100cm | silt | % | 18–26 | 1–43 | 102 |
| 60..100cm | bd.core | kg/m3 | 1370–1580 | 930–1890 | 102 |
| 60..100cm | soc | g/kg | 1.5–13.3 | 0.3–113.8 | 102 |
| 60..100cm | ph.h2o | pH | 7.1–8.5 | 3.5–9.4 | 102 |
