# Khamis-Mushait civil soil screening

173 route/station sample locations; 170 complete profiles; 3 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 3 |
| fine-soil-plasticity-and-shrink-swell-tests | 169 |
| granular-density-and-groundwater-tests | 168 |

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
| 0..30cm | clay | % | 18–28 | 6–40 | 170 |
| 0..30cm | sand | % | 43–61 | 14–89 | 170 |
| 0..30cm | silt | % | 20–29 | 4–46 | 170 |
| 0..30cm | bd.core | kg/m3 | 1400–1530 | 1190–1730 | 170 |
| 0..30cm | soc | g/kg | 2.4–8.5 | 1.1–15.3 | 170 |
| 0..30cm | ph.h2o | pH | 7.9–8.4 | 6.8–9.2 | 170 |
| 30..60cm | clay | % | 22–29 | 4–44 | 170 |
| 30..60cm | sand | % | 43–57 | 15–90 | 170 |
| 30..60cm | silt | % | 20–27 | 1–44 | 170 |
| 30..60cm | bd.core | kg/m3 | 1470–1530 | 1250–1690 | 170 |
| 30..60cm | soc | g/kg | 1.5–4.9 | 0.1–9.3 | 170 |
| 30..60cm | ph.h2o | pH | 8–8.5 | 7.6–9.3 | 170 |
| 60..100cm | clay | % | 23–31 | 5–44 | 170 |
| 60..100cm | sand | % | 41–57 | 13–88 | 170 |
| 60..100cm | silt | % | 21–28 | 0–45 | 170 |
| 60..100cm | bd.core | kg/m3 | 1470–1560 | 1210–1760 | 170 |
| 60..100cm | soc | g/kg | 1.2–3.4 | 0–6.4 | 170 |
| 60..100cm | ph.h2o | pH | 8–8.6 | 7.5–9.3 | 170 |
