# Sayun civil soil screening

203 route/station sample locations; 144 complete profiles; 59 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 59 |
| fine-soil-plasticity-and-shrink-swell-tests | 39 |
| granular-density-and-groundwater-tests | 144 |

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
| 0..30cm | clay | % | 13–22 | 3–37 | 144 |
| 0..30cm | sand | % | 52–69 | 26–90 | 144 |
| 0..30cm | silt | % | 17–26 | 5–40 | 144 |
| 0..30cm | bd.core | kg/m3 | 1420–1540 | 1150–1700 | 144 |
| 0..30cm | soc | g/kg | 1.6–4.5 | 0.4–9.1 | 144 |
| 0..30cm | ph.h2o | pH | 7.9–8.5 | 6.7–9.4 | 144 |
| 30..60cm | clay | % | 14–22 | 2–37 | 144 |
| 30..60cm | sand | % | 53–69 | 24–93 | 144 |
| 30..60cm | silt | % | 17–24 | 3–38 | 144 |
| 30..60cm | bd.core | kg/m3 | 1470–1540 | 1260–1730 | 144 |
| 30..60cm | soc | g/kg | 1.2–3 | 0.2–6.1 | 144 |
| 30..60cm | ph.h2o | pH | 7.9–8.8 | 6.1–9.8 | 144 |
| 60..100cm | clay | % | 14–22 | 2–38 | 144 |
| 60..100cm | sand | % | 54–68 | 23–93 | 144 |
| 60..100cm | silt | % | 18–24 | 3–39 | 144 |
| 60..100cm | bd.core | kg/m3 | 1490–1580 | 1250–1790 | 144 |
| 60..100cm | soc | g/kg | 1–2.4 | 0–5.1 | 144 |
| 60..100cm | ph.h2o | pH | 7.9–8.8 | 6.2–9.8 | 144 |
