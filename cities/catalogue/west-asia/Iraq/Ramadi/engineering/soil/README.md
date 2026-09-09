# Ramadi civil soil screening

87 route/station sample locations; 81 complete profiles; 6 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 6 |
| fine-soil-plasticity-and-shrink-swell-tests | 30 |
| granular-density-and-groundwater-tests | 75 |
| silt-moisture-frost-and-erosion-review | 29 |

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
| 0..30cm | clay | % | 16–27 | 2–37 | 81 |
| 0..30cm | sand | % | 35–59 | 13–82 | 81 |
| 0..30cm | silt | % | 25–38 | 8–51 | 81 |
| 0..30cm | bd.core | kg/m3 | 1470–1500 | 1280–1700 | 81 |
| 0..30cm | soc | g/kg | 2.5–4.8 | 0.5–10.3 | 81 |
| 0..30cm | ph.h2o | pH | 8.2–8.5 | 7.5–9.6 | 81 |
| 30..60cm | clay | % | 18–27 | 3–40 | 81 |
| 30..60cm | sand | % | 36–57 | 10–91 | 81 |
| 30..60cm | silt | % | 25–37 | 5–56 | 81 |
| 30..60cm | bd.core | kg/m3 | 1420–1480 | 1180–1760 | 81 |
| 30..60cm | soc | g/kg | 2–2.9 | 0–8.3 | 81 |
| 30..60cm | ph.h2o | pH | 8.4–8.9 | 7.6–10.2 | 81 |
| 60..100cm | clay | % | 18–27 | 2–40 | 81 |
| 60..100cm | sand | % | 35–56 | 10–91 | 81 |
| 60..100cm | silt | % | 26–37 | 5–57 | 81 |
| 60..100cm | bd.core | kg/m3 | 1430–1480 | 1230–1800 | 81 |
| 60..100cm | soc | g/kg | 1.8–2.7 | 0.1–7.5 | 81 |
| 60..100cm | ph.h2o | pH | 8.4–8.9 | 7.6–10.2 | 81 |
