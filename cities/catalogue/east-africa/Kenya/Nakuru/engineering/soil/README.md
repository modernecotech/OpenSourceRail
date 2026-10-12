# Nakuru civil soil screening

1,533 route/station sample locations; 1,533 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 24 |
| fine-soil-plasticity-and-shrink-swell-tests | 1047 |
| granular-density-and-groundwater-tests | 1251 |

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
| 0..30cm | clay | % | 21–37 | 11–49 | 1533 |
| 0..30cm | sand | % | 32–62 | 10–83 | 1533 |
| 0..30cm | silt | % | 17–32 | 5–45 | 1533 |
| 0..30cm | bd.core | kg/m3 | 1200–1320 | 1010–1510 | 1533 |
| 0..30cm | soc | g/kg | 6.7–20.6 | 2.9–40.4 | 1533 |
| 0..30cm | ph.h2o | pH | 6.1–7.5 | 5–8.3 | 1533 |
| 30..60cm | clay | % | 20–37 | 10–51 | 1533 |
| 30..60cm | sand | % | 33–63 | 8–83 | 1533 |
| 30..60cm | silt | % | 16–31 | 3–48 | 1533 |
| 30..60cm | bd.core | kg/m3 | 1200–1340 | 980–1530 | 1533 |
| 30..60cm | soc | g/kg | 5–10.8 | 2.4–18.3 | 1533 |
| 30..60cm | ph.h2o | pH | 6.1–7.6 | 5.3–8.4 | 1533 |
| 60..100cm | clay | % | 16–37 | 7–51 | 1533 |
| 60..100cm | sand | % | 34–70 | 8–86 | 1533 |
| 60..100cm | silt | % | 13–31 | 0–48 | 1533 |
| 60..100cm | bd.core | kg/m3 | 1190–1360 | 950–1580 | 1533 |
| 60..100cm | soc | g/kg | 3.2–7.8 | 1.4–14.3 | 1533 |
| 60..100cm | ph.h2o | pH | 6.2–7.7 | 5.2–8.6 | 1533 |
