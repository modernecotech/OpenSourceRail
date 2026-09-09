# Sayun civil soil screening

49 route/station sample locations; 41 complete profiles; 8 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 8 |
| fine-soil-plasticity-and-shrink-swell-tests | 7 |
| granular-density-and-groundwater-tests | 41 |

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
| 0..30cm | clay | % | 14–20 | 3–35 | 41 |
| 0..30cm | sand | % | 56–68 | 29–90 | 41 |
| 0..30cm | silt | % | 17–24 | 5–37 | 41 |
| 0..30cm | bd.core | kg/m3 | 1450–1530 | 1280–1710 | 41 |
| 0..30cm | soc | g/kg | 1.7–3.4 | 0.4–7.5 | 41 |
| 0..30cm | ph.h2o | pH | 7.9–8.5 | 6.6–9.3 | 41 |
| 30..60cm | clay | % | 16–21 | 2–35 | 41 |
| 30..60cm | sand | % | 56–67 | 30–93 | 41 |
| 30..60cm | silt | % | 17–23 | 3–37 | 41 |
| 30..60cm | bd.core | kg/m3 | 1480–1530 | 1300–1690 | 41 |
| 30..60cm | soc | g/kg | 1.2–2.1 | 0.2–4.8 | 41 |
| 30..60cm | ph.h2o | pH | 7.8–8.9 | 6.1–9.8 | 41 |
| 60..100cm | clay | % | 15–21 | 2–38 | 41 |
| 60..100cm | sand | % | 56–67 | 20–93 | 41 |
| 60..100cm | silt | % | 18–23 | 4–37 | 41 |
| 60..100cm | bd.core | kg/m3 | 1500–1570 | 1280–1730 | 41 |
| 60..100cm | soc | g/kg | 1–1.8 | 0.2–4.6 | 41 |
| 60..100cm | ph.h2o | pH | 7.8–8.9 | 6.2–9.8 | 41 |
