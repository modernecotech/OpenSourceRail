# Gazipur civil soil screening

1,746 route/station sample locations; 1,745 complete profiles; 1 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1745 |
| coverage-gap | 1 |
| fine-soil-plasticity-and-shrink-swell-tests | 1745 |
| granular-density-and-groundwater-tests | 1683 |
| organic-content-and-compressibility-tests | 674 |
| silt-moisture-frost-and-erosion-review | 3 |

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
| 0..30cm | clay | % | 21–30 | 7–47 | 1745 |
| 0..30cm | sand | % | 41–59 | 9–87 | 1745 |
| 0..30cm | silt | % | 20–30 | 0–50 | 1745 |
| 0..30cm | bd.core | kg/m3 | 820–1320 | 500–1600 | 1745 |
| 0..30cm | soc | g/kg | 11.1–30.2 | 3.9–84.8 | 1745 |
| 0..30cm | ph.h2o | pH | 5.6–6.2 | 4.3–7.5 | 1745 |
| 30..60cm | clay | % | 22–31 | 5–49 | 1745 |
| 30..60cm | sand | % | 40–60 | 7–87 | 1745 |
| 30..60cm | silt | % | 17–31 | 0–49 | 1745 |
| 30..60cm | bd.core | kg/m3 | 900–1360 | 570–1600 | 1745 |
| 30..60cm | soc | g/kg | 5–23.5 | 1.2–82.5 | 1745 |
| 30..60cm | ph.h2o | pH | 5.8–6.4 | 4.6–7.9 | 1745 |
| 60..100cm | clay | % | 23–32 | 5–49 | 1745 |
| 60..100cm | sand | % | 39–57 | 8–88 | 1745 |
| 60..100cm | silt | % | 18–31 | 0–49 | 1745 |
| 60..100cm | bd.core | kg/m3 | 910–1360 | 460–1610 | 1745 |
| 60..100cm | soc | g/kg | 3.7–16.8 | 1.1–67.5 | 1745 |
| 60..100cm | ph.h2o | pH | 6–6.7 | 4.6–8.2 | 1745 |
