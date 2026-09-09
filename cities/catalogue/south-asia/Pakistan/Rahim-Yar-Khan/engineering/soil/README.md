# Rahim-Yar-Khan civil soil screening

87 route/station sample locations; 87 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 10 |
| granular-density-and-groundwater-tests | 87 |

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
| 0..30cm | clay | % | 13–19 | 2–33 | 87 |
| 0..30cm | sand | % | 54–67 | 32–88 | 87 |
| 0..30cm | silt | % | 20–27 | 8–39 | 87 |
| 0..30cm | bd.core | kg/m3 | 1460–1560 | 1310–1710 | 87 |
| 0..30cm | soc | g/kg | 2.7–5.5 | 0.8–13.5 | 87 |
| 0..30cm | ph.h2o | pH | 7.9–8.3 | 6.6–9.2 | 87 |
| 30..60cm | clay | % | 15–21 | 1–37 | 87 |
| 30..60cm | sand | % | 51–63 | 19–89 | 87 |
| 30..60cm | silt | % | 21–28 | 7–45 | 87 |
| 30..60cm | bd.core | kg/m3 | 1490–1600 | 1310–1790 | 87 |
| 30..60cm | soc | g/kg | 1.7–2.7 | 0.4–7.4 | 87 |
| 30..60cm | ph.h2o | pH | 8–8.6 | 6.5–9.3 | 87 |
| 60..100cm | clay | % | 16–21 | 1–36 | 87 |
| 60..100cm | sand | % | 50–62 | 19–87 | 87 |
| 60..100cm | silt | % | 22–29 | 6–46 | 87 |
| 60..100cm | bd.core | kg/m3 | 1490–1630 | 1260–1820 | 87 |
| 60..100cm | soc | g/kg | 1.5–2.2 | 0.2–5.6 | 87 |
| 60..100cm | ph.h2o | pH | 8–8.7 | 6.5–9.6 | 87 |
