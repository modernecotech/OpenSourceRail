# Malanje civil soil screening

223 route/station sample locations; 223 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 223 |
| fine-soil-plasticity-and-shrink-swell-tests | 223 |
| granular-density-and-groundwater-tests | 213 |

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
| 0..30cm | clay | % | 27–34 | 9–47 | 223 |
| 0..30cm | sand | % | 42–54 | 18–83 | 223 |
| 0..30cm | silt | % | 18–25 | 3–40 | 223 |
| 0..30cm | bd.core | kg/m3 | 1250–1380 | 1050–1580 | 223 |
| 0..30cm | soc | g/kg | 7.4–14.7 | 3.5–29.2 | 223 |
| 0..30cm | ph.h2o | pH | 5.4–5.9 | 4.5–7.3 | 223 |
| 30..60cm | clay | % | 29–37 | 9–51 | 223 |
| 30..60cm | sand | % | 35–49 | 8–83 | 223 |
| 30..60cm | silt | % | 20–28 | 5–47 | 223 |
| 30..60cm | bd.core | kg/m3 | 1250–1440 | 1030–1730 | 223 |
| 30..60cm | soc | g/kg | 4.3–7.2 | 1.9–14.8 | 223 |
| 30..60cm | ph.h2o | pH | 5.5–6.1 | 4.6–7.1 | 223 |
| 60..100cm | clay | % | 29–37 | 8–52 | 223 |
| 60..100cm | sand | % | 35–48 | 7–81 | 223 |
| 60..100cm | silt | % | 20–28 | 4–47 | 223 |
| 60..100cm | bd.core | kg/m3 | 1210–1450 | 920–1750 | 223 |
| 60..100cm | soc | g/kg | 3.8–5.9 | 1.5–11.2 | 223 |
| 60..100cm | ph.h2o | pH | 5.9–6.3 | 4.4–8 | 223 |
