# Khulna civil soil screening

2,230 route/station sample locations; 2,217 complete profiles; 13 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 2216 |
| coverage-gap | 13 |
| fine-soil-plasticity-and-shrink-swell-tests | 2217 |
| granular-density-and-groundwater-tests | 2217 |
| organic-content-and-compressibility-tests | 897 |
| silt-moisture-frost-and-erosion-review | 10 |

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
| 0..30cm | clay | % | 19–29 | 4–46 | 2217 |
| 0..30cm | sand | % | 42–63 | 8–89 | 2217 |
| 0..30cm | silt | % | 18–30 | 2–50 | 2217 |
| 0..30cm | bd.core | kg/m3 | 780–1180 | 400–1540 | 2217 |
| 0..30cm | soc | g/kg | 8.4–43.8 | 3–181.6 | 2217 |
| 0..30cm | ph.h2o | pH | 5.9–6.6 | 4.7–7.9 | 2217 |
| 30..60cm | clay | % | 20–30 | 2–47 | 2217 |
| 30..60cm | sand | % | 41–62 | 6–90 | 2217 |
| 30..60cm | silt | % | 18–31 | 2–49 | 2217 |
| 30..60cm | bd.core | kg/m3 | 850–1210 | 530–1560 | 2217 |
| 30..60cm | soc | g/kg | 5.8–28.3 | 1.2–106.5 | 2217 |
| 30..60cm | ph.h2o | pH | 6.2–6.9 | 4.9–8 | 2217 |
| 60..100cm | clay | % | 21–30 | 2–48 | 2217 |
| 60..100cm | sand | % | 40–59 | 5–91 | 2217 |
| 60..100cm | silt | % | 19–31 | 2–49 | 2217 |
| 60..100cm | bd.core | kg/m3 | 920–1210 | 530–1730 | 2217 |
| 60..100cm | soc | g/kg | 4.8–18 | 1.2–83.3 | 2217 |
| 60..100cm | ph.h2o | pH | 6.2–7.1 | 4.9–8.2 | 2217 |
