# Sylhet civil soil screening

2,232 route/station sample locations; 2,232 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 2232 |
| fine-soil-plasticity-and-shrink-swell-tests | 2232 |
| granular-density-and-groundwater-tests | 1079 |
| organic-content-and-compressibility-tests | 858 |

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
| 0..30cm | clay | % | 24–32 | 10–49 | 2232 |
| 0..30cm | sand | % | 38–53 | 11–77 | 2232 |
| 0..30cm | silt | % | 23–31 | 7–48 | 2232 |
| 0..30cm | bd.core | kg/m3 | 830–1170 | 440–1450 | 2232 |
| 0..30cm | soc | g/kg | 9.7–25.2 | 3.3–96.2 | 2232 |
| 0..30cm | ph.h2o | pH | 5.3–5.9 | 4.4–7.2 | 2232 |
| 30..60cm | clay | % | 24–33 | 8–49 | 2232 |
| 30..60cm | sand | % | 37–52 | 10–81 | 2232 |
| 30..60cm | silt | % | 23–31 | 3–47 | 2232 |
| 30..60cm | bd.core | kg/m3 | 900–1210 | 520–1530 | 2232 |
| 30..60cm | soc | g/kg | 5.3–18.2 | 1.7–56.1 | 2232 |
| 30..60cm | ph.h2o | pH | 5.5–6.1 | 4.6–7.3 | 2232 |
| 60..100cm | clay | % | 26–34 | 7–53 | 2232 |
| 60..100cm | sand | % | 36–50 | 10–80 | 2232 |
| 60..100cm | silt | % | 23–31 | 4–48 | 2232 |
| 60..100cm | bd.core | kg/m3 | 930–1240 | 330–1580 | 2232 |
| 60..100cm | soc | g/kg | 5.1–15.6 | 1.1–72.7 | 2232 |
| 60..100cm | ph.h2o | pH | 5.6–6.1 | 4.6–7.3 | 2232 |
