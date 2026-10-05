# Gaza-City civil soil screening

60 route/station sample locations; 60 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 60 |
| granular-density-and-groundwater-tests | 57 |

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
| 0..30cm | clay | % | 22–28 | 5–44 | 60 |
| 0..30cm | sand | % | 42–54 | 18–85 | 60 |
| 0..30cm | silt | % | 24–30 | 8–44 | 60 |
| 0..30cm | bd.core | kg/m3 | 1370–1440 | 1160–1670 | 60 |
| 0..30cm | soc | g/kg | 3.1–9.5 | 1.1–17.7 | 60 |
| 0..30cm | ph.h2o | pH | 7.5–7.7 | 6.9–8.3 | 60 |
| 30..60cm | clay | % | 24–30 | 4–45 | 60 |
| 30..60cm | sand | % | 41–53 | 14–88 | 60 |
| 30..60cm | silt | % | 23–29 | 4–46 | 60 |
| 30..60cm | bd.core | kg/m3 | 1490–1560 | 1140–1830 | 60 |
| 30..60cm | soc | g/kg | 2.3–5.8 | 0.8–13.4 | 60 |
| 30..60cm | ph.h2o | pH | 7.5–7.8 | 6.8–8.6 | 60 |
| 60..100cm | clay | % | 24–31 | 6–47 | 60 |
| 60..100cm | sand | % | 40–52 | 10–88 | 60 |
| 60..100cm | silt | % | 23–30 | 3–48 | 60 |
| 60..100cm | bd.core | kg/m3 | 1460–1580 | 1150–1860 | 60 |
| 60..100cm | soc | g/kg | 1.7–3.5 | 0.4–7.7 | 60 |
| 60..100cm | ph.h2o | pH | 7.6–7.8 | 6.7–8.7 | 60 |
