# Hillah civil soil screening

583 route/station sample locations; 583 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 486 |
| granular-density-and-groundwater-tests | 375 |
| silt-moisture-frost-and-erosion-review | 108 |

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
| 0..30cm | clay | % | 16–30 | 4–41 | 583 |
| 0..30cm | sand | % | 30–59 | 10–84 | 583 |
| 0..30cm | silt | % | 26–40 | 9–56 | 583 |
| 0..30cm | bd.core | kg/m3 | 1460–1510 | 1270–1710 | 583 |
| 0..30cm | soc | g/kg | 2.4–6.3 | 0.5–13.6 | 583 |
| 0..30cm | ph.h2o | pH | 7.9–8.4 | 7.1–9.5 | 583 |
| 30..60cm | clay | % | 16–30 | 2–42 | 583 |
| 30..60cm | sand | % | 32–59 | 10–90 | 583 |
| 30..60cm | silt | % | 25–38 | 4–54 | 583 |
| 30..60cm | bd.core | kg/m3 | 1440–1610 | 1230–1780 | 583 |
| 30..60cm | soc | g/kg | 1.7–3.4 | 0–8.4 | 583 |
| 30..60cm | ph.h2o | pH | 8.2–8.8 | 7.2–10.1 | 583 |
| 60..100cm | clay | % | 16–30 | 2–40 | 583 |
| 60..100cm | sand | % | 32–59 | 10–90 | 583 |
| 60..100cm | silt | % | 24–39 | 4–54 | 583 |
| 60..100cm | bd.core | kg/m3 | 1440–1670 | 1230–1940 | 583 |
| 60..100cm | soc | g/kg | 1.4–2.7 | 0–8.6 | 583 |
| 60..100cm | ph.h2o | pH | 8.2–8.8 | 7.4–10.1 | 583 |
