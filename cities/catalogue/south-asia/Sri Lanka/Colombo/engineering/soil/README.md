# Colombo civil soil screening

963 route/station sample locations; 955 complete profiles; 8 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 955 |
| coverage-gap | 8 |
| fine-soil-plasticity-and-shrink-swell-tests | 955 |
| granular-density-and-groundwater-tests | 886 |
| organic-content-and-compressibility-tests | 381 |

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
| 0..30cm | clay | % | 20–37 | 3–49 | 955 |
| 0..30cm | sand | % | 35–62 | 12–95 | 955 |
| 0..30cm | silt | % | 18–29 | 0–46 | 955 |
| 0..30cm | bd.core | kg/m3 | 340–1320 | 140–1560 | 955 |
| 0..30cm | soc | g/kg | 8.5–104.5 | 3.1–271.6 | 955 |
| 0..30cm | ph.h2o | pH | 5.2–5.8 | 4.2–6.9 | 955 |
| 30..60cm | clay | % | 21–40 | 1–54 | 955 |
| 30..60cm | sand | % | 34–63 | 6–94 | 955 |
| 30..60cm | silt | % | 16–29 | 0–46 | 955 |
| 30..60cm | bd.core | kg/m3 | 350–1410 | 150–1630 | 955 |
| 30..60cm | soc | g/kg | 4.1–65 | 1.2–170.3 | 955 |
| 30..60cm | ph.h2o | pH | 5.2–6 | 4.2–7.3 | 955 |
| 60..100cm | clay | % | 22–40 | 1–55 | 955 |
| 60..100cm | sand | % | 33–61 | 3–94 | 955 |
| 60..100cm | silt | % | 17–30 | 0–48 | 955 |
| 60..100cm | bd.core | kg/m3 | 370–1450 | 170–1710 | 955 |
| 60..100cm | soc | g/kg | 3.8–43 | 1.3–376.7 | 955 |
| 60..100cm | ph.h2o | pH | 5.3–6.1 | 4.3–7.9 | 955 |
