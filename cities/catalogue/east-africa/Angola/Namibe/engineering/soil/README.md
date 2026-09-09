# Namibe civil soil screening

121 route/station sample locations; 72 complete profiles; 49 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 49 |
| fine-soil-plasticity-and-shrink-swell-tests | 8 |
| granular-density-and-groundwater-tests | 72 |

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
| 0..30cm | clay | % | 11–20 | 0–34 | 72 |
| 0..30cm | sand | % | 57–75 | 31–91 | 72 |
| 0..30cm | silt | % | 14–24 | 3–34 | 72 |
| 0..30cm | bd.core | kg/m3 | 1430–1530 | 1180–1790 | 72 |
| 0..30cm | soc | g/kg | 1.8–6.2 | 0.8–12 | 72 |
| 0..30cm | ph.h2o | pH | 8–8.4 | 7.2–9.1 | 72 |
| 30..60cm | clay | % | 13–20 | 0–36 | 72 |
| 30..60cm | sand | % | 58–71 | 29–94 | 72 |
| 30..60cm | silt | % | 14–22 | 1–38 | 72 |
| 30..60cm | bd.core | kg/m3 | 1480–1540 | 1200–1820 | 72 |
| 30..60cm | soc | g/kg | 1.2–4.2 | 0.3–10 | 72 |
| 30..60cm | ph.h2o | pH | 8.2–8.4 | 7.3–9.3 | 72 |
| 60..100cm | clay | % | 14–20 | 0–35 | 72 |
| 60..100cm | sand | % | 59–70 | 30–93 | 72 |
| 60..100cm | silt | % | 14–22 | 0–39 | 72 |
| 60..100cm | bd.core | kg/m3 | 1400–1540 | 1090–1880 | 72 |
| 60..100cm | soc | g/kg | 1–4.5 | 0.2–16.3 | 72 |
| 60..100cm | ph.h2o | pH | 8.3–8.6 | 7.5–9.5 | 72 |
