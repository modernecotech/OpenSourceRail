# Biratnagar civil soil screening

905 route/station sample locations; 905 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 905 |
| fine-soil-plasticity-and-shrink-swell-tests | 843 |
| granular-density-and-groundwater-tests | 905 |

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
| 0..30cm | clay | % | 19–28 | 6–43 | 905 |
| 0..30cm | sand | % | 45–60 | 14–83 | 905 |
| 0..30cm | silt | % | 21–29 | 9–49 | 905 |
| 0..30cm | bd.core | kg/m3 | 1040–1220 | 760–1530 | 905 |
| 0..30cm | soc | g/kg | 8.1–13.8 | 2.6–29.1 | 905 |
| 0..30cm | ph.h2o | pH | 5.9–6.2 | 4.8–7.6 | 905 |
| 30..60cm | clay | % | 18–27 | 4–43 | 905 |
| 30..60cm | sand | % | 47–63 | 15–87 | 905 |
| 30..60cm | silt | % | 19–28 | 6–47 | 905 |
| 30..60cm | bd.core | kg/m3 | 1120–1370 | 760–1630 | 905 |
| 30..60cm | soc | g/kg | 6.2–11.3 | 2–39.6 | 905 |
| 30..60cm | ph.h2o | pH | 6.1–6.4 | 4.9–7.5 | 905 |
| 60..100cm | clay | % | 18–27 | 3–44 | 905 |
| 60..100cm | sand | % | 48–63 | 16–88 | 905 |
| 60..100cm | silt | % | 18–27 | 2–47 | 905 |
| 60..100cm | bd.core | kg/m3 | 1180–1460 | 680–1810 | 905 |
| 60..100cm | soc | g/kg | 4.8–9.3 | 1.1–49.2 | 905 |
| 60..100cm | ph.h2o | pH | 6.2–6.5 | 5.1–7.9 | 905 |
