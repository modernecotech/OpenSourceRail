# East-London-Za civil soil screening

1,242 route/station sample locations; 1,242 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1232 |
| fine-soil-plasticity-and-shrink-swell-tests | 1242 |
| granular-density-and-groundwater-tests | 1242 |
| organic-content-and-compressibility-tests | 14 |

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
| 0..30cm | clay | % | 18–30 | 2–45 | 1242 |
| 0..30cm | sand | % | 47–70 | 18–97 | 1242 |
| 0..30cm | silt | % | 12–23 | 0–38 | 1242 |
| 0..30cm | bd.core | kg/m3 | 970–1330 | 670–1510 | 1242 |
| 0..30cm | soc | g/kg | 5.1–23.7 | 2–55.7 | 1242 |
| 0..30cm | ph.h2o | pH | 5.6–6.6 | 4.8–8 | 1242 |
| 30..60cm | clay | % | 19–33 | 1–48 | 1242 |
| 30..60cm | sand | % | 47–72 | 17–97 | 1242 |
| 30..60cm | silt | % | 9–21 | 0–39 | 1242 |
| 30..60cm | bd.core | kg/m3 | 1120–1450 | 740–1640 | 1242 |
| 30..60cm | soc | g/kg | 3.3–9.7 | 0.8–21.4 | 1242 |
| 30..60cm | ph.h2o | pH | 5.9–6.8 | 5–8 | 1242 |
| 60..100cm | clay | % | 19–34 | 2–49 | 1242 |
| 60..100cm | sand | % | 46–72 | 13–97 | 1242 |
| 60..100cm | silt | % | 9–21 | 0–38 | 1242 |
| 60..100cm | bd.core | kg/m3 | 1100–1500 | 720–1730 | 1242 |
| 60..100cm | soc | g/kg | 2.3–7.5 | 0.2–15.6 | 1242 |
| 60..100cm | ph.h2o | pH | 6.1–7.1 | 4.9–8.7 | 1242 |
