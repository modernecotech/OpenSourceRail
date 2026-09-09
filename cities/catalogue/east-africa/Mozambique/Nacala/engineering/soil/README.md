# Nacala civil soil screening

89 route/station sample locations; 84 complete profiles; 5 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 14 |
| coverage-gap | 5 |
| fine-soil-plasticity-and-shrink-swell-tests | 84 |
| granular-density-and-groundwater-tests | 84 |

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
| 0..30cm | clay | % | 21–28 | 5–42 | 84 |
| 0..30cm | sand | % | 55–71 | 23–95 | 84 |
| 0..30cm | silt | % | 8–17 | 0–32 | 84 |
| 0..30cm | bd.core | kg/m3 | 1290–1450 | 1050–1600 | 84 |
| 0..30cm | soc | g/kg | 5.3–8.5 | 1.8–16.5 | 84 |
| 0..30cm | ph.h2o | pH | 6.4–6.7 | 5.4–7.9 | 84 |
| 30..60cm | clay | % | 23–30 | 4–50 | 84 |
| 30..60cm | sand | % | 53–70 | 19–94 | 84 |
| 30..60cm | silt | % | 7–17 | 0–34 | 84 |
| 30..60cm | bd.core | kg/m3 | 1290–1530 | 970–1660 | 84 |
| 30..60cm | soc | g/kg | 3.2–5.5 | 1.2–11.5 | 84 |
| 30..60cm | ph.h2o | pH | 6.5–7 | 5.4–8 | 84 |
| 60..100cm | clay | % | 23–29 | 5–47 | 84 |
| 60..100cm | sand | % | 52–69 | 20–94 | 84 |
| 60..100cm | silt | % | 8–18 | 0–40 | 84 |
| 60..100cm | bd.core | kg/m3 | 1200–1570 | 730–1750 | 84 |
| 60..100cm | soc | g/kg | 2.9–4.1 | 0.9–10.3 | 84 |
| 60..100cm | ph.h2o | pH | 6.7–7.2 | 5.3–8.6 | 84 |
