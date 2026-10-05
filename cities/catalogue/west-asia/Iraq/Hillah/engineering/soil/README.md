# Hillah civil soil screening

245 route/station sample locations; 245 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 180 |
| granular-density-and-groundwater-tests | 207 |
| silt-moisture-frost-and-erosion-review | 18 |

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
| 0..30cm | clay | % | 16–30 | 4–41 | 245 |
| 0..30cm | sand | % | 31–59 | 11–81 | 245 |
| 0..30cm | silt | % | 26–40 | 11–53 | 245 |
| 0..30cm | bd.core | kg/m3 | 1460–1510 | 1270–1710 | 245 |
| 0..30cm | soc | g/kg | 2.6–6.2 | 0.7–13.5 | 245 |
| 0..30cm | ph.h2o | pH | 8–8.4 | 7.2–9.5 | 245 |
| 30..60cm | clay | % | 16–30 | 2–42 | 245 |
| 30..60cm | sand | % | 32–59 | 11–90 | 245 |
| 30..60cm | silt | % | 25–38 | 4–54 | 245 |
| 30..60cm | bd.core | kg/m3 | 1440–1570 | 1230–1770 | 245 |
| 30..60cm | soc | g/kg | 1.7–3.2 | 0–8.4 | 245 |
| 30..60cm | ph.h2o | pH | 8.2–8.8 | 7.4–10.1 | 245 |
| 60..100cm | clay | % | 16–29 | 2–40 | 245 |
| 60..100cm | sand | % | 32–59 | 11–90 | 245 |
| 60..100cm | silt | % | 24–38 | 4–53 | 245 |
| 60..100cm | bd.core | kg/m3 | 1450–1620 | 1230–1910 | 245 |
| 60..100cm | soc | g/kg | 1.5–2.7 | 0.1–8.6 | 245 |
| 60..100cm | ph.h2o | pH | 8.2–8.8 | 7.5–10.1 | 245 |
