# Kisii civil soil screening

820 route/station sample locations; 820 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 820 |
| fine-soil-plasticity-and-shrink-swell-tests | 820 |
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
| 0..30cm | clay | % | 40–49 | 24–57 | 820 |
| 0..30cm | sand | % | 23–42 | 11–67 | 820 |
| 0..30cm | silt | % | 18–28 | 4–39 | 820 |
| 0..30cm | bd.core | kg/m3 | 1080–1220 | 870–1470 | 820 |
| 0..30cm | soc | g/kg | 9.4–30.1 | 4.9–57.6 | 820 |
| 0..30cm | ph.h2o | pH | 5.5–5.9 | 5.1–6.5 | 820 |
| 30..60cm | clay | % | 40–50 | 23–57 | 820 |
| 30..60cm | sand | % | 19–39 | 8–67 | 820 |
| 30..60cm | silt | % | 21–32 | 6–44 | 820 |
| 30..60cm | bd.core | kg/m3 | 1100–1260 | 910–1460 | 820 |
| 30..60cm | soc | g/kg | 7.2–15.6 | 2.9–30.1 | 820 |
| 30..60cm | ph.h2o | pH | 5.5–5.9 | 5–6.4 | 820 |
| 60..100cm | clay | % | 39–50 | 21–58 | 820 |
| 60..100cm | sand | % | 19–39 | 8–67 | 820 |
| 60..100cm | silt | % | 22–32 | 6–44 | 820 |
| 60..100cm | bd.core | kg/m3 | 1130–1290 | 930–1520 | 820 |
| 60..100cm | soc | g/kg | 5.8–11.2 | 2.2–21.2 | 820 |
| 60..100cm | ph.h2o | pH | 5.4–5.9 | 4.9–6.4 | 820 |
