# Bamenda civil soil screening

105 route/station sample locations; 105 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 105 |
| fine-soil-plasticity-and-shrink-swell-tests | 105 |
| granular-density-and-groundwater-tests | 76 |
| organic-content-and-compressibility-tests | 10 |

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
| 0..30cm | clay | % | 22–35 | 12–44 | 105 |
| 0..30cm | sand | % | 38–62 | 14–78 | 105 |
| 0..30cm | silt | % | 16–27 | 5–42 | 105 |
| 0..30cm | bd.core | kg/m3 | 930–1180 | 680–1390 | 105 |
| 0..30cm | soc | g/kg | 11.3–36.9 | 3.9–63.4 | 105 |
| 0..30cm | ph.h2o | pH | 5–5.6 | 4.5–6 | 105 |
| 30..60cm | clay | % | 26–37 | 13–50 | 105 |
| 30..60cm | sand | % | 34–58 | 12–79 | 105 |
| 30..60cm | silt | % | 16–28 | 1–43 | 105 |
| 30..60cm | bd.core | kg/m3 | 1090–1330 | 720–1550 | 105 |
| 30..60cm | soc | g/kg | 7.5–16.4 | 2.8–24.5 | 105 |
| 30..60cm | ph.h2o | pH | 5.1–5.6 | 4.5–6 | 105 |
| 60..100cm | clay | % | 27–39 | 13–50 | 105 |
| 60..100cm | sand | % | 32–57 | 11–84 | 105 |
| 60..100cm | silt | % | 16–29 | 0–43 | 105 |
| 60..100cm | bd.core | kg/m3 | 1220–1410 | 840–1640 | 105 |
| 60..100cm | soc | g/kg | 7.9–10.6 | 2.4–19.8 | 105 |
| 60..100cm | ph.h2o | pH | 5.1–5.6 | 4.5–6.1 | 105 |
