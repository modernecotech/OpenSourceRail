# Barisal civil soil screening

2,661 route/station sample locations; 2,658 complete profiles; 3 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 2658 |
| coverage-gap | 3 |
| fine-soil-plasticity-and-shrink-swell-tests | 2658 |
| granular-density-and-groundwater-tests | 2031 |
| organic-content-and-compressibility-tests | 1131 |
| silt-moisture-frost-and-erosion-review | 11 |

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
| 0..30cm | clay | % | 22–32 | 7–46 | 2658 |
| 0..30cm | sand | % | 38–55 | 9–85 | 2658 |
| 0..30cm | silt | % | 22–32 | 6–50 | 2658 |
| 0..30cm | bd.core | kg/m3 | 920–1080 | 640–1460 | 2658 |
| 0..30cm | soc | g/kg | 9.3–24.1 | 2.3–66.3 | 2658 |
| 0..30cm | ph.h2o | pH | 5.9–6.5 | 4.6–8 | 2658 |
| 30..60cm | clay | % | 23–33 | 8–47 | 2658 |
| 30..60cm | sand | % | 36–54 | 9–87 | 2658 |
| 30..60cm | silt | % | 23–31 | 2–48 | 2658 |
| 30..60cm | bd.core | kg/m3 | 910–1130 | 600–1490 | 2658 |
| 30..60cm | soc | g/kg | 6.7–18.8 | 1–63.1 | 2658 |
| 30..60cm | ph.h2o | pH | 6.2–6.8 | 4.9–8 | 2658 |
| 60..100cm | clay | % | 25–34 | 8–47 | 2658 |
| 60..100cm | sand | % | 36–52 | 7–87 | 2658 |
| 60..100cm | silt | % | 23–31 | 2–50 | 2658 |
| 60..100cm | bd.core | kg/m3 | 880–1150 | 460–1550 | 2658 |
| 60..100cm | soc | g/kg | 5.7–17.2 | 1.2–94 | 2658 |
| 60..100cm | ph.h2o | pH | 6.5–7 | 4.8–8.2 | 2658 |
