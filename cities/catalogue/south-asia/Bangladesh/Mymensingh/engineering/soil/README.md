# Mymensingh civil soil screening

651 route/station sample locations; 649 complete profiles; 2 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 649 |
| coverage-gap | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 649 |
| granular-density-and-groundwater-tests | 527 |
| organic-content-and-compressibility-tests | 453 |
| silt-moisture-frost-and-erosion-review | 33 |

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
| 0..30cm | clay | % | 23–31 | 6–47 | 649 |
| 0..30cm | sand | % | 38–53 | 9–83 | 649 |
| 0..30cm | silt | % | 24–32 | 0–49 | 649 |
| 0..30cm | bd.core | kg/m3 | 830–1080 | 440–1370 | 649 |
| 0..30cm | soc | g/kg | 11.8–23 | 4.2–69 | 649 |
| 0..30cm | ph.h2o | pH | 5.4–5.9 | 4.4–7.4 | 649 |
| 30..60cm | clay | % | 23–31 | 6–46 | 649 |
| 30..60cm | sand | % | 37–53 | 11–82 | 649 |
| 30..60cm | silt | % | 23–32 | 0–50 | 649 |
| 30..60cm | bd.core | kg/m3 | 870–1140 | 520–1470 | 649 |
| 30..60cm | soc | g/kg | 5.5–20 | 1.4–65.7 | 649 |
| 30..60cm | ph.h2o | pH | 5.5–6.2 | 4.4–7.7 | 649 |
| 60..100cm | clay | % | 24–32 | 6–44 | 649 |
| 60..100cm | sand | % | 36–50 | 7–82 | 649 |
| 60..100cm | silt | % | 24–32 | 0–52 | 649 |
| 60..100cm | bd.core | kg/m3 | 950–1120 | 530–1480 | 649 |
| 60..100cm | soc | g/kg | 4.7–17.2 | 1.4–193 | 649 |
| 60..100cm | ph.h2o | pH | 5.6–6.3 | 4.4–7.9 | 649 |
