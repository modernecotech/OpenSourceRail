# Yangon civil soil screening

981 route/station sample locations; 939 complete profiles; 42 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 939 |
| coverage-gap | 42 |
| fine-soil-plasticity-and-shrink-swell-tests | 939 |
| granular-density-and-groundwater-tests | 921 |
| organic-content-and-compressibility-tests | 6 |
| silt-moisture-frost-and-erosion-review | 40 |

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
| 0..30cm | clay | % | 23–33 | 5–51 | 939 |
| 0..30cm | sand | % | 38–57 | 8–87 | 939 |
| 0..30cm | silt | % | 19–30 | 0–48 | 939 |
| 0..30cm | bd.core | kg/m3 | 850–1290 | 550–1600 | 939 |
| 0..30cm | soc | g/kg | 6.8–20.8 | 2.3–51.4 | 939 |
| 0..30cm | ph.h2o | pH | 5.4–6.6 | 4.4–7.8 | 939 |
| 30..60cm | clay | % | 22–32 | 5–50 | 939 |
| 30..60cm | sand | % | 37–58 | 7–89 | 939 |
| 30..60cm | silt | % | 20–31 | 0–52 | 939 |
| 30..60cm | bd.core | kg/m3 | 940–1360 | 510–1730 | 939 |
| 30..60cm | soc | g/kg | 3.4–15.9 | 0.6–46.1 | 939 |
| 30..60cm | ph.h2o | pH | 5.6–6.9 | 4.7–8.1 | 939 |
| 60..100cm | clay | % | 22–32 | 3–52 | 939 |
| 60..100cm | sand | % | 38–59 | 8–89 | 939 |
| 60..100cm | silt | % | 19–31 | 0–52 | 939 |
| 60..100cm | bd.core | kg/m3 | 960–1400 | 530–1810 | 939 |
| 60..100cm | soc | g/kg | 2.4–12.8 | 0.3–50.7 | 939 |
| 60..100cm | ph.h2o | pH | 5.7–7.1 | 4.6–8.3 | 939 |
