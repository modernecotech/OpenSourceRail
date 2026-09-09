# Basra civil soil screening

595 route/station sample locations; 401 complete profiles; 194 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 194 |
| fine-soil-plasticity-and-shrink-swell-tests | 381 |
| granular-density-and-groundwater-tests | 341 |
| silt-moisture-frost-and-erosion-review | 58 |

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
| 0..30cm | clay | % | 16–28 | 2–38 | 401 |
| 0..30cm | sand | % | 32–58 | 14–84 | 401 |
| 0..30cm | silt | % | 26–40 | 11–54 | 401 |
| 0..30cm | bd.core | kg/m3 | 1420–1510 | 1190–1730 | 401 |
| 0..30cm | soc | g/kg | 2.4–5.2 | 0.4–12 | 401 |
| 0..30cm | ph.h2o | pH | 7.9–8.4 | 7.1–9.3 | 401 |
| 30..60cm | clay | % | 18–29 | 2–41 | 401 |
| 30..60cm | sand | % | 33–56 | 13–92 | 401 |
| 30..60cm | silt | % | 25–38 | 4–50 | 401 |
| 30..60cm | bd.core | kg/m3 | 1380–1510 | 1090–1770 | 401 |
| 30..60cm | soc | g/kg | 1.4–3.9 | 0–9 | 401 |
| 30..60cm | ph.h2o | pH | 8.3–8.6 | 7.2–10.2 | 401 |
| 60..100cm | clay | % | 18–29 | 2–41 | 401 |
| 60..100cm | sand | % | 33–56 | 10–92 | 401 |
| 60..100cm | silt | % | 26–38 | 4–52 | 401 |
| 60..100cm | bd.core | kg/m3 | 1340–1500 | 1090–1770 | 401 |
| 60..100cm | soc | g/kg | 1.4–5.2 | 0–14.6 | 401 |
| 60..100cm | ph.h2o | pH | 8.3–8.7 | 7.2–10.3 | 401 |
