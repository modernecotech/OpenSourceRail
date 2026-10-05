# Barisal civil soil screening

893 route/station sample locations; 891 complete profiles; 2 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 891 |
| coverage-gap | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 891 |
| granular-density-and-groundwater-tests | 724 |
| organic-content-and-compressibility-tests | 371 |
| silt-moisture-frost-and-erosion-review | 4 |

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
| 0..30cm | clay | % | 21–31 | 7–46 | 891 |
| 0..30cm | sand | % | 38–55 | 9–88 | 891 |
| 0..30cm | silt | % | 23–32 | 6–50 | 891 |
| 0..30cm | bd.core | kg/m3 | 930–1230 | 670–1590 | 891 |
| 0..30cm | soc | g/kg | 10.4–23.6 | 2.8–66.3 | 891 |
| 0..30cm | ph.h2o | pH | 5.9–6.4 | 4.6–7.9 | 891 |
| 30..60cm | clay | % | 23–33 | 6–46 | 891 |
| 30..60cm | sand | % | 37–55 | 9–86 | 891 |
| 30..60cm | silt | % | 22–31 | 2–48 | 891 |
| 30..60cm | bd.core | kg/m3 | 910–1280 | 640–1600 | 891 |
| 30..60cm | soc | g/kg | 6–18.8 | 1.3–62.4 | 891 |
| 30..60cm | ph.h2o | pH | 6.3–6.7 | 4.8–8 | 891 |
| 60..100cm | clay | % | 24–34 | 7–47 | 891 |
| 60..100cm | sand | % | 36–54 | 9–88 | 891 |
| 60..100cm | silt | % | 22–31 | 2–48 | 891 |
| 60..100cm | bd.core | kg/m3 | 890–1290 | 460–1600 | 891 |
| 60..100cm | soc | g/kg | 5.4–17.2 | 1.3–125.2 | 891 |
| 60..100cm | ph.h2o | pH | 6.5–6.9 | 4.8–8.2 | 891 |
