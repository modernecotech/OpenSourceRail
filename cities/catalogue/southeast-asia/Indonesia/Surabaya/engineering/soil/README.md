# Surabaya civil soil screening

2,549 route/station sample locations; 2,274 complete profiles; 275 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 2274 |
| coverage-gap | 275 |
| fine-soil-plasticity-and-shrink-swell-tests | 2274 |
| granular-density-and-groundwater-tests | 2233 |
| organic-content-and-compressibility-tests | 111 |
| silt-moisture-frost-and-erosion-review | 17 |

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
| 0..30cm | clay | % | 19–38 | 3–54 | 2274 |
| 0..30cm | sand | % | 34–67 | 8–94 | 2274 |
| 0..30cm | silt | % | 15–30 | 0–47 | 2274 |
| 0..30cm | bd.core | kg/m3 | 1010–1380 | 590–1660 | 2274 |
| 0..30cm | soc | g/kg | 4.7–24.4 | 1.2–87.6 | 2274 |
| 0..30cm | ph.h2o | pH | 5.6–6.4 | 4.4–7.6 | 2274 |
| 30..60cm | clay | % | 20–40 | 3–57 | 2274 |
| 30..60cm | sand | % | 35–67 | 4–93 | 2274 |
| 30..60cm | silt | % | 14–28 | 0–50 | 2274 |
| 30..60cm | bd.core | kg/m3 | 1000–1480 | 510–1760 | 2274 |
| 30..60cm | soc | g/kg | 3–19.6 | 0.9–60.3 | 2274 |
| 30..60cm | ph.h2o | pH | 5.6–6.3 | 4.5–7.7 | 2274 |
| 60..100cm | clay | % | 21–41 | 3–61 | 2274 |
| 60..100cm | sand | % | 35–65 | 5–93 | 2274 |
| 60..100cm | silt | % | 13–28 | 0–51 | 2274 |
| 60..100cm | bd.core | kg/m3 | 950–1510 | 380–1770 | 2274 |
| 60..100cm | soc | g/kg | 2.6–26.3 | 0.3–118.4 | 2274 |
| 60..100cm | ph.h2o | pH | 5.6–6.4 | 4.6–7.9 | 2274 |
