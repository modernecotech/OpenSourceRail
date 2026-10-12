# Aden civil soil screening

778 route/station sample locations; 373 complete profiles; 405 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 405 |
| fine-soil-plasticity-and-shrink-swell-tests | 22 |
| granular-density-and-groundwater-tests | 373 |

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
| 0..30cm | clay | % | 11–17 | 0–32 | 373 |
| 0..30cm | sand | % | 61–72 | 28–96 | 373 |
| 0..30cm | silt | % | 16–22 | 2–42 | 373 |
| 0..30cm | bd.core | kg/m3 | 1370–1500 | 1020–1720 | 373 |
| 0..30cm | soc | g/kg | 2.3–7.2 | 0.5–22.1 | 373 |
| 0..30cm | ph.h2o | pH | 8.3–8.8 | 7.6–9.6 | 373 |
| 30..60cm | clay | % | 11–20 | 0–34 | 373 |
| 30..60cm | sand | % | 57–72 | 24–97 | 373 |
| 30..60cm | silt | % | 16–23 | 0–41 | 373 |
| 30..60cm | bd.core | kg/m3 | 1400–1550 | 1060–1730 | 373 |
| 30..60cm | soc | g/kg | 1.4–8.1 | 0–48.4 | 373 |
| 30..60cm | ph.h2o | pH | 8.3–8.8 | 7.4–9.5 | 373 |
| 60..100cm | clay | % | 12–21 | 0–35 | 373 |
| 60..100cm | sand | % | 56–72 | 26–96 | 373 |
| 60..100cm | silt | % | 16–24 | 0–43 | 373 |
| 60..100cm | bd.core | kg/m3 | 1300–1560 | 790–1790 | 373 |
| 60..100cm | soc | g/kg | 1.3–6 | 0–38.8 | 373 |
| 60..100cm | ph.h2o | pH | 8.3–9 | 7.5–9.5 | 373 |
