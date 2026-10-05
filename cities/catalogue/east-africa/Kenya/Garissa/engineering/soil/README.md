# Garissa civil soil screening

70 route/station sample locations; 70 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 9 |
| granular-density-and-groundwater-tests | 65 |

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
| 0..30cm | clay | % | 17–29 | 10–42 | 70 |
| 0..30cm | sand | % | 38–62 | 11–76 | 70 |
| 0..30cm | silt | % | 21–33 | 11–45 | 70 |
| 0..30cm | bd.core | kg/m3 | 1430–1490 | 1250–1640 | 70 |
| 0..30cm | soc | g/kg | 4.3–6.5 | 1.5–12.9 | 70 |
| 0..30cm | ph.h2o | pH | 7.1–8.4 | 5.8–9.1 | 70 |
| 30..60cm | clay | % | 19–29 | 11–45 | 70 |
| 30..60cm | sand | % | 39–58 | 14–71 | 70 |
| 30..60cm | silt | % | 22–32 | 9–46 | 70 |
| 30..60cm | bd.core | kg/m3 | 1440–1530 | 1250–1720 | 70 |
| 30..60cm | soc | g/kg | 2.7–3.9 | 1.3–6.7 | 70 |
| 30..60cm | ph.h2o | pH | 7.1–8.4 | 5.7–9.3 | 70 |
| 60..100cm | clay | % | 21–28 | 10–45 | 70 |
| 60..100cm | sand | % | 41–55 | 12–75 | 70 |
| 60..100cm | silt | % | 23–31 | 9–49 | 70 |
| 60..100cm | bd.core | kg/m3 | 1410–1530 | 1200–1750 | 70 |
| 60..100cm | soc | g/kg | 2.3–2.9 | 1–6.1 | 70 |
| 60..100cm | ph.h2o | pH | 7–8.4 | 5.6–9.3 | 70 |
