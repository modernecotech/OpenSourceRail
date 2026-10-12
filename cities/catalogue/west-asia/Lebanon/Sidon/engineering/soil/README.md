# Sidon civil soil screening

1,142 route/station sample locations; 1,142 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 163 |
| fine-soil-plasticity-and-shrink-swell-tests | 1142 |
| granular-density-and-groundwater-tests | 827 |
| silt-moisture-frost-and-erosion-review | 110 |

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
| 0..30cm | clay | % | 19–33 | 4–47 | 1142 |
| 0..30cm | sand | % | 35–62 | 12–86 | 1142 |
| 0..30cm | silt | % | 19–33 | 2–52 | 1142 |
| 0..30cm | bd.core | kg/m3 | 1210–1400 | 930–1600 | 1142 |
| 0..30cm | soc | g/kg | 4.5–15.6 | 1.3–37.2 | 1142 |
| 0..30cm | ph.h2o | pH | 6.4–7.7 | 5.3–8.2 | 1142 |
| 30..60cm | clay | % | 21–36 | 2–49 | 1142 |
| 30..60cm | sand | % | 34–62 | 10–91 | 1142 |
| 30..60cm | silt | % | 17–32 | 0–52 | 1142 |
| 30..60cm | bd.core | kg/m3 | 1310–1520 | 1020–1750 | 1142 |
| 30..60cm | soc | g/kg | 2.4–8.1 | 0.7–25.2 | 1142 |
| 30..60cm | ph.h2o | pH | 6.5–7.6 | 5.2–8.3 | 1142 |
| 60..100cm | clay | % | 21–36 | 3–50 | 1142 |
| 60..100cm | sand | % | 34–62 | 9–92 | 1142 |
| 60..100cm | silt | % | 17–31 | 0–51 | 1142 |
| 60..100cm | bd.core | kg/m3 | 1310–1560 | 940–1780 | 1142 |
| 60..100cm | soc | g/kg | 1.6–7.6 | 0.1–33.6 | 1142 |
| 60..100cm | ph.h2o | pH | 6.5–7.6 | 5.2–8.4 | 1142 |
