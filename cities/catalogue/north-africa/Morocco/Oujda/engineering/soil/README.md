# Oujda civil soil screening

78 route/station sample locations; 78 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 78 |
| granular-density-and-groundwater-tests | 52 |

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
| 0..30cm | clay | % | 22–26 | 11–38 | 78 |
| 0..30cm | sand | % | 42–51 | 20–73 | 78 |
| 0..30cm | silt | % | 27–31 | 14–46 | 78 |
| 0..30cm | bd.core | kg/m3 | 1330–1460 | 1170–1610 | 78 |
| 0..30cm | soc | g/kg | 4.5–9.2 | 2.3–16.7 | 78 |
| 0..30cm | ph.h2o | pH | 7.9–8.1 | 7.4–8.5 | 78 |
| 30..60cm | clay | % | 24–29 | 13–40 | 78 |
| 30..60cm | sand | % | 42–51 | 16–75 | 78 |
| 30..60cm | silt | % | 25–30 | 11–45 | 78 |
| 30..60cm | bd.core | kg/m3 | 1490–1570 | 1290–1770 | 78 |
| 30..60cm | soc | g/kg | 2.9–4.5 | 1.3–8.6 | 78 |
| 30..60cm | ph.h2o | pH | 8.1–8.3 | 7.5–8.8 | 78 |
| 60..100cm | clay | % | 25–30 | 12–44 | 78 |
| 60..100cm | sand | % | 42–51 | 14–77 | 78 |
| 60..100cm | silt | % | 24–29 | 9–46 | 78 |
| 60..100cm | bd.core | kg/m3 | 1480–1560 | 1280–1780 | 78 |
| 60..100cm | soc | g/kg | 2.2–3 | 0.8–5.6 | 78 |
| 60..100cm | ph.h2o | pH | 8.1–8.4 | 7.6–9 | 78 |
