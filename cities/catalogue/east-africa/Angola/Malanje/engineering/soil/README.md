# Malanje civil soil screening

30 route/station sample locations; 30 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 30 |
| fine-soil-plasticity-and-shrink-swell-tests | 30 |
| granular-density-and-groundwater-tests | 26 |

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
| 0..30cm | clay | % | 29–33 | 10–45 | 30 |
| 0..30cm | sand | % | 43–53 | 19–78 | 30 |
| 0..30cm | silt | % | 18–24 | 4–40 | 30 |
| 0..30cm | bd.core | kg/m3 | 1250–1370 | 1050–1580 | 30 |
| 0..30cm | soc | g/kg | 8.5–14.9 | 3.8–29.2 | 30 |
| 0..30cm | ph.h2o | pH | 5.5–5.9 | 4.5–7.3 | 30 |
| 30..60cm | clay | % | 31–36 | 10–49 | 30 |
| 30..60cm | sand | % | 38–47 | 10–76 | 30 |
| 30..60cm | silt | % | 21–27 | 5–45 | 30 |
| 30..60cm | bd.core | kg/m3 | 1250–1440 | 1030–1730 | 30 |
| 30..60cm | soc | g/kg | 5–7 | 1.9–14.3 | 30 |
| 30..60cm | ph.h2o | pH | 5.6–6 | 4.8–7 | 30 |
| 60..100cm | clay | % | 31–35 | 9–51 | 30 |
| 60..100cm | sand | % | 38–46 | 9–79 | 30 |
| 60..100cm | silt | % | 22–28 | 5–47 | 30 |
| 60..100cm | bd.core | kg/m3 | 1210–1450 | 980–1750 | 30 |
| 60..100cm | soc | g/kg | 3.9–5.4 | 1.7–11.2 | 30 |
| 60..100cm | ph.h2o | pH | 6–6.2 | 4.5–8 | 30 |
