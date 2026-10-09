# Gaza-City civil soil screening

400 route/station sample locations; 400 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 400 |
| granular-density-and-groundwater-tests | 394 |

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
| 0..30cm | clay | % | 21–28 | 3–44 | 400 |
| 0..30cm | sand | % | 42–57 | 16–91 | 400 |
| 0..30cm | silt | % | 21–30 | 5–45 | 400 |
| 0..30cm | bd.core | kg/m3 | 1360–1440 | 1130–1680 | 400 |
| 0..30cm | soc | g/kg | 2.8–10.5 | 1.1–22.6 | 400 |
| 0..30cm | ph.h2o | pH | 7.5–7.7 | 6.8–8.3 | 400 |
| 30..60cm | clay | % | 23–30 | 4–45 | 400 |
| 30..60cm | sand | % | 41–57 | 14–91 | 400 |
| 30..60cm | silt | % | 19–29 | 0–46 | 400 |
| 30..60cm | bd.core | kg/m3 | 1470–1570 | 1060–1870 | 400 |
| 30..60cm | soc | g/kg | 2.3–6 | 0.7–13.4 | 400 |
| 30..60cm | ph.h2o | pH | 7.4–7.8 | 6.7–8.6 | 400 |
| 60..100cm | clay | % | 23–31 | 5–47 | 400 |
| 60..100cm | sand | % | 39–57 | 10–91 | 400 |
| 60..100cm | silt | % | 19–31 | 0–49 | 400 |
| 60..100cm | bd.core | kg/m3 | 1460–1580 | 950–1880 | 400 |
| 60..100cm | soc | g/kg | 1.7–3.7 | 0.3–7.7 | 400 |
| 60..100cm | ph.h2o | pH | 7.4–7.8 | 6.7–8.7 | 400 |
