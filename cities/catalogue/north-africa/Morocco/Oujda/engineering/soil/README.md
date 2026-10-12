# Oujda civil soil screening

642 route/station sample locations; 642 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 642 |
| granular-density-and-groundwater-tests | 430 |

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
| 0..30cm | clay | % | 22–26 | 11–39 | 642 |
| 0..30cm | sand | % | 42–52 | 19–74 | 642 |
| 0..30cm | silt | % | 26–32 | 14–47 | 642 |
| 0..30cm | bd.core | kg/m3 | 1330–1460 | 1170–1630 | 642 |
| 0..30cm | soc | g/kg | 4.3–9.4 | 2.1–16.2 | 642 |
| 0..30cm | ph.h2o | pH | 7.8–8.1 | 7.3–8.6 | 642 |
| 30..60cm | clay | % | 23–29 | 9–42 | 642 |
| 30..60cm | sand | % | 41–52 | 16–79 | 642 |
| 30..60cm | silt | % | 25–30 | 9–45 | 642 |
| 30..60cm | bd.core | kg/m3 | 1470–1570 | 1290–1770 | 642 |
| 30..60cm | soc | g/kg | 2.8–4.7 | 1.1–8.6 | 642 |
| 30..60cm | ph.h2o | pH | 8–8.4 | 7.6–9 | 642 |
| 60..100cm | clay | % | 24–30 | 10–46 | 642 |
| 60..100cm | sand | % | 41–52 | 14–79 | 642 |
| 60..100cm | silt | % | 24–30 | 7–47 | 642 |
| 60..100cm | bd.core | kg/m3 | 1480–1590 | 1280–1770 | 642 |
| 60..100cm | soc | g/kg | 2.2–3.2 | 0.8–6 | 642 |
| 60..100cm | ph.h2o | pH | 8.1–8.4 | 7.6–9.1 | 642 |
