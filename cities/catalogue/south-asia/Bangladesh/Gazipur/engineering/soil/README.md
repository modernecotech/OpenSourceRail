# Gazipur civil soil screening

649 route/station sample locations; 644 complete profiles; 5 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 644 |
| coverage-gap | 5 |
| fine-soil-plasticity-and-shrink-swell-tests | 644 |
| granular-density-and-groundwater-tests | 625 |
| organic-content-and-compressibility-tests | 304 |
| silt-moisture-frost-and-erosion-review | 2 |

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
| 0..30cm | clay | % | 22–29 | 6–46 | 644 |
| 0..30cm | sand | % | 41–58 | 10–87 | 644 |
| 0..30cm | silt | % | 19–31 | 1–50 | 644 |
| 0..30cm | bd.core | kg/m3 | 810–1310 | 430–1560 | 644 |
| 0..30cm | soc | g/kg | 11.1–28.8 | 3.9–83.3 | 644 |
| 0..30cm | ph.h2o | pH | 5.6–6.2 | 4.1–7.5 | 644 |
| 30..60cm | clay | % | 22–31 | 6–49 | 644 |
| 30..60cm | sand | % | 39–58 | 7–87 | 644 |
| 30..60cm | silt | % | 17–32 | 0–49 | 644 |
| 30..60cm | bd.core | kg/m3 | 900–1330 | 500–1600 | 644 |
| 30..60cm | soc | g/kg | 5.1–22.6 | 1.2–74.2 | 644 |
| 30..60cm | ph.h2o | pH | 5.8–6.5 | 4.6–7.9 | 644 |
| 60..100cm | clay | % | 23–32 | 6–50 | 644 |
| 60..100cm | sand | % | 38–57 | 8–88 | 644 |
| 60..100cm | silt | % | 17–31 | 0–49 | 644 |
| 60..100cm | bd.core | kg/m3 | 910–1330 | 460–1600 | 644 |
| 60..100cm | soc | g/kg | 3.6–16 | 1.1–57.8 | 644 |
| 60..100cm | ph.h2o | pH | 6–6.7 | 4.6–8.2 | 644 |
