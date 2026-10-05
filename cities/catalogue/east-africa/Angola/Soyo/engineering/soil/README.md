# Soyo civil soil screening

72 route/station sample locations; 72 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 72 |
| granular-density-and-groundwater-tests | 72 |
| organic-content-and-compressibility-tests | 23 |

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
| 0..30cm | clay | % | 21–27 | 2–42 | 72 |
| 0..30cm | sand | % | 51–63 | 24–95 | 72 |
| 0..30cm | silt | % | 15–22 | 0–41 | 72 |
| 0..30cm | bd.core | kg/m3 | 900–1390 | 580–1620 | 72 |
| 0..30cm | soc | g/kg | 5.4–22.8 | 2.4–56.6 | 72 |
| 0..30cm | ph.h2o | pH | 6.5–7 | 5.5–8.1 | 72 |
| 30..60cm | clay | % | 20–28 | 3–44 | 72 |
| 30..60cm | sand | % | 50–64 | 19–95 | 72 |
| 30..60cm | silt | % | 15–23 | 0–41 | 72 |
| 30..60cm | bd.core | kg/m3 | 1020–1470 | 630–1630 | 72 |
| 30..60cm | soc | g/kg | 3.7–20.3 | 1.5–57.7 | 72 |
| 30..60cm | ph.h2o | pH | 6.8–7.2 | 5.6–8.2 | 72 |
| 60..100cm | clay | % | 20–28 | 3–44 | 72 |
| 60..100cm | sand | % | 50–64 | 14–95 | 72 |
| 60..100cm | silt | % | 16–23 | 0–43 | 72 |
| 60..100cm | bd.core | kg/m3 | 1010–1480 | 600–1750 | 72 |
| 60..100cm | soc | g/kg | 3.5–18.3 | 0.8–106.2 | 72 |
| 60..100cm | ph.h2o | pH | 7–7.3 | 5.5–8.4 | 72 |
