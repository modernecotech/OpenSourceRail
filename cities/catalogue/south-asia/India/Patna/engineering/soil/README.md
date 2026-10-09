# Patna civil soil screening

2,513 route/station sample locations; 2,511 complete profiles; 2 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 671 |
| coverage-gap | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 2293 |
| granular-density-and-groundwater-tests | 2510 |
| silt-moisture-frost-and-erosion-review | 7 |

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
| 0..30cm | clay | % | 16–27 | 1–41 | 2511 |
| 0..30cm | sand | % | 42–64 | 13–94 | 2511 |
| 0..30cm | silt | % | 20–31 | 1–49 | 2511 |
| 0..30cm | bd.core | kg/m3 | 1290–1490 | 1010–1720 | 2511 |
| 0..30cm | soc | g/kg | 4–11.2 | 1.3–22.9 | 2511 |
| 0..30cm | ph.h2o | pH | 6.2–6.9 | 5.3–8.1 | 2511 |
| 30..60cm | clay | % | 17–29 | 1–44 | 2511 |
| 30..60cm | sand | % | 39–63 | 10–93 | 2511 |
| 30..60cm | silt | % | 21–33 | 2–50 | 2511 |
| 30..60cm | bd.core | kg/m3 | 1350–1580 | 1080–1770 | 2511 |
| 30..60cm | soc | g/kg | 2.2–5.6 | 0.4–15.6 | 2511 |
| 30..60cm | ph.h2o | pH | 6.4–7.1 | 5.3–8.2 | 2511 |
| 60..100cm | clay | % | 17–30 | 1–45 | 2511 |
| 60..100cm | sand | % | 37–61 | 10–95 | 2511 |
| 60..100cm | silt | % | 21–33 | 1–49 | 2511 |
| 60..100cm | bd.core | kg/m3 | 1420–1620 | 1080–1880 | 2511 |
| 60..100cm | soc | g/kg | 1.8–4.4 | 0.4–11.7 | 2511 |
| 60..100cm | ph.h2o | pH | 6.5–7.3 | 5.3–8.5 | 2511 |
