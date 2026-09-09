# Pemba-Mz civil soil screening

104 route/station sample locations; 102 complete profiles; 2 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 28 |
| coverage-gap | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 102 |
| granular-density-and-groundwater-tests | 102 |

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
| 0..30cm | clay | % | 21–27 | 5–41 | 102 |
| 0..30cm | sand | % | 58–71 | 29–93 | 102 |
| 0..30cm | silt | % | 9–15 | 0–31 | 102 |
| 0..30cm | bd.core | kg/m3 | 1280–1460 | 1020–1610 | 102 |
| 0..30cm | soc | g/kg | 5.4–10.4 | 2.8–20.9 | 102 |
| 0..30cm | ph.h2o | pH | 6.3–6.7 | 5.3–8 | 102 |
| 30..60cm | clay | % | 22–30 | 6–44 | 102 |
| 30..60cm | sand | % | 54–70 | 23–93 | 102 |
| 30..60cm | silt | % | 8–15 | 0–36 | 102 |
| 30..60cm | bd.core | kg/m3 | 1260–1530 | 990–1710 | 102 |
| 30..60cm | soc | g/kg | 3.6–5.5 | 1.8–10.2 | 102 |
| 30..60cm | ph.h2o | pH | 6.5–6.9 | 5.6–7.9 | 102 |
| 60..100cm | clay | % | 22–31 | 5–46 | 102 |
| 60..100cm | sand | % | 53–69 | 27–93 | 102 |
| 60..100cm | silt | % | 9–16 | 0–36 | 102 |
| 60..100cm | bd.core | kg/m3 | 1160–1550 | 740–1770 | 102 |
| 60..100cm | soc | g/kg | 2.8–4.8 | 1.3–11.9 | 102 |
| 60..100cm | ph.h2o | pH | 6.8–7.3 | 5.1–8.7 | 102 |
